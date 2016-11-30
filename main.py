import json
import sys,getopt,codecs
import numpy as np
import pandas as pd

def videoCSVToJSON(ifile):
	"""
	convert videoDataInfo.csv to json
	"""
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

def listen_scores_overall_stats(ifile1, ifile2):
	"""
	generate overall stats for listen scores
	"""
	listenScores = []
	loadfile = []
	loadfile.append(ifile1)
	loadfile.append(ifile2)

	for f in loadfile:
		with open(f) as data_file:
			all_data = json.load(data_file)
	
	for b in all_data:
		for s in b['listenScore']:
			listenScores.append(s)
	
	scores = pd.DataFrame.from_records(listenScores)
	grouped = scores.groupby('postId')
	return grouped.describe()

   
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
		print listen_scores_overall_stats(ifile, ifile2)

	except arg:
		print 'Arguments parser error ' + arg
	finally:
		print 'Done...'


if __name__ == '__main__':
	main(sys.argv[1:])