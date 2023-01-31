import os
from flask import Flask, render_template, request, redirect, url_for, session ,flash ,logging
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_uploads import UploadSet, configure_uploads, IMAGES
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
 
app.secret_key = 'xyzsdfg'

app.config['UPLOADED_PHOTOS_DEST'] = 'static/images/books'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'
  
mysql = MySQL(app)



#default home page 
@app.route('/')
def Home():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT  * FROM books')
    data = cur.fetchall()
    cur.close()
    return render_template('Home.html' , books=data) 

#login page 
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('user.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

#register page   
@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
            return render_template('user.html', mesage = mesage)
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)



@app.route('/admin_login', methods =['GET', 'POST'])
def admin_login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE email = % s AND password = % s', (email, password, ))
        admin = cursor.fetchone()
        if admin:
            session['loggedin'] = True
            session['id'] = admin['id']
            session['firstName'] = admin['firstName']
            session['email'] = admin['email']
            mesage = 'Logged in successfully !'
            return  redirect(url_for('admin'))
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('admin_login.html', mesage = mesage)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    if request.method == 'POST': 
        flash("Data Inserted Successfully")
        title = request.form['title']
        category = request.form['category']
        item = request.form['item']
        price = request.form['price']
        author = request.form['author']
        description = request.form['description']
        stock = request.form['stock']
        file = request.files['picture']
        pic = file.filename
        photo = pic.replace("'", "")
        picture = photo.replace(" ", "_")
        if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
             save_photo = photos.save(file)
             if save_photo:
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO books VALUES (NULL,%s, %s, %s, %s, %s, %s, %s, %s)', (title, category, item, price, author, description, stock,  picture))
                mysql.connection.commit()
             else:
                flash('Picture not save', 'danger')
                return redirect(url_for('add_product'))
        else:
                flash('File not supported', 'danger')
                return redirect(url_for('add_product'))        
        
    return render_template('add_product.html')



@app.route('/all_product')
def all_product():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT  * FROM books')
    data = cur.fetchall()
    cur.close()
    return render_template('index2.html', books=data)

@app.route('/all_users')
def all_users():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT  * FROM users')
    data = cur.fetchall()
    cur.close()
    return render_template('all_users.html', users=data)

@app.route('/all_orders')
def all_orders():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT  * FROM orders')
    data = cur.fetchall()
    cur.close()
    return render_template('all_orders.html', orders=data)    

@app.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        id_data = request.form['id']
        title = request.form['title']
        category = request.form['category']
        item = request.form['item']
        price = request.form['price']
        author = request.form['author']
        description = request.form['description']
        stock = request.form['stock']
        file = request.files['picture']
        pic = file.filename
        photo = pic.replace("'", "")
        picture = photo.replace(" ", "")
        if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
         file.filename = picture
         save_photo = photos.save(file)
         if save_photo:
            cur = mysql.connection.cursor()
            cur.execute("""
               UPDATE books
               SET title=%s, category=%s, item=%s, price=%s, author=%s, description=%s, stock=%s, picture=%s
               WHERE id=%s
            """, (title, category, item, price, author, description, stock,  picture, id_data))
            flash("Data Updated Successfully")
            mysql.connection.commit()
         
         else:
            flash('Pic not upload', 'danger')
            return redirect(url_for('all_product'))
        else:
            flash('File not support', 'danger')
            return redirect(url_for('all_product'))
                                               
    return redirect(url_for('all_product'))

@app.route('/delete/<string:id>', methods = ['GET'])
def delete(code):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM books WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('all_product'))


@app.route('/detail')
def detail():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM books ")
    data = cur.fetchall()
    cur.close()
    return render_template('detail.html', books=data)
    
        



@app.route('/add', methods=['POST'])
def add_product_to_cart():
    _quantity = int(request.form['quantity'])
    _code = request.form['code']
    # validate the received values
    if _quantity and _code and request.method == 'POST':
 
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
 
        cur.execute('SELECT * FROM books WHERE code = %s', (_code,))
        row = cur.fetchone()
                 
        itemArray = { row['code'] : {'title' : row['title'], 'code' : row['code'], 'quantity' : _quantity, 'price' : row['price'], 'picture' : row['picture'], 'total_price': _quantity * row['price']}}
                 
        all_total_price = 0
        all_total_quantity = 0
                 
        session.modified = True
        if 'cart_item' in session:
            if row['code'] in session['cart_item']:
                for key, value in session['cart_item'].items():
                    if row['code'] == key:
                        old_quantity = session['cart_item'][key]['quantity']
                        total_quantity = old_quantity + _quantity
                        session['cart_item'][key]['quantity'] = total_quantity
                        session['cart_item'][key]['total_price'] = total_quantity * row['price']
            else:
                session['cart_item'] = array_merge(session['cart_item'], itemArray)
         
            for key, value in session['cart_item'].items():
                individual_quantity = int(session['cart_item'][key]['quantity'])
                individual_price = float(session['cart_item'][key]['total_price'])
                all_total_quantity = all_total_quantity + individual_quantity
                all_total_price = all_total_price + individual_price
        else:
            session['cart_item'] = itemArray
            all_total_quantity = all_total_quantity + _quantity
            all_total_price = all_total_price + _quantity * row['price']
             
        session['all_total_quantity'] = all_total_quantity
        session['all_total_price'] = all_total_price
                 
        return render_template('cart.html')
    else:
        return 'Error while adding item to cart'
 
@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return render_template('cart.html')
    except Exception as e:
        print(e)
 
@app.route('/sup/<string:code>')
def delate_book(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
         
        for item in session['cart_item'].items():
            if item[0] == code:    
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break
         
        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price
             
        return render_template('cart.html')
    except Exception as e:
        print(e)
 
def array_merge( first_array , second_array ):
    if isinstance( first_array , list ) and isinstance( second_array , list ):
        return first_array + second_array
    elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
        return dict( list( first_array.items() ) + list( second_array.items() ) )
    elif isinstance( first_array , set ) and isinstance( second_array , set ):
        return first_array.union( second_array )
    return False



if __name__ == "__main__":
    app.run(debug=True)