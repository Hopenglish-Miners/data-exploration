import json
import sys,getopt,codecs
import numpy as np
import pandas as pd
import xlsxwriter
from pandas.io.json import json_normalize

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


def getAllStudentBehavior(ifile1, ifile2):
	loadfile = []
	all_student_behavior = []
	loadfile.append(ifile1)
	loadfile.append(ifile2)

	for file in loadfile:
		with open(file) as data_file:
			all_student_behavior.append(json.load(data_file))
	return all_student_behavior


def getVideoData(ifile):
	with open(ifile) as data_file:
		video_data = json.load(data_file)
	return video_data


def prepDataForAnalysisWithVideoSections(studentBehavior, videoData):
	final = []

	for s in studentBehavior:
		for sb in s:
			for vid in sb['chosenVideo']:
				section = 0
				for ls in sb['listenScore']:
					if ls['postId'] == vid:
						section += 1
						result = {
						'section': section,
						'postId': vid,
						'score': ls['score'],
						'user': int(sb['memberId'])
						}
						final.append(result)
	return final


def prepDataForAnalysisWithoutVideoSections(studentBehavior, videoData):
	final = []
	count = 0
	vocabCount = 0
	listenScore = []

	for s in studentBehavior:
		for sb in s:
			for vid in sb['chosenVideo']:
				vocabCount = 0
				count = 0
				listenScore = []
				for v in videoData:
					if int(vid) == int(v['postId']):
						for w in v['wordList'].split(','):
							count += 1
				for ls in sb['listenScore']:
					if int(ls['postId']) == int(vid):
						listenScore.append(ls)
				for vl in sb['vocabularyList']:
					if int(vid) ==  int(vl['postId']):
						vocabCount += 1

				result = {
				'postId': vid,
				'listenScore': listenScore,
				'user': int(sb['memberId']),
				'vocab_list_count': vocabCount,
				'video_vocab_count': count - 1
				}
				final.append(result)
			
	return final


def loadExistingPrepData(ifile, ifile2):
	with open(ifile) as data_file:
		prep1 = json.load(data_file)

	with open(ifile2) as data_file:
		prep2 = json.load(data_file)

	return [prep1, prep2]


def listenScoreRange(dl):
	if dl < -1: return '<-1'
	elif dl == -1: return 'Incomplete'
	elif dl == 0: return '0'
	elif 1 <= dl <= 49: return '1-49'
	elif 49 < dl <= 59: return '50-59'
	elif 59 < dl <= 62: return '60-62'
	elif 62 < dl <= 66: return '63-66'
	elif 66 < dl <= 69: return '67-69'
	elif 69 < dl <= 72: return '70-72'
	elif 72 < dl <= 76: return '73-76'
	elif 76 < dl <= 79: return '77-79'
	elif 79 < dl <= 84: return '80-84'
	elif 84 < dl <= 89: return '85-89'
	elif 89 < dl <= 100: return '90-100'
	elif dl > 100: return '>100'
	else: return 'None'


def wordCountRange(dl):
	if dl == 0: return '0'
	elif 1 <= dl <= 30: return '1-30'
	elif 30 < dl <= 60: return '31-60'
	else: return 'None'


def listenScoreStatsByPostID(preppedDataWithSection):
	"""
	DESCRIPTION: For each video (PostID), generate frequency listen scores based on score range
	REFERENCES:
	http://stackoverflow.com/questions/36723625/pandas-sql-case-statement-equivalent
	http://stackoverflow.com/questions/16349389/grouping-data-by-value-ranges
	http://stackoverflow.com/questions/25748683/python-pandas-sum-dataframe-rows-for-given-columns
	http://stackoverflow.com/questions/15262134/apply-different-functions-to-different-items-in-group-object-python-pandas
	#df['totals'] = df.sum(axis=1) totals per column
	"""
	df = pd.DataFrame.from_records(preppedDataWithSection)
	df['score_range'] = df['score'].map(listenScoreRange)
	results = df.groupby(['postId', 'score_range']).size()
	return results.unstack()


def listenScoreStatsByPostIDAndSection(preppedDataWithSection):
	df = pd.DataFrame.from_records(preppedDataWithSection)
	df['score_range'] = df['score'].map(listenScoreRange)
	results = df.groupby(['postId', 'section', 'score_range']).size()
	return results.unstack()


def vocabStatsByPostIDAndScoreRange(preppedDataWithoutSection):
	"""
	http://stackoverflow.com/questions/30482071/how-to-calculate-mean-values-grouped-on-another-column-in-pandas
	http://pandas.pydata.org/pandas-docs/version/0.18.1/generated/pandas.io.json.json_normalize.html
	http://chrisalbon.com/python/pandas_apply_operations_to_groups.html
	"""
	results = json_normalize(preppedDataWithoutSection, 'listenScore', ['user', 'vocab_list_count', 'video_vocab_count'])
	results['score_range'] = results['score'].mean().map(listenScoreRange)
	#results['avg_words_saved'] = ((results['vocab_list_count'] / results['video_vocab_count']) * 100).map(wordCountRange)
	grpResults = results.groupby(['postId', 'score_range'])['vocab_list_count'].size()
	return grpResults.unstack()


def listenScoreStatsbyUser():
	print 'to be implemented'
	#results = json_normalize(preppedDataWithoutSection, 'listenScore', ['user', 'vocab_list_count', 'video_vocab_count'])
	#return results.groupby(['user','postId'], as_index = False)['score'].mean()

   
def main(argv):
	try:
		ifile = ''
		ifile2 = ''
		ifile3 = ''
		ofile = ''
		opts, args = getopt.getopt(argv, "", ("ifile=","ifile2=","ifile3=","ofile="))
				
		for opt,arg in opts:
			if opt == '--ifile':
				ifile = arg
			if opt == '--ifile2':
				ifile2 = arg
			if opt == '--ifile3':
				ifile3 = arg
			if opt == '--ofile':
				ofile = arg

		pd.set_option("display.max_rows", 400000)
		pd.set_option("display.max_columns", 1000)


		"""
		PREP DATA
		python main.py --ifile files/studentBehaviorInfo_1.json --ifile2 files/studentBehaviorInfo_2.json --ifile3 files/videoDataInfo.json  > stats/prepped.json
		"""
		#print "Prepping.."
		#student_data = getAllStudentBehavior(ifile, ifile2)
		#video_data = getVideoData(ifile3)

		#prepped_with_vid_sections = prepDataForAnalysisWithVideoSections(student_data, video_data)
		#print json.dumps(prepped_with_vid_sections, indent = 4)

		#prepped_without_vid_sections = prepDataForAnalysisWithoutVideoSections(student_data, video_data)
		#print json.dumps(prepped_without_vid_sections, indent = 4)


		"""
		LOAD EXISTING PREP DATA
		:ifile: prepped without section
		:ifile2: prepped with section
		"""
		print "Loading data.."
		loaded = loadExistingPrepData(ifile, ifile2)


		"""
		GENERATE STATS
		PARAMS: either from loaded data or prepped data
		"""
		#print "Generating listenScoreStatsByPostID.."
		#print listenScoreStatsByPostID(loaded[1])

		#print "Generating listenScoreStatsByPostIDAndSection.."
		#print listenScoreStatsByPostIDAndSection(loaded[1])

		print "Generating vocabStatsByPostIDAndScoreRange.."
		print vocabStatsByPostIDAndScoreRange(loaded[0])

	except arg:
		print 'Arguments parser error ' + arg
	finally:
		print 'Done...'


if __name__ == '__main__':
	main(sys.argv[1:])
