import json
import sys,getopt,codecs
import numpy as np
import pandas as pd

def videoCSVToJSON(ifile):
	videos = []
	inputFile = codecs.open(ifile, 'r', encoding = "utf-8")

	for row in inputFile:
		row = row.split(',',6)
		videos.append({
			'id':row[0], 
			'postId':row[1],
			'wordLevel':row[2],
			'videoSpeed':row[3],
			'subtitleLengthRatio':row[4],
			'sectionLength':row[5],
			'wordList':row[6]
			})
	inputFile.close()
	return videos[1:]

def loadJSONFiles(ifile1, ifile2):
	loadfile = []
	loadfile.append(ifile1)
	loadfile.append(ifile2)

	for f in loadfile:
		with open(f) as data_file:
			all_data = json.load(data_file)
	return all_data

def getListenScores(all_data):
	listenScores = []
	
	for b in all_data:
		for s in b['listenScore']:
			listenScores.append(s)
	return listenScores

def listenScoresOverallStats(ifile1, ifile2):
	"""
	generate overall stats for listen scores
	"""
	all_data = loadJSONFiles(ifile1, ifile2)
	listenScores = getListenScores(all_data)
	all_scores = pd.DataFrame.from_records(listenScores)
	grouped = all_scores.groupby('postId')
	return grouped.describe()

def listen_score_range(dl):
	if dl < -1: return '< -1'
	elif dl == -1: return 'Incomplete'
	elif 0 <= dl <= 30: return '0-30'
	elif 30 < dl <= 60: return '30-60'
	elif 60 < dl <= 80: return '60-80'
	elif 80 < dl <= 100: return '80-100'
	else: return 'None'

def listenScoreStats(ifile1, ifile2):
	"""
	DESCRIPTION: For each video, group listen scores based on range, could be more useful to group by section as well
	REFERENCES:
	http://stackoverflow.com/questions/36723625/pandas-sql-case-statement-equivalent
	http://stackoverflow.com/questions/16349389/grouping-data-by-value-ranges
	"""
	all_data = loadJSONFiles(ifile1, ifile2)
	listenScores = getListenScores(all_data)
	df = pd.DataFrame.from_records(listenScores)
	df['score_range'] = df['score'].map(listen_score_range)
	results = df.groupby(["postId","score_range"]).size()
	return results.unstack()
   
def main(argv):
	"""
	SAMPLE RUN: 
	python main.py --ifile files/studentBehaviorInfo_1.json --ifile2 files/studentBehaviorInfo_2.json > stats.json
	"""
	try:
		ifile = ''
		ifile2 = ''
		opts, args = getopt.getopt(argv, "", ("ifile=","ifile2="))
				
		for opt,arg in opts:
			if opt == '--ifile':
				ifile = arg
			if opt == '--ifile2':
				ifile2 = arg

		pd.set_option("display.max_rows", 5000)
		pd.set_option("display.max_columns", 500)
		print listenScoreStats(ifile, ifile2)

	except arg:
		print 'Arguments parser error ' + arg
	finally:
		print 'Done...'


if __name__ == '__main__':
	main(sys.argv[1:])