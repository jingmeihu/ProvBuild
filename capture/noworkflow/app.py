import os
import re
import commands
import time 
import string
from flask import Flask, request, redirect, url_for, render_template,session
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = set(['py'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "HII"

def stripComments(code):
    #code = str(code) code code
    #return re.sub(r'(?m) *#.*\n?', '\n', code)
    return code

@app.route('/normal', methods = ['GET', 'POST'])
def normal():
   if request.method == 'POST':
		user_file = request.files['file']
		user_file.save(secure_filename(user_file.filename))

		file = open("session.txt", "w")
		file.write("session:" + user_file.filename)

		timefile = open("time.txt", "a")
		timefile.write(user_file.filename + "\n")

		timefile.write("NORMAL start run:" + str(time.time()) + "\n")
		print 'python ' + user_file.filename
		status, output = commands.getstatusoutput('python ' + user_file.filename)
		timefile.write("NORMAL end run:" + str(time.time()) + "\n")

		return render_template('normal.html', 
		 					user_file=user_file.filename, 
		 					message="completed run", 
		 					content=open(user_file.filename, 'r').read(), 
		 					status=status, 
		 					result=open("result.txt", "r").read(),
		 					output=output)
@app.route("/finish", methods=['POST'])
def finish():
	file = open("session.txt", "r") 
	filename = file.readline().split(":",1)[1] 
	currfile = open(filename, "w")
	origfile = open("backup-" + filename, "r")
	currfile.write(origfile.read())

	timefile = open("time.txt", "a")
	timefile.write("NORMAL finish:" + str(time.time())  + "\n")
	timefile.write("--------------------------------------\n")
	return render_template('index.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
		user_file = request.files['file']
		user_file.save(secure_filename(user_file.filename))

		file = open("session.txt", "w")
		file.write("session:" + user_file.filename)

		commands.getstatusoutput('rm -r .noworkflow')
		commands.getstatusoutput('rm ProvScript.py')

		timefile = open("time.txt", "a")
		timefile.write(user_file.filename + "\n")

		timefile.write("PROVBUILD start run:" + str(time.time()) + "\n")
		print 'python __init__.py run ' + user_file.filename
		status, output = commands.getstatusoutput('python __init__.py run ' + user_file.filename)
		timefile.write("PROVBUILD end run:" + str(time.time()) + "\n")

		return render_template('upload.html', 
		 					user_file=user_file.filename, 
		 					message="completed run", 
		 					content=open(user_file.filename, 'r').read(), 
		 					status=status, 
		 					result=open("result.txt", "r").read(),
		 					output=output, 
		 					provscript="Please execute the 'update' command to generate a ProvScript.")

@app.route("/update", methods=['POST'])
def update():
        file = open("session.txt", "r") 
        filename = file.readline().split(":",1)[1]
	if not request.form['function'] : 
		return render_template('upload.html', 
			user_file=filename, 
			message="unable to execute update -- no variable or function name", 
			content=session['content'], 
			status="", 
			result=open("result.txt", "r").read(),
			output="Please enter a variable or function name to update", 
			provscript="Please execute the 'update' command again to generate a ProvScript.")	

	command = "python __init__.py update -t 1 "
	if (request.form['function']): 
		command += "-fn " + request.form['function'] + " "

	timefile = open("time.txt", "a")
	timefile.write("PROVBUILD start update:" + str(time.time())  + "\n")
	print command + filename
	status, output = commands.getstatusoutput(command + filename)
	timefile.write("PROVBUILD end update:" + str(time.time())  + "\n")

	return render_template('upload.html', 
					user_file=filename, 
					message="completed update", 
					content=open(filename, 'r').read(), 
					status=status, 
					result=open("result.txt", "r").read(),
					output=output, 
					provscript=stripComments(open("ProvScript.py", "r").read().split("relevant to your update", 1)[1]))

@app.route("/runupdate", methods=['POST'])
def runupdate():
	file = open("session.txt", "r") 
	filename = file.readline().split(":",1)[1] 

	f = open('ProvScript.py', 'w')
	f.write(request.form['provscript'].replace("&gt;", ">").replace("&lt;", "<").replace("<br>", "\n").replace("<div>", "\n").replace("</div>", "\n"))
	f.close()

	timefile = open("time.txt", "a")
	timefile.write("PROVBUILD start runupdate:" + str(time.time())  + "\n")
	print 'python ProvScript.py'
	status, output = commands.getstatusoutput('python ProvScript.py')
	timefile.write("PROVBUILD end runupdate:" + str(time.time())  + "\n")
	return render_template('upload.html', 
							user_file=filename, 
							message="completed runupdate", 
							content=open(filename, 'r').read(), 
							status=status, 
							result=open("result.txt", "r").read(),
							output=output, 
							provscript=stripComments(open("ProvScript.py", "r").read()))

@app.route("/runnormal", methods=['POST'])
def runnormal():
	file = open("session.txt", "r") 
	filename = file.readline().split(":",1)[1] 

	f= open(filename, 'w')
	f.write(request.form['script'].replace("&gt;", ">").replace("<br>", "\n").replace("&lt;", "<").replace("<div>", "\n").replace("</div>", "\n"))
	f.close()

	timefile = open("time.txt", "a")
	timefile.write("NORMAL start run:" + str(time.time())  + "\n")
	print 'python '	+ filename
	status, output = commands.getstatusoutput('python '	+ filename)
	timefile.write("NORMAL end run:" + str(time.time())  + "\n")

	return render_template('normal.html', 
							user_file=filename, 
							message="completed runupdate", 
							content=open(filename, 'r').read(), 
							status=status, 
							result=open("result.txt", "r").read(),
							output=output)

@app.route("/merge", methods=['POST'])
def merge():
	timefile = open("time.txt", "a")
	timefile.write("PROVBUILD start merge:" + str(time.time()) + "\n")
	print 'python __init__.py merge -t 1'
	status, output = commands.getstatusoutput('python __init__.py merge -t 1')
	timefile.write("PROVBUILD end merge:" + str(time.time()) + "\n")
	timefile.write("--------------------------------------\n")

	file = open("session.txt", "r") 
	filename = file.readline().split(":",1)[1] 
	newfilename = "new-" + filename

	newfile = open(newfilename, "r") 
	return render_template('upload.html', 
							user_file=newfilename, 
							message="completed merge", 
							content=newfile.read(), 
							status=status, 
							result=open("result.txt", "r").read(),
							output=output, 
							provscript="Please execute the 'run + update' command to generate a ProvScript.")

@app.route("/")
def main():
	open('result.txt', 'w').close()
	return render_template('index.html')
if __name__ == "__main__":
        app.run()
