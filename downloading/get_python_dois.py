import requests
import json
import re
import os

# defining some constants
python_file_query = "fileType:python-script"
dataverse_key = "" # please enter your dataverse API here

# initialize variables to store current state of scraping
page_num = 0
python_dois = []
#  keep requesting until the API returns fewer than 1000 results
while True:
	print("Requesting page {} from API...".format(page_num))
	# query the API for 1000 results
	myresults = requests.get("https://dataverse.harvard.edu/api/search/",
							 params= {"q": python_file_query, "type": "file",
							 "key": dataverse_key,
							 "start": str(1000 * page_num),
							 "per_page": str(1000)}).json()['data']['items']

	print("Parsing results from page {}...".format(page_num))
	
	# iterate through results, recording dataset_citations
	for myresult in myresults:
		# citation = myresult['dataset_citation']
		# if '2018' in citation:
		# extract the DOI (if any) from the result
		# doi_match = re.search("(doi:[^,]*)", myresult['dataset_citation'])
		doi_match2 = re.search("https://doi.org/([^,]*),", myresult['dataset_citation'])
		# if doi_match:
		# 	python_dois.append(doi_match.group(1) + '\n')
		if doi_match2:
			python_dois.append('doi:' + doi_match2.group(1) + '\n')


	# if fewer than 1000 results were returned; we must have reached the end
	if len(myresults) < 1000:
		print("Reached last page of results. Done.")
		break
	page_num += 1

# remove duplicate DOIs
python_dois = list(set(python_dois))

# remove old output file if one exists
if os.path.exists('python_dois.txt'):   
	os.remove('python_dois.txt')

# write dois to file, one-per-line
with open('python_dois.txt', 'a') as myfile:
	map(myfile.write, python_dois) 