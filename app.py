from flask import Flask, jsonify, request
from repository.database import db
from models.payment import Payment
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')

db.init_app(app)


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
    db.session.add(new_payment)
    db.session.commit()
    return jsonify(
        {"message": "The payment has been created",
         "payment": new_payment.to_dict()})


# Webhook --> ver mais sobre o conceito
@app.route('/payments/pix/confirmation', methods=['POST'])
def pix_confirmation():
    return jsonify({"message": "The payment has been confirmed"})


@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    return 'Pagamento pix'


if __name__ == '__main__':
    app.run(debug=True)
