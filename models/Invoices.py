from main import db
from models.Invoice_products import InvoiceProductsModel


class InvoicesModel(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.Integer())
    date = db.Column(db.String())
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))

    # pseudo column
    invoice_products = db.relationship(InvoiceProductsModel, backref='invoice')

    # insert into db
    def insert_records(self):
        db.session.add(self)
        db.session.commit()

    # fetch by id
    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    # fetch all invoices
    @classmethod
    def fetch_all(cls):
        return cls.query.all()