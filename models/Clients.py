from app import db
from models.Invoices import InvoicesModel
from models.Payments import PaymentsModel


class ClientsModel(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String())
    branch = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    phone_number = db.Column(db.String())

    # pseudo column
    invoices = db.relationship(InvoicesModel, backref='client')
    payments = db.relationship(PaymentsModel, backref='client')

    # insert records in db
    def insert_records(self):
        db.session.add(self)
        db.session.commit()
        return self

    # read clients from the db
    @classmethod
    def fetch_all_clients(cls):
        return cls.query.all()

    # read by id
    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    # check email
    @classmethod
    def check_email(cls, email):
        record = cls.query.filter_by(email=email).first()
        return record

    # check branch
    @classmethod
    def check_branch(cls, branch):
        record = cls.query.filter_by(branch=branch).first()
        return record

    # update clients information
    @classmethod
    def update_client_by_id(cls, id, client_name=None, branch=None, email=None, phone_number=None):
        record = cls.query.filter_by(id=id).first()
        if client_name:
            record.client_name = client_name
        if branch:
            record.branch = branch
        if email:
            record.email = email
        if phone_number:
            record.phone_number = phone_number

        db.session.commit()
        return True
