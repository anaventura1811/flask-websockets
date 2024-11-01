from flask import Flask, jsonify, request, send_file, render_template
from repository.database import db
from models.payment import Payment
from payments.pix import Pix
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_socketio import SocketIO
import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')

HOST = os.getenv('HOST')

db.init_app(app)
socketio = SocketIO(app)


@app.route('/payments/pix', methods=['POST'])
def create_payment_pix():
    data = request.get_json()
    # Validações
    if 'value' not in data:
        return jsonify({"message": "Invalid value"}), 400
    expiration_date = datetime.now() + timedelta(minutes=30)

    new_payment = Payment(
        value=data.get("value"),
        expiration_date=expiration_date)
    pix_obj = Pix()
    data_payment_pix = pix_obj.create_payment()
    new_payment.bank_payment_id = str(data_payment_pix['bank_payment_id'])
    new_payment.qr_code = data_payment_pix['qr_code_path']
    db.session.add(new_payment)
    db.session.commit()
    return jsonify(
        {"message": "The payment has been created",
         "payment": new_payment.to_dict()})


@app.route('/payments/pix/qr_code/<file_name>', methods=['GET'])
def get_image(file_name):
    return send_file(
        path_or_file=f"static/img/{file_name}.png",
        mimetype='image/png')


# Webhook
@app.route('/payments/pix/confirmation', methods=['POST'])
def pix_confirmation():
    data = request.get_json()
    if 'bank_payment_id' not in data:
        return jsonify({"message": "Invalid payment data"}), 400

    if 'value' not in data:
        return jsonify({"message": "Invalid payment data"}), 400

    payment = Payment.query.filter_by(
        bank_payment_id=data.get('bank_payment_id')
        ).first()
    if not payment or payment.paid:
        return jsonify({"message": "Payment not found"}), 404

    if data.get('value') != payment.value:
        return jsonify({"message": "Invalid payment data"}), 400

    payment.paid = True
    db.session.commit()
    socketio.emit(f'payment-confirmed-{payment.id}')
    return jsonify({"message": "The payment has been confirmed"})


@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return render_template('not_found.html')
    
    if payment.paid:
        return render_template('payment_confirmed.html',
                               payment_id=payment.id,
                               value=payment.value,
                               host=HOST,
                               qr_code=payment.qr_code)

    return render_template('payment_created.html',
                           payment_id=payment.id,
                           value=payment.value,
                           host=HOST,
                           qr_code=payment.qr_code)


# websockets
@socketio.on('connect')
def connect():
    print('client is connected')


if __name__ == '__main__':
    socketio.run(app, debug=True)
