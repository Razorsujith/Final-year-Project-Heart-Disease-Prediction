from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import numpy as np
import pickle


  
app = Flask(__name__)
sc = pickle.load(open('sc.pkl', 'rb'))
model = pickle.load(open('model.pkl', 'rb'))

app.secret_key = 'xyzsdfg'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'
  
mysql = MySQL(app)
  
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
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
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)




@app.route('/predict',methods=['POST'])
def predict():
    lst = []
    cp = int(request.form['chest pain type (4 values)'])
    if cp == 0:
        lst += [1 , 0 ,0 ,0]
    elif cp == 1:
        lst += [0 ,1 ,0 ,0]
    elif cp == 2:
        lst += [0 ,0 ,1 ,0]
    elif cp >= 3:
        lst += [0 ,0 ,0 ,1]
    trestbps = int(request.form["resting blood pressure" ])
    lst += [trestbps]
    chol = int(request.form["serum cholestoral in mg/dl"])
    lst += [chol]
    fbs = int(request.form["fasting blood sugar > 120 mg/dl"])
    if fbs == 0:
        lst += [1 , 0]
    else:
        lst += [0 , 1]
    restecg = int(request.form["resting electrocardiographic results (values 0,1,2)"])
    if restecg == 0:
        lst += [1 ,0 ,0]
    elif restecg == 1:
        lst += [0 ,1 ,0]
    else:
        lst += [0 , 0,1]
    thalach = int(request.form["maximum heart rate achieved"])
    lst += [thalach]
    exang = int(request.form["exercise induced angina"])
    if exang == 0:
        lst += [1 , 0]
    else:
        lst += [0 ,1 ]
    final_features = np.array([lst])
    pred = model.predict( sc.transform(final_features))
    return render_template('result.html', prediction = pred)
  
if __name__ == "__main__":
    app.run(debug=True)
