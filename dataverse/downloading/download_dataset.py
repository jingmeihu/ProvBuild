from __future__ import print_function

import requests
import json
import os
import sys
import pickle

# make a new directory to store the dataset
# (if one doesn't exist)
storage_path = "./dataverse_data"

if not os.path.exists(storage_path):   
	os.makedirs(storage_path)

with open('python_dois_sub.txt', 'r') as myfile:
	content = myfile.readlines()

content = [x.strip() for x in content] 

for i in content:
	print(i)
	# get DOI from file
	doi = i
	dataverse_key = "22474fc6-e76b-4196-8249-41d8f0c0eeda" # example: "3b0777ab-4af9-4b3a-971e-5c84ac75926b"

	# query the dataverse API for all the files in a dataverse
	files = requests.get("https://dataverse.harvard.edu/api/datasets/:persistentId",
						 params= {"persistentId": doi, "key": dataverse_key})\
						 .json()['data']['latestVersion']['files']

	# convert DOI into a friendly directory name by replacing slashes and colons
	doi_direct = storage_path + '/' + doi.replace("/", "-").replace(":", "--")

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