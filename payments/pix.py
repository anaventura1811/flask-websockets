import uuid
import qrcode


class Pix:
    def __init__(self) -> None:
        pass

    def create_payment(self, base_dir=""):
        # criar o pagamento na instituição financeira
        bank_payment_id = uuid.uuid4()

        # qr code ==>
        hash_payment = f'hash_payment_{bank_payment_id}'

        qr_code_img = qrcode.make(hash_payment)

        # Salvar a imagem como arquivo png
        qr_code_img.save(
            f"{base_dir}static/img/qr_code_payment_{bank_payment_id}.png")

        return {
            "bank_payment_id": bank_payment_id,
            "qr_code_path": f"qr_code_payment_{bank_payment_id}",
        }
