from app import db


class InvoiceProductsModel(db.Model):
    __tablename__ = 'invoice_products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String())
    quantity = db.Column(db.Integer())
    price = db.Column(db.String())
    total = db.Column(db.String())

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))

    # insert into database
    def insert_records(self):
        db.session.add(self)
        db.session.commit()
        return self

    # fetch by invoice id
    @classmethod
    def fetch_by_invoice_id(cls, invoice_id):
        return cls.query.filter_by(invoice_id=invoice_id).all()

    # fetch by id
    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.filter_by(id=id).first()