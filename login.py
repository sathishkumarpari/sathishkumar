#!C:\Users\Sathish\AppData\Local\conda\conda\envs\opencv-env\python.exe
import cgi
import pymysql

db=pymysql.connect("localhost","root","","userdetails")
cursor=db.cursor()

print("Content-type: text/html\n")

def start(title):
	print("<html>\n<head>\n<title>%s</title>\n</head>\n<body>\n"%(title))

def end():
	print("</body>\n</html>")

form=cgi.FieldStorage()
global username
global password
global temp_pwd
global temp_name

if not form:
	start("Invalid")
	print('"<center><h3>Invalid Attempt! Go to <a href="login_page.html">Login Page</a></h3></center>"')

if form.getvalue("uname") :
	temp=form.getvalue("uname")
	cursor.execute("select * from users where username='%s'"%(temp))
	row=cursor.fetchone()
	if not row:
		start("Not a User")
		print('<script>alert("username %s is not registered");</script>'%(temp))
	else:
		temp_name=temp
		username=row[0]
		password=row[1]

if form.getvalue("pwd"):
	temp_pwd=form.getvalue("pwd")

if (temp_name==username) and (temp_pwd==password):
	start("Successfully")
	print('<script>alert("Successfully Login!");</script>')
	print("<h3>welcome %s</h3>"%(username))
if (temp_name==username) and (temp_pwd!=password):
	start("Incorrect Data")
	print('<script>alert("Incorrect Password!");</script')

end()