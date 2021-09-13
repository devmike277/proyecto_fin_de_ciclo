from flask import Flask, render_template, Response, request,url_for, redirect, session, flash
from streamer import Streamer
#from flask_mysqldb import MySQL
import pymysql.cursors
import re

app = Flask(__name__)

app.secret_key = 'clavesecreta'

dbhost = "localhost"
dbuser = "lamp_user"
dbuserpass = "14MpU53RP4$$"
datab = "lamp_db"

def gen():
  streamer = Streamer('', 8080)
  streamer.start()

  while True:
    if streamer.streaming:
      yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + streamer.get_jpeg() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
  return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def home():
  if 'loggedin' in session and session['loggedin']:
    return redirect(url_for('admin'))
  return render_template('index.html')

@app.route('/login')
def login():
  if 'loggedin' in session and session['loggedin']:
    return redirect(url_for('admin'))
  return render_template('login.html')

@app.route('/video')
def video():
  if 'loggedin' in session and session['loggedin']:
    return render_template('video.html')
  return render_template('index.html')

@app.route('/logout')
def logout():
  session.pop('loggedin',None)
  session.pop('username',None)
  session.pop('userid',None)
  print(session)
  return redirect(url_for('login'))

@app.route('/checklogin',methods=['POST'])
def checklogin():
  alert = 0
  if request.method == 'POST':
    username = request.form['user']
    password = request.form['pass']
    if not username or not password:
      flash('Please fill out the form')
      alert = 2;

    else:
      if not re.match(r'[\w\d]{4,12}$',username):
        flash('Invalid Username')
        alert = 2

      elif not re.match(r'[\w\d]{4,20}$',password):
        flash('Invalid Password')
        alert = 2
      
      else:
        db = pymysql.connect(host=dbhost,user=dbuser,password=dbuserpass,database=datab)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE name = %s',username)
        account = cursor.fetchone()

        if account:
          if account[3] == password:
            session['loggedin'] = True
            session['username'] = account[1]
            session['userid'] = account[0]
            return redirect(url_for('admin')) 

          else:
            flash('Incorrect password')
            alert = 1

        else:
          flash('Account does not exists')
          alert = 2

  return redirect(url_for('login', alertType=alert))

@app.route("/admin")
def admin():

  dbconection = pymysql.connect(host=dbhost,user=dbuser,password=dbuserpass,database=datab)
  sql = 'SELECT * FROM `users`'
  cursor = dbconection.cursor()
  cursor.execute(sql)
  results = cursor.fetchall()
  dbconection.close()

  print(results)
  if 'loggedin' in session and session['loggedin']:
    return render_template('admin.html',users=results)
  return redirect(url_for('home'))
  

@app.route('/add_user',methods=['POST'])
def add():
  alert = 0

  if request.method == 'POST':
    user = request.form['user']
    email = request.form['email']
    password = request.form['pass']
    
    if not user or not email or not password:
      flash('Please fill out the form')
      alert = 2;

    else:
      if not re.match(r'[\w\d]{4,12}$',user):
        flash('User name must be between 4 and 12 length, and contains characters or numbers or both')
        alert = 2

      elif not re.match(r'\b[\w]+@[\w]+\.[a-zA-Z]{2,3}\b',email):
        flash('Invalid email adress')
        alert = 2

      elif not re.match(r'[\w\d]{4,20}$',password):
        flash('Invalid password')
        alert = 2

      else:
        dbconection = pymysql.connect(host=dbhost,user=dbuser,password=dbuserpass,database=datab)
        sql = 'SELECT * FROM `users` WHERE name = %s AND email= %s'
        cursor = dbconection.cursor()
        cursor.execute(sql,(user,email))
        result = cursor.fetchone()

        if not result:
          sql = 'INSERT INTO `users` (`name`,`email`,`password`) VALUES (%s,%s,%s)'
          cursor.execute(sql,(user,email,password))
          dbconection.commit()
          
          flash('User Added Succesfully')
          alert = 1

        else:
          flash('User exist')
          alert = 2

        dbconection.close()  

  return redirect(url_for('admin',alertType=alert))


@app.route('/edit_user/<string:id>')
def edit(id):

  dbconection = pymysql.connect(host=dbhost,user=dbuser,password=dbuserpass,database=datab)
  cursor = dbconection.cursor()
  cursor.execute( 'SELECT * FROM `users` WHERE `id` = {0}'.format(id))
  result = cursor.fetchall()
  dbconection.close()

  print (result[0])
  if 'loggedin' in session and session['loggedin']:
    return render_template('edit.html',user = result[0])
  return redirect(url_for('home'))

@app.route('/update/<string:id>',methods=['POST'])
def update(id):
  alert = 0

  if request.method == 'POST':
    user = request.form['user']
    email = request.form['email']
    password = request.form['pass']

    if not user or not email or not password:
      flash('Please don`t let empty fields')
      alert = 2;

    else:

      dbconection = pymysql.connect(host=dbhost,user=dbuser,password=dbuserpass,database=datab)
      sql = 'SELECT * FROM `users` WHERE name = %s AND email= %s AND password = %s AND id !={0}'.format(id)
      cursor = dbconection.cursor()
      cursor.execute(sql,(user,email,password))
      result = cursor.fetchone()

      if not re.match(r'[\w\d]{4,12}$',user):
        flash('User name must be between 4 and 12 length, and contains characters or numbers or both')
        alert = 2

      elif not re.match(r'\b[\w]+@[\w]+\.[a-zA-Z]{2,3}\b',email):
        flash('Invalid email adress')
        alert = 2

      elif not re.match(r'[\w\d]{4,20}$',password):
        flash('Invalid password, passwoerd name must be between 4 and 12 length, and contains characters or numbers or both')
        alert = 2

      else:
        if not result: 
          sql = 'UPDATE `users` SET `name` = %s, `email` = %s , `password` = %s WHERE `id` = {0}'.format(id)
          cursor.execute(sql,(user,email,password))
          dbconection.commit()
          
          alert = 1
          flash('User Updated Succesfully')
        
        else:
          alert = 2
          flash('Don`t duplicate users')

        dbconection.close()
    return redirect(url_for('admin',alertType=alert))
  

@app.route('/delete_user/<string:id>')
def delete(id):

  dbconection = pymysql.connect(host=dbhost,user=dbuser,password=dbuserpass,database=datab)
  cursor = dbconection.cursor()
  cursor.execute( 'DELETE FROM `users` WHERE `id` = {0}'.format(id))
  dbconection.commit()
  dbconection.close()

  flash('User Removed Succesfully')

  return redirect(url_for('admin', alertType=1))


if __name__ == '__main__':
  app.run(host='localhost', debug=True, threaded=True)
