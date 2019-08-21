from app import db


class PaymentsModel(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.Integer)
    transaction_type = db.Column(db.String())
    transaction_id = db.Column(db.String(10))
    cheque_no = db.Column(db.String())
    bank_name = db.Column(db.String())
    amount = db.Column(db.Integer)
    balance = db.Column(db.Integer)
    date = db.Column(db.String())

    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))

    # insert records
    def insert_records(self):
        db.session.add(self)
        db.session.commit()
        return self

    # fetch by client id
    @classmethod
    def fetch_by_client_id(cls, client_id):
        return cls.query.filter_by(client_id=client_id).first()

    # fetch by id
    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    # check invoice number
    @classmethod
    def check_invoice_no(cls, invoice_no):
        record = cls.query.filter_by(invoice_no=invoice_no).first()
        return record