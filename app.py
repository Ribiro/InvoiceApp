from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from config import Development, Production
from datetime import datetime
# create an instance of class Flask called app
app = Flask(__name__)
app.config.from_object(Development)
# app.config.from_object(Production)

# create an instance of SQLAlchemy
db = SQLAlchemy(app)

from models.Products import ProductsModel
from models.Clients import ClientsModel
from models.Invoices import InvoicesModel
from models.Invoice_products import InvoiceProductsModel
from models.Payments import PaymentsModel

# create tables in our database
@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def hello_world():
    return render_template('home.html')

# add client
@app.route('/new_client', methods=['POST'])
def new_client():
    if request.method == 'POST':
        client_name = request.form['client_name']
        branch = request.form['branch']
        phone_number = request.form['phone_number']
        email = request.form['email']

        if ClientsModel.check_email(email):
            flash('Email already in use!')
            return redirect(url_for('clients_information'))
        new = ClientsModel(client_name=client_name, branch=branch, email=email, phone_number=phone_number)
        new.insert_records()
    return redirect(url_for('clients_information'))

# clients info route
@app.route('/clients_information')
def clients_information():
    clients = ClientsModel.fetch_all_clients()
    return render_template('clients.html', clients=clients)

# update clients information
@app.route('/editclient/<int:id>', methods=['POST'])
def edit_client(id):
    if request.method == 'POST':
        client_name = request.form['client_name']
        branch = request.form['branch']
        phone_number = request.form['phone_number']
        email = request.form['email']

        ClientsModel.update_client_by_id(id=id, client_name=client_name, branch=branch, email=email,
                                         phone_number=phone_number)
    return redirect(url_for('clients_information'))

# add new product
@app.route('/new_product', methods=['POST'])
def new_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        unit_price = request.form['price']

        if ProductsModel.check_product_name(product_name):
            flash('Product Already Exists')
            return redirect(url_for('products'))
        new = ProductsModel(product_name=product_name, price=unit_price)
        new.insert_records()
    return redirect(url_for('products'))

# products route
@app.route('/products')
def products():
    products = ProductsModel.fetch_all_products()
    return render_template('products.html', products=products)

# update products
@app.route('/editproduct/<int:id>', methods=['POST'])
def edit_product(id):
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = request.form['price']

        ProductsModel.update_product_by_id(id=id, product_name=product_name, price=price)
    return redirect(url_for('products'))

# create invoice route // this is for viewing invoice route fo a particular client
@app.route('/create_invoice/<int:id>')
def create_invoice(id):
    client = ClientsModel.fetch_by_id(id)
    return render_template('create_invoice.html', client=client)

# generate invoice // this is now inside the create invoice route
@app.route('/generate_invoice/<int:id>', methods=['POST'])
def generate_invoice(id):
    # generate invoice number
    invoice = InvoicesModel.fetch_all()

    last = invoice[-1]
    last_invoice_no = last.invoice_no
    invoice_no = last_invoice_no + 1

    d = datetime.now()

    month = d.month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', ' October',
              'November', 'December']
    month = months[month - 1]

    day = d.day
    year = d.year

    date = str(day) + ' ' + month + ' ' + str(year)
    date = str(date)
    print(date)
    new = InvoicesModel(invoice_no=invoice_no, date=date, client_id=id)
    new.insert_records()
    return redirect(url_for('create_invoice', id=id))

# invoice products route
@app.route('/invoice_products/<int:id>')
def invoice_products(id):
    products = ProductsModel.fetch_all_products()
    invoice = InvoicesModel.fetch_by_id(id)
    return render_template('invoice_products.html', products=products, hii_invoice=invoice)

# new invoice product
@app.route('/new_invoice_product/<int:id>', methods=['POST'])
def new_invoice_product(id):
    product_name = request.form['product_name']
    quantity = request.form['quantity']

    product = ProductsModel.check_product_name(product_name)
    price = product.price

    total = int(price) * int(quantity)

    print("product name:", product_name)
    print('quantity', quantity)
    print('price ', price)
    print('total ', total)

    new = InvoiceProductsModel(product_name=product_name, quantity=quantity, price=price, total=total, invoice_id=id)
    new.insert_records()

    return redirect(url_for('invoice_products', id=id))

# list invoice route
@app.route('/list_invoices')
def list_invoices():
    return render_template('invoice_list.html')

# generate statement
@app.route('/generate_statement/<int:id>', methods=['POST'])
def generate_statement(id):
    invoice = InvoicesModel.fetch_by_id(id)
    date = invoice.date
    invoice_no = invoice.invoice_no
    print(date)
    print(invoice_no)

    invoice_particulars = InvoiceProductsModel.fetch_by_invoice_id(id)

    sum = 0
    for each in invoice_particulars:
        sum += int(each.total)
    print("Total Cost of Products is: ", sum)

    if sum != 0:
        transaction_type = "BILLING"
        balance = -sum

        client_id = invoice.client_id
        print("This is client id: ", client_id)

        if PaymentsModel.check_invoice_no(invoice_no):
            flash("Invoice Already Exists!!")
            return redirect(url_for('invoice_products', id=id))
        new = PaymentsModel(invoice_no=invoice_no, transaction_type=transaction_type, amount=sum, balance=balance, date=date, client_id=client_id)
        new.insert_records()
        flash("Invoice submitted successfully!")
        return redirect(url_for('invoice_products', id=id))
    else:
        flash("Nothing to submit, please select products")
        return redirect(url_for('invoice_products', id=id))

# statements route
@app.route('/statements/<int:id>')
def statements(id):
    client = ClientsModel.fetch_by_id(id)
    return render_template('statements.html', client=client)

# make payments for each client
@app.route('/cashpayments/<int:id>', methods=['POST'])
def make_payment(id):
    d = datetime.now()

    month = d.month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', ' October',
              'November', 'December']
    month = months[month - 1]

    day = d.day
    year = d.year

    date = str(day) + ' ' + month + ' ' + str(year)
    date = str(date)
    print(date)

    try:
        client = PaymentsModel.fetch_by_id(id)
        statement_amount = client.payments[-1]

        prev_balance = statement_amount.balance
        prev_balance = int(prev_balance)

        print(prev_balance)
    except:
        prev_balance = 0
        print("No charges")
        # return redirect(url_for('payments', id=mid))

    if request.form['amount_paid']:
        amount_paid = request.form['amount_paid']
        transaction_type = "PAYMENT"
        balance = int(amount_paid) + prev_balance
        new_payment = PaymentsModel(transaction_type=transaction_type, amount=amount_paid, balance=balance, client_id=id, date=date)
        new_payment.insert_records()

    return redirect(url_for('statements', id=id))

# make mpesa payments for each client
@app.route('/mpesapayments/<int:id>', methods=['POST'])
def mpesa_payment(id):
    d = datetime.now()

    month = d.month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', ' October',
              'November', 'December']
    month = months[month - 1]

    day = d.day
    year = d.year

    date = str(day) + ' ' + month + ' ' + str(year)
    date = str(date)
    print(date)

    try:
        client = PaymentsModel.fetch_by_id(id)
        statement_amount = client.payments[-1]

        prev_balance = statement_amount.balance
        prev_balance = int(prev_balance)

        print(prev_balance)
    except:
        prev_balance = 0
        print("No charges")
        # return redirect(url_for('payments', id=mid))

    if request.form['amount_paid']:
        amount_paid = request.form['amount_paid']
        transaction_type = "PAYMENT"
        transaction_id = request.form['transaction_id']
        balance = int(amount_paid) + prev_balance
        new_payment = PaymentsModel(transaction_type=transaction_type, transaction_id=transaction_id, amount=amount_paid, balance=balance, client_id=id, date=date)
        new_payment.insert_records()

    return redirect(url_for('statements', id=id))

# make cheque payment
@app.route('/chequepayments/<int:id>', methods=['POST'])
def cheque_payment(id):
    d = datetime.now()

    month = d.month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', ' October',
              'November', 'December']
    month = months[month - 1]

    day = d.day
    year = d.year

    date = str(day) + ' ' + month + ' ' + str(year)
    date = str(date)
    print(date)

    try:
        client = PaymentsModel.fetch_by_id(id)
        statement_amount = client.payments[-1]

        prev_balance = statement_amount.balance
        prev_balance = int(prev_balance)

        print(prev_balance)

        # print(prev_balance)
    except:
        prev_balance = 0
        print("No charges")
        # return redirect(url_for('payments', id=mid))

    if request.form['amount_paid']:
        amount_paid = request.form['amount_paid']
        transaction_type = "PAYMENT"
        cheque_no = request.form['cheque_no']
        bank_name = request.form['bank_name']
        balance = int(amount_paid) + prev_balance
        new_payment = PaymentsModel(transaction_type=transaction_type, cheque_no=cheque_no,bank_name=bank_name, amount=amount_paid, balance=balance, client_id=id, date=date)
        new_payment.insert_records()

    return redirect(url_for('statements', id=id))

# brought forward payments
@app.route('/forward_payments/<int:id>', methods=['POST'])
def forward_payment(id):
    d = datetime.now()

    month = d.month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', ' October',
              'November', 'December']
    month = months[month - 1]

    day = d.day
    year = d.year

    date = str(day) + ' ' + month + ' ' + str(year)
    date = str(date)
    print(date)

    client = ClientsModel.fetch_by_id(id)
    transaction_type = ""
    amount = 0
    try:
        met_amount = client.payments[-1]
        print(met_amount)
        flash("This is a one time service, Brought forwards already set!")
    except:
        balance = request.form['balance']
        if int(balance) >= 0:
            transaction_type = "PAYMENT"
            balance = balance
            amount = balance
        else:
            transaction_type = "BILL"
            balance = balance
            amount = -int(balance)

        new_payment = PaymentsModel(transaction_type=transaction_type, amount=amount, balance=balance, client_id=id, date=date)
        new_payment.insert_records()
    return redirect(url_for('statements', id=id))


if __name__ == '__main__':
    app.run()
