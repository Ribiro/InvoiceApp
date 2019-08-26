from main import db


class ProductsModel(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(), nullable=False)
    price = db.Column(db.String())

    # insert records in db
    def insert_records(self):
        db.session.add(self)
        db.session.commit()
        return self

    # read clients from the db
    @classmethod
    def fetch_all_products(cls):
        return cls.query.all()

    # check email
    @classmethod
    def check_product_name(cls, product_name):
        record = cls.query.filter_by(product_name=product_name).first()
        return record

    # update products
    @classmethod
    def update_product_by_id(cls, id, product_name=None, price=None):
        record = cls.query.filter_by(id=id).first()
        if product_name:
            record.product_name = product_name
        if price:
            record.price = price

        db.session.commit()
        return True
