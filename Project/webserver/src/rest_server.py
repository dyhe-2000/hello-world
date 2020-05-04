from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.renderers import render_to_response

import requests
import json
import mysql.connector as mysql
import os
import datetime
import smtplib, ssl

db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
db_host = os.environ['MYSQL_HOST'] 

USERS_FILE_PATH = "users.txt"
jetbotid = "jetbotid"

## File Utility methods
def read_file(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data

def write_to_file(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)
      
# update the txt file to data base info
def refresh_users_file():
  Lines = []
  # Connect to the database and retrieve the student
  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()
  cursor.execute("select * from TStudents;")
  records = cursor.fetchall()
  # cursor.execute("select userid from Tcuser where id = 1;")
  # userid = cursor.fetchall()
  # userid = str(userid)
  # fixuserid = userid[3:]#remove first two chars
  # userid = fixuserid[:-4]#remove last four chars
  for record in records:
    #print(str(record[0])) #id
    #print(str(record[1])) #user_id
    #print(str(record[2])) #pwd
    #print(str(record[3])) #status
    #print(str(record[4])) #created_at
    tempStr = ''
    for x in range(0, 6):
      tempStr += str(record[x])
      tempStr += ' '
    tempStr += '\n'
    print(tempStr)
    Lines.append(tempStr)
  file2 = open('templates/public/users.txt', 'w') 
  file2.writelines(Lines)
  file2.close()
  # file3 = open('templates/public/user.txt', 'w') 
  # file3.writelines(userid)
  # file3.close()

def check(test_str):
  import re
    #http://docs.python.org/library/re.html
    #re.search returns None if no position in the string matches the pattern
    #pattern to search for any character other then . a-z 0-9
  pattern = r'[^\.a-z0-9A-Z]'
  if re.search(pattern, test_str):
        #Character other then . a-z 0-9 was found
        #print 'Invalid : %r' % (test_str,)
        return False
  else:
        #No character other then . a-z 0-9 was found
        #print 'Valid   : %r' % (test_str,)
      return True
  
def get_home_page(req):
  return render_to_response('templates/Home_Page.html', {}, request=req)
  
def get_about_us(req):
  return render_to_response('templates/About_Us.html', {}, request=req)
  
def back_to_home_page(req):
  return render_to_response('templates/Home_Page.html', {}, request=req)
  
def get_post_user(req):
  return render_to_response('templates/post_user.html', {}, request=req)
  
def post_user(req):
  # x = datetime.datetime.utcnow()+datetime.timedelta(hours=-7)+datetime.timedelta(minutes=-12)+datetime.timedelta(seconds=30)
  # Connect to the database
  db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
  cursor = db.cursor()
  # get user info
  firstname = req.params['firstname']
  lastname = req.params['lastname']
  email = req.params['email']
  # print(check(userId))
  # print(check(password))
  tempStr = ''
  if firstname != tempStr and lastname != tempStr and email != tempStr:
    # Insert Records
    query = "insert into Customers (firstname, lastname, email) values (%s, %s, %s)"
    values = [
      (firstname, lastname, email)
    ]
    cursor.executemany(query, values)
    db.commit()
    return render_to_response('templates/Home_Page.html', {}, request=req)
  else:
    return render_to_response('templates/try_again.html', {}, request=req)
    
def sendAnEmial(req):
    print("in send an email function")
    port = 465
    sender = "allstarsei@gmail.com"
    password = "allstarsei123"
    recieve = req.params['receiverEmail']
    message = """\
Subject: IMPORTANT ECE140B PROJECT EMAIL


This message is sent from Python.Please do not reply to this email.\n\n"""
    message = message + str(req.params['message'])
    context = ssl.create_default_context()
    try:
      print("Starting to send")
      with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recieve, message)
      print("sent email!")
      return render_to_response('templates/success_send.html', {}, request=req)
    except:
      print("send email unsuccessful")
      return render_to_response('templates/unsuccess_send.html', {}, request=req)
      
def get_send_email(req):
    return render_to_response('templates/send_email.html', {}, request=req)
    
#--- this route will show a login form
def get_login(req):
  refresh_users_file()
  return render_to_response('templates/show_login.html', {}, request=req)

#check login info
def gotoAdminPortal(req):
  userId = req.params['userid']
  password = req.params['pwd']
  # Connect to the database and retrieve the student
  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()
  cursor.execute("select * from TStudents where userid='%s' and status = 'verified';" % userId) 
  record = cursor.fetchone()
  db.close()
  if record is None:
    return render_to_response('templates/invalid_credentials.html', {'error':'invalid credentials'}, request=req)
  else: # userId exists and is verified
      return render_to_response('templates/gotoAdminPortal.html', {}, request=req)
      
def sendASpecificEmial(email):
    print("in send an email function")
    port = 465
    sender = "allstarsei@gmail.com"
    password = "allstarsei123"
    recieve = email
    message = """\
Subject: IMPORTANT ECE140B PROJECT EMAIL


This message is sent from Python.Please do not reply to this email.\n\n"""
    message = message + 'Reminder: let us set up a conversation tomorrow, go to bed early'
    context = ssl.create_default_context()
    try:
      print("Starting to send")
      with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recieve, message)
      print("sent email!")
      return 'templates/success_send.html'
    except:
      print("send email unsuccessful")
      return 'templates/unsuccess_send.html'
      
def manipulateDataBase(req):
  print("in manipulateDataBase function!!!")
  buttonNumber = int(req.params['submit_button'])
  changeLineNumber = int(req.params['submit_button'])/2 #careful here, button number divide by 2 is changing line num
  
  if int(req.params['submit_button']) % 2 == 1 :
     print('sending an email')
     print(int(int(req.params['submit_button'])/2)) #use this line num to extract email address
     
     file1 = open('templates/public/users.txt', 'r') 
     Lines = file1.readlines() 
     file1.close()
     count = 0
     #Strips the newline character 
     for line in Lines: 
       if len(line.split()) >= 5:
         if count == int(int(req.params['submit_button'])/2):
           print('email is: ')
           email = str(line.split()[4])
           print(email)
           return render_to_response(sendASpecificEmial(email), {}, request=req) #send an email
       count = count + 1
     
     return render_to_response('templates/did_login.html', {}, request=req)
  
  print('button number is: ')
  print(buttonNumber)
  file1 = open('templates/public/users.txt', 'r') 
  Lines = file1.readlines() 
  file1.close()
  count = 0
  #Strips the newline character 
  print("in mainpulate function")
  for line in Lines: 
    if len(line.split()) >= 5:
      print(count)
      print(changeLineNumber)
      if line.split()[3] == "pending" and count == changeLineNumber:
        db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
        cursor = db.cursor()
        #Updating Records
        cursor.execute("update TStudents set status='verified' where userid='%s' and status = 'pending';" % line.split()[1])
        db.commit()
        print('---------- UPDATE ----------')
        print(cursor.rowcount, "record(s) updated.")
        refresh_users_file()
        return render_to_response('templates/did_login.html', {}, request=req)
      
      
      if line.split()[3] == "verified" and count == changeLineNumber: 
        db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
        cursor = db.cursor()      
        #Deleting Records
        cursor.execute("delete from TStudents where userid = '%s' and status = 'verified';" % line.split()[1])
        db.commit()

        print('---------- DELETE ----------')
        print(cursor.rowcount, "record(s) deleted.")
        refresh_users_file()
        return render_to_response('templates/did_login.html', {}, request=req)
    count = count + 1
  return render_to_response('templates/did_login.html', {}, request=req)
      
#--- this route will register
def get_register(req):
  print("get_register")
  return render_to_response('templates/register.html', {}, request=req)
  
  
def signUp(req):
  x = datetime.datetime.utcnow()+datetime.timedelta(hours=-7)+datetime.timedelta(minutes=-12)+datetime.timedelta(seconds=30)
  # Connect to the database
  db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
  cursor = db.cursor()
  # get user info
  userId = req.params['username']
  password = req.params['password']
  email = req.params['email']
  print(check(userId))
  print(check(password))
  print(check(email))
  tempStr = ''
  if check(userId) and check(password) and userId != tempStr and password != tempStr:
    # Insert Records
    query = "insert into TStudents (userid, pwd, status, email, created_at) values (%s, %s, %s, %s, %s)"
    values = [
      (userId,password, 'pending', email, x)
    ]
    cursor.executemany(query, values)
    db.commit()
    refresh_users_file()
    return render_to_response('templates/Home_Page.html', {}, request=req)
  else:
    return render_to_response('templates/try_again_for_register.html', {}, request=req)
    
#--- this is called to compare credentials to the value
def is_valid_user(req):
  return True
  
#--- this route will validate login credentials...
def did_login(req):
  print("post_login")
  if is_valid_user(req):   
    return render_to_response('templates/did_login.html', {}, request=req)
  else:
    return render_to_response('templates/show_login.html', {'error':'invalid credentials'}, request=req)
    
def get_product_features(req):
  return render_to_response('templates/product_features.html', {}, request=req)
  
def get_pricing(req):
  return render_to_response('templates/pricing.html', {}, request=req)

''' Route Configurations '''
if __name__ == '__main__':
  config = Configurator()

  config.include('pyramid_jinja2')
  config.add_jinja2_renderer('.html')

  config.add_route('v2', '/')
  config.add_view(get_home_page, route_name='v2')
  
  config.add_route('login', '/login')
  config.add_view(get_login, route_name='login')
  config.add_view(gotoAdminPortal, route_name='login', request_method='POST')
  
  config.add_route('register', '/register')
  config.add_view(get_register, route_name='register')
  config.add_view(signUp, route_name='register', request_method='POST')
  
  config.add_route('did_login', '/did_login')
  config.add_view(did_login, route_name='did_login')
  config.add_view(manipulateDataBase, route_name='did_login', request_method='POST')
  
  config.add_route('about_us', '/about_us')
  config.add_view(get_about_us, route_name='about_us')
  
  config.add_route('product_features', '/product_features')
  config.add_view(get_product_features, route_name='product_features')
  
  config.add_route('pricing', '/pricing')
  config.add_view(get_pricing, route_name='pricing')
  
  config.add_route('send_email', '/send_email')
  config.add_view(get_send_email, route_name='send_email')
  config.add_view(sendAnEmial, route_name='send_email', request_method='POST')
  
  config.add_route('backToHomePage', '/')
  config.add_view(back_to_home_page, route_name='backToHomePage')
  config.add_view(back_to_home_page, route_name='backToHomePage', request_method='POST')
  
  config.add_route('post_user', '/post_user')
  config.add_view(get_post_user, route_name='post_user')
  config.add_view(post_user, route_name='post_user', request_method='POST')
  
  
  config.add_static_view(name='/', path='./templates/public', cache_max_age=3600) #expose the public folder for the CSS file

  app = config.make_wsgi_app()
  server = make_server('0.0.0.0', 6000, app)
  server.serve_forever()