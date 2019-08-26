"""
customers - clients :  orders pseudo column
orders - invoices : customer_id, product_id
products - products : customer pseudo column
# """
from datetime import datetime

d = datetime.now()

month = d.month
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', ' October',
          'November', 'December']
month = months[month-1]
year = d.year

month = month + ' ' + str(year)
print(month)

