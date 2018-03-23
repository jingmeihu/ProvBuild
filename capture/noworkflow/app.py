import os
import re
import commands
import time 
import string
from flask import Flask, request, redirect, url_for, render_template,session
from werkzeug.utils import secure_filename
import threading
import webbrowser

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = set(['py'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "HII"

def stripComments(code):
    #code = str(code) code code
    #return re.sub(r'(?m) *#.*\n?', '\n', code)
    return code

def cleanhtml(code):
	code = str(code)
	cleanrule = re.compile('<.*?>')
	cleantext = re.sub(cleanrule, '', code)
	return cleantext

def getFuncname(line):
	flag = 0
	name = ""
	for i in line:
		if i == "'" and flag == 0:
			flag = 1
			continue
		elif i == "'" and flag == 1:
			break
		elif flag == 1:
			name += i
	return name


@app.route('/normal', methods = ['GET', 'POST'])
def normal():
   if request.method == 'POST':
		user_file = request.files['file']
		user_file.save(secure_filename(user_file.filename))

		user_name = request.form['username']

		file = open("record-time/session.txt", "w")
		file.write(user_name + ":" + user_file.filename + ":" + "NORMAL")

		# initialize the first run, recall the time
		print 'run ' + user_file.filename + ": " + 'python '	+ user_file.filename
		timefile = open("record-time/time.txt", "a")
		timefile.write(user_name + "\t" + user_file.filename + "\n")
		timefile.write("NORMAL start first run: \t" + str(time.time()) + "\n")
		status, output = commands.getstatusoutput('python ' + user_file.filename)
		timefile.write("NORMAL end first run and we start here: \t" + str(time.time()) + "\n")

		return render_template('normal.html', 
		 					user_file=user_file.filename, 
		 					message="Initial Done", 
		 					content=open(user_file.filename, 'r').read(), 
		 					status=status, 
		 					result=open("result.txt", "r").read(),
		 					output=output)

@app.route("/runnormal", methods=['POST'])
def runnormal():
	file = open("record-time/session.txt", "r") 
	info = file.readline().split(":")
	username = info[0]
	filename = info[1] 

	f= open(filename, 'w')
	code = request.form['script'].replace("<br>", "\n").replace("<div>", "\n").replace("</div>", "\n")
	finalcode = cleanhtml(code)
	finalcode = finalcode.replace("&gt;", ">").replace("&lt;", "<")
	f.write(finalcode)
	f.close()

	# execute the script
	print 'run '	+ filename + ": " + 'python '	+ filename
	timefile = open("record-time/time.txt", "a")
	timefile.write("NORMAL start run: \t" + str(time.time())  + "\n")
	status, output = commands.getstatusoutput('python '	+ filename)
	timefile.write("NORMAL end run: \t" + str(time.time())  + "\n")

	return render_template('normal.html', 
							user_file=filename, 
							message="Execute Done", 
							content=open(filename, 'r').read(), 
							status=status, 
							result=open("result.txt", "r").read(),
							output=output)

@app.route("/finish", methods=['POST'])
def finish():
	# update finish time
	timefile = open("record-time/time.txt", "a")
	timefile.write("NORMAL finish: \t" + str(time.time())  + "\n")
	timefile.write("--------------------------------------\n")

	file = open("record-time/session.txt", "r") 
	info = file.readline().split(":")
	username = info[0]
	filename = info[1] 

	# keep the user's script and recall the script for next user
	commands.getstatusoutput ('mv ' + filename + ' ' + './Task-results/' + username + '-' + filename)
	commands.getstatusoutput ('mv ./record-time/time.txt ./Task-time/' + username + '-' + filename + '-normaltime.txt')
	# commands.getstatusoutput ('rm ' + filename)
	# commands.getstatusoutput ('cp ' + './examplebackup/' + filename + ' ' + filename)

	return render_template('index.html')

@app.route('/provbuild', methods = ['GET', 'POST'])
def provbuild():
   if request.method == 'POST':
		user_file = request.files['file']
		user_file.save(secure_filename(user_file.filename))

		user_name = request.form['username']

		file = open("record-time/session.txt", "w")
		file.write(user_name + ":" + user_file.filename + ":" + "PROVBUILD")

		print 'run ' + user_file.filename + ": " + './make.sh r ' + user_file.filename
		timefile = open("record-time/time.txt", "a")
		timefile.write(user_name + "\t" + user_file.filename + "\n")
		timefile.write("PROVBUILD start first run: \t" + str(time.time()) + "\n")
		status, output = commands.getstatusoutput('./make.sh r ' + user_file.filename)
		timefile.write("PROVBUILD end first run and we start here: \t" + str(time.time()) + "\n")

		print 'update ' + user_file.filename + ": " + './make.sh uf output_write'
		timefile = open("record-time/time.txt", "a")
		timefile.write("PROVBUILD initial output_write: \t" + str(time.time()) + "\n")
		status, output = commands.getstatusoutput('./make.sh uf output_write')
		timefile.write("PROVBUILD end initial output_write: \t" + str(time.time()) + "\n")

		return render_template('provbuild.html', 
		 					user_file=user_file.filename, 
		 					message="Initial Done", 
		 					content=open(user_file.filename, 'r').read(), 
		 					status=status, 
		 					result=open("result.txt", "r").read(),
		 					output=output, 
		 					provscript=stripComments(open("ProvScript.py", "r").read().split("# This is the parameter setup part", 1)[1]))

@app.route("/update", methods=['POST'])
def update():
	file = open("record-time/session.txt", "r") 
	info = file.readline().split(":")
	username = info[0]
	filename = info[1] 

	if not request.form['func_var']: 
		return render_template('provbuild.html', 
			user_file=filename, 
			message="unable to execute search -- no variable or function name", 
			content=session['content'], 
			status="", 
			result=open("result.txt", "r").read(),
			output="Please enter a variable or function name and click the 'search' button to generate a ProvScript.", 
			provscript="Please enter a variable or function name and click the 'search' button to generate a ProvScript.")	

	ret = request.form['func_var']
	file = open("record-time/session.txt", "a") 
	command = "./make.sh "
	if ret == 'function': 
		command += "uf " + request.form['func_var_text'] + " "
		file.write(":f:" + request.form['func_var_text'])
	elif ret == 'variable': 
		command += "uv " + request.form['func_var_text'] + " "
		file.write(":v:" + request.form['func_var_text'])

	
	print 'update ' + filename + ": " + command
	timefile = open("record-time/time.txt", "a")
	timefile.write("PROVBUILD start update: \t" + str(time.time())  + "\n")
	status, output = commands.getstatusoutput(command)
	timefile.write("PROVBUILD end update: \t" + str(time.time())  + "\n")

	return render_template('provbuild.html', 
					user_file=filename, 
					message="Search Done: " + request.form['func_var_text'],
					content=open(filename, 'r').read(), 
					status=status, 
					result=open("result.txt", "r").read(),
					output=output, 
					provscript=stripComments(open("ProvScript.py", "r").read().split("# This is the parameter setup part", 1)[1]))

@app.route("/runupdate", methods=['POST'])
def runupdate():
	file = open("record-time/session.txt", "r") 
	info = file.readline().split(":")
	username = info[0]
	filename = info[1] 
	fvtype = info[-2]
	fvname = info[-1]

	f = open('ProvScript.py', 'w')
	code = request.form['provscript'].replace("<br>", "\n").replace("<div>", "\n").replace("</div>", "\n")
	finalcode = cleanhtml(code)
	finalcode = finalcode.replace("&gt;", ">").replace("&lt;", "<")
	f.write(finalcode)
	f.close()

	# execute ProvScript.py
	print 'run ProvScript.py: ' + './make.sh d' 
	timefile = open("record-time/time.txt", "a")
	timefile.write("PROVBUILD start runupdate: \t" + str(time.time())  + "\n")
	status, output = commands.getstatusoutput('./make.sh d')
	print(status)
	print(output)
	errorflag = 0
	while status != 0:
		timefile.write("PROVBUILD end runupdate (need regeneration): \t" + str(time.time())  + "\n")
		if "NameError" in output and "is not defined" in output:
			lines = output.split('\n')
	        	funcname = getFuncname(lines[-1])

	        	print 'regenerate ProvScript.py: ' + './make.sh g ' + funcname
	        	timefile = open("record-time/time.txt", "a")
	        	timefile.write("PROVBUILD start regenerate: \t" + str(time.time())  + "\n")
	        	status, output = commands.getstatusoutput('./make.sh g ' + funcname)
	        	timefile.write("PROVBUILD end regenerate: \t" + str(time.time())  + "\n")
	        	if "UNFOUND" in output:
	        		errorflag = 1
	        		break

	        	timefile.write("PROVBUILD start runupdate: \t" + str(time.time())  + "\n")
	        	status, output = commands.getstatusoutput('./make.sh d')
        	else: 
        		errorflag = 1
			break

	timefile.write("PROVBUILD end runupdate: \t" + str(time.time())  + "\n")
	if errorflag == 0:
		return render_template('provbuild.html', 
						user_file=filename, 
						message="Execute Done", 
						content=open(filename, 'r').read(), 
						status=status, 
						result=open("result.txt", "r").read(),
						output=output, 
						provscript=stripComments(open("ProvScript.py", "r").read()))
	else:
		return render_template('provbuild.html', 
						user_file=filename, 
						message="Unknown Error", 
						content=open(filename, 'r').read(), 
						status=status, 
						result="",
						output=output, 
						provscript="Unknown Error")




@app.route("/merge", methods=['POST'])
def merge():
	# update merge time
	print 'merge: ' + './make.sh m'
	timefile = open("record-time/time.txt", "a")
	timefile.write("PROVBUILD start merge: \t" + str(time.time()) + "\n")
	status, output = commands.getstatusoutput('./make.sh m')
	timefile.write("PROVBUILD end merge: \t" + str(time.time()) + "\n")

	file = open("record-time/session.txt", "r") 
	info = file.readline().split(":")
	username = info[0]
	filename = info[1] 
	# merge output - new script
	newfilename = "new-" + filename

	# # keep user's record in ./results/ directory
	# commands.getstatusoutput ('cp ' + 'new-' + filename + ' ' + './Task-results/' + username + '-' + filename)

	# keep the current script for second try
	commands.getstatusoutput ('cp ' + 'new-' + filename + ' ' + filename)
	commands.getstatusoutput ('rm ' + 'new-' + filename)

	# generate provenance for new file
	print 'now we generate new provenance'
	print 'run ' + filename + ": " + './make.sh r ' + filename
	timefile = open("record-time/time.txt", "a")
	timefile.write("PROVBUILD start another run: \t" + str(time.time()) + "\n")
	status, output = commands.getstatusoutput('./make.sh r ' + filename)
	timefile.write("PROVBUILD end another run: \t" + str(time.time()) + "\n")


	newfile = open(filename, "r") 
	return render_template('provbuild.html', 
						user_file=filename, 
						message="Merge Done", 
						content=open(filename, 'r').read(),
						status=status, 
						result=open("result.txt", "r").read(),
						output=output, 
						provscript="Please enter a variable or function name and click the 'search' button to generate a ProvScript.")

@app.route("/provfinish", methods=['POST'])
def provfinish():
	# update finish time
	timefile = open("record-time/time.txt", "a")
	timefile.write("PROVBUILD finish: \t" + str(time.time())  + "\n")
	timefile.write("--------------------------------------\n")

	file = open("record-time/session.txt", "r") 
	info = file.readline().split(":")
	username = info[0]
	filename = info[1] 

	# keep the user's script and recall the script for next user
	commands.getstatusoutput ('mv ' + filename + ' ' + './Task-results/' + username + '-' + filename)
	commands.getstatusoutput ('mv ./record-time/time.txt ./Task-time/' + username  + '-' + filename + '-provtime.txt')
	# commands.getstatusoutput ('rm ' + filename)
	# commands.getstatusoutput ('cp ' + './examplebackup/' + filename + ' ' + filename)

	return render_template('index.html')

@app.route("/")
def main():
	open('result.txt', 'w').close()
	return render_template('index.html')

if __name__ == "__main__":
	url = "http://127.0.0.1:5000"
	threading.Timer(1.25, lambda: webbrowser.open(url)).start()
	app.run()
