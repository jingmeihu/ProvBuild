from __future__ import print_function

import requests
import json
import os
import sys
import pickle
import signal
import shutil

# make a new directory to store the dataset
# (if one doesn't exist)
storage_path = "./dataverse_data"

class TimeoutException(Exception):   # Custom exception class
	pass

def timeout_handler(signum, frame):   # Custom signal handler
	raise TimeoutException

# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

if not os.path.exists(storage_path):   
	os.makedirs(storage_path)

with open('python_dois.txt', 'r') as myfile:
	content = myfile.readlines()

content = [x.strip() for x in content] 

for i in content:
	# start the timer. Once 60 seconds are over, a SIGALRM signal is sent.
	signal.alarm(60)
	try:
		print(i)
		# get DOI from file
		doi = i
		dataverse_key = "3b930718-55c3-420f-9ab1-82f0f720c194" # example: "3b0777ab-4af9-4b3a-971e-5c84ac75926b"

		try:
			# query the dataverse API for all the files in a dataverse
			files = requests.get("https://dataverse.harvard.edu/api/datasets/:persistentId",
								 params= {"persistentId": doi, "key": dataverse_key})\
								 .json()['data']['latestVersion']['files']
		except:
			continue

		# convert DOI into a friendly directory name by replacing slashes and colons
		doi_direct = storage_path + '/' + doi.replace("/", "-").replace(":", "--")
		#print(doi_direct, end='')

		# make a new directory to store the dataset
		if not os.path.exists(doi_direct):   
			os.makedirs(doi_direct)

		# for each file result
		for file in files:
			# parse the filename and fileid 
			filename = file['dataFile']['filename']
			fileid = file['dataFile']['id']

			# query the API for the file contents
			response = requests.get("https://dataverse.harvard.edu/api/access/datafile/" + str(fileid),
									params={"key": dataverse_key})

			# write the response to correctly-named file in the dataset directory
			with open(doi_direct + "/" + filename, 'w') as handle:
				handle.write(response.content)

		# print out the dataset directory name for the shell script
		print(doi_direct, end='')
	except TimeoutException:
		# cleanup the directory
		shutil.rmtree(doi_direct)
		continue # continue the for loop if downloading takes more than 60 seconds
	else:
		# Reset the alarm
		signal.alarm(0)