from flask import Flask, render_template, url_for, request, redirect, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from config import Development, Production
from datetime import datetime
from functools import wraps
import pygal
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
from models.Auth import AuthModel
# create tables in our database
@app.before_first_request
def create_tables():
    db.create_all()


@app.before_request
def setg():
    g.user = None
    if session:
        if session['username']:
            g.user = session['username']
        else:
            g.user = None
    else:
        g.user = None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/3b4c830cd7d88c05cfa5d6da59af4561', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']
        confirm_passw = request.form['confirm_passw']
        hashed = AuthModel.generate_hash(passw)

        if passw == confirm_passw:
            if AuthModel.check_email(mail) and AuthModel.check_username(uname):
                flash("Username/Email already exists")
                return render_template("register.html")
            else:
                register = AuthModel(username=uname, email=mail, password=hashed)
                register.insert_records()

                return redirect(url_for("login"))
        else:
            flash("The two passwords do not match!")
            return render_template("register.html")
    return render_template("register.html")

# logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def hello_world():
    if session:
        system_user = AuthModel.fetch_by_username(session['username'])
        print(system_user.id)

        d = datetime.now()

        month = d.month
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', ' October',
                  'November', 'December']
        month = months[month - 1]
        year = d.year

        month = month + ' ' + str(year)
        search_date = month
        print("This is the search date: ", search_date)

        amount_billed = 0
        amount_paid = 0
        statements = PaymentsModel.fetch_by_search_date(search_date)
        for statement in statements:
            if statement.transaction_type == "BILLING":
                amount_billed += statement.amount
            else:
                amount_paid += statement.amount
        print("Total bill: ", amount_billed)
        print("Amount Paid: ", amount_paid)
        pending = amount_billed - amount_paid
        if pending < 0:
            pending = 0
        print("Pending amount: ", pending)

        billed = [amount_billed]
        paid = [amount_paid]
        pending = [pending]
        search_date = [search_date]
        print(search_date)
        print(billed)
        print(paid)
        print(pending)

        # create a pie chart
        pie_chart = pygal.Pie()
        pie_chart.title = 'Sales Statistics '
        pie_chart.add('Amount Billed', billed)
        pie_chart.add('Amount Paid', paid)
        pie_chart.add('Amount Pending', pending)
        graph = pie_chart.render_data_uri()
        print(graph)

        return render_template('home.html', search_date=search_date, billed=billed, paid=paid, pending=pending, graph=graph)
    else:
        return redirect(url_for('login'))


@app.route('/')
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        if AuthModel.fetch_by_username(uname):
            if AuthModel.check_password(uname, passw):
                session['username'] = uname
                session['uid'] = AuthModel.fetch_by_username(uname).id
                # session['role'] = 'admin'
                # print(session['role'])
                return redirect(url_for('hello_world'))
        # flash("Admin With Such Username does not Exist!")
    return render_template("login.html")


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
        new = ClientsModel(client_name=client_name, branch=branch, email=email, phone_number=phone_number, system_user_id=session['uid'])
        new.insert_records()
    return redirect(url_for('clients_information'))

# clients info route
@app.route('/clients_information')
@login_required
def clients_information():
    system_user = AuthModel.fetch_by_username(session['username'])
    # print(system_user.id)

    clients = system_user.clients
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
@login_required
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
@login_required
def create_invoice(id):
    client = ClientsModel.fetch_by_id(id)
    return render_template('create_invoice.html', client=client)

# generate invoice // this is now inside the create invoice route
@app.route('/generate_invoice/<int:id>', methods=['POST'])
def generate_invoice(id):
    # generate invoice number
    try:
        invoice = InvoicesModel.fetch_all()
        last = invoice[-1]
        last_invoice_no = last.invoice_no
        invoice_no = last_invoice_no + 1
    except:
        invoice_no = 1000

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

    d = datetime.now()

    month = d.month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', ' October',
              'November', 'December']
    month = months[month - 1]
    year = d.year

    month = month + ' ' + str(year)
    print(month)
    print(date)
    print(invoice_no)

    invoice_particulars = InvoiceProductsModel.fetch_by_invoice_id(id)

    sum = 0
    for each in invoice_particulars:
        sum += int(each.total)
    print("Total Cost of Products is: ", sum)

    if sum != 0:
        client_id = invoice.client_id
        try:
            statement = PaymentsModel.fetch_by_client_id(client_id)
            client_id = statement.client_id
            client = ClientsModel.fetch_by_id(client_id)
            statement_amount = client.payments[-1]

            prev_balance = statement_amount.balance
            prev_balance = int(prev_balance)

            print("prev balance is :", prev_balance)

            if prev_balance >= sum:
                transaction_type = "PAYMENT"
                balance = prev_balance - sum

                if PaymentsModel.check_invoice_no(invoice_no):
                    flash("Invoice Already Exists!!")
                    return redirect(url_for('invoice_products', id=id))
                new = PaymentsModel(invoice_no=invoice_no, transaction_type=transaction_type, amount=sum,
                                    balance=balance, date=date, search_date=month, client_id=client_id)
                new.insert_records()
                flash("Invoice submitted successfully!")
            else:
                transaction_type = "BILLING"
                balance = prev_balance - sum

                if PaymentsModel.check_invoice_no(invoice_no):
                    flash("Invoice Already Exists!!")
                    return redirect(url_for('invoice_products', id=id))
                new = PaymentsModel(invoice_no=invoice_no, transaction_type=transaction_type, amount=sum,
                                    balance=balance, date=date, search_date=month, client_id=client_id)
                new.insert_records()
                flash("Invoice submitted successfully!")
            return redirect(url_for('invoice_products', id=id))

        except:
            prev_balance = 0
            print("This is the last balance from statements: ", prev_balance)
            transaction_type = "BILLING"
            balance = -sum

            print("This is client id: ", client_id)
            if PaymentsModel.check_invoice_no(invoice_no):
                flash("Invoice Already Exists!!")
                return redirect(url_for('invoice_products', id=id))
            new = PaymentsModel(invoice_no=invoice_no, transaction_type=transaction_type, amount=sum, balance=balance, date=date, search_date=month, client_id=client_id)
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
    search_date = month + ' ' + str(year)
    date = str(date)
    print(date)


    try:
        statement = PaymentsModel.fetch_by_client_id(id)
        client_id = statement.client_id
        client = ClientsModel.fetch_by_id(client_id)
        statement_amount = client.payments[-1]

        prev_balance = statement_amount.balance
        prev_balance = int(prev_balance)

        print("prev balance is :", prev_balance)
    except:
        prev_balance = 0
        print("No charges")
        # return redirect(url_for('payments', id=mid))

    if request.form['amount_paid']:
        amount_paid = request.form['amount_paid']
        transaction_type = "PAYMENT"
        balance = int(amount_paid) + prev_balance
        new_payment = PaymentsModel(transaction_type=transaction_type, amount=amount_paid, balance=balance, client_id=id, date=date, search_date=search_date)
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
    search_date = month + ' ' + str(year)
    date = str(date)
    print(date)

    try:
        statement = PaymentsModel.fetch_by_client_id(id)
        client_id = statement.client_id
        client = ClientsModel.fetch_by_id(client_id)
        statement_amount = client.payments[-1]

        prev_balance = statement_amount.balance
        prev_balance = int(prev_balance)

        print("prev balance is :", prev_balance)
    except:
        prev_balance = 0
        print("No charges")
        # return redirect(url_for('payments', id=mid))

    if request.form['amount_paid']:
        amount_paid = request.form['amount_paid']
        transaction_type = "PAYMENT"
        transaction_id = request.form['transaction_id']
        balance = int(amount_paid) + prev_balance
        new_payment = PaymentsModel(transaction_type=transaction_type, transaction_id=transaction_id, amount=amount_paid, balance=balance, client_id=id, date=date, search_date=search_date)
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
    search_date = month + ' ' + str(year)
    date = str(date)
    print(date)

    try:
        statement = PaymentsModel.fetch_by_client_id(id)
        client_id = statement.client_id
        client = ClientsModel.fetch_by_id(client_id)
        statement_amount = client.payments[-1]

        prev_balance = statement_amount.balance
        prev_balance = int(prev_balance)

        print("prev balance is :", prev_balance)
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
        new_payment = PaymentsModel(transaction_type=transaction_type, cheque_no=cheque_no,bank_name=bank_name, amount=amount_paid, balance=balance, client_id=id, date=date, search_date=search_date)
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
    search_date = month + ' ' + str(year)
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

        new_payment = PaymentsModel(transaction_type=transaction_type, amount=amount, balance=balance, client_id=id, date=date, search_date=search_date)
        new_payment.insert_records()
    return redirect(url_for('statements', id=id))


if __name__ == '__main__':
    app.run()
