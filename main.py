import json
import sys,getopt,codecs
import numpy as np
import pandas as pd
import xlsxwriter
from pandas.io.json import json_normalize

"""
REFERENCES
http://stackoverflow.com/questions/36723625/pandas-sql-case-statement-equivalent
http://stackoverflow.com/questions/16349389/grouping-data-by-value-ranges
http://stackoverflow.com/questions/25748683/python-pandas-sum-dataframe-rows-for-given-columns
http://stackoverflow.com/questions/15262134/apply-different-functions-to-different-items-in-group-object-python-pandas
#df['totals'] = df.sum(axis=1) totals per column
http://stackoverflow.com/questions/30482071/how-to-calculate-mean-values-grouped-on-another-column-in-pandas
http://pandas.pydata.org/pandas-docs/version/0.18.1/generated/pandas.io.json.json_normalize.html
http://chrisalbon.com/python/pandas_apply_operations_to_groups.html
http://manishamde.github.io/blog/2013/03/07/pandas-and-python-top-10/
http://www.gregreda.com/2013/10/26/working-with-pandas-dataframes/
sort by field: f.sort_values(by=["c1","c2"], ascending=[False, True])
"""

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


def getMissingVideoVocab(ifile, ifile2):
	final = []

	with open(ifile) as data_file:
		existing_video_data = json.load(data_file)

	with open(ifile2) as data_file:
		new_video_data = json.load(data_file)

	for x, y in zip(existing_video_data, new_video_data):
		if x['postId'] == y['postId']:
			x['wordList'] = y['wordList']
			final.append(x)
	return final


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

	for s in studentBehavior:
		for sb in s:
			for vid in sb['chosenVideo']:
				vocabCount = 0
				video_word_count = 0
				count_incomplete = 0
				all_scores = []
				actual_grade = []
				for v in videoData:
					if int(vid) == int(v['postId']):
						for w in v['wordList']:
							video_word_count += 1
				for ls in sb['listenScore']:
					if int(ls['postId']) == int(vid):
						all_scores.append(int(ls['score']))
				for score in all_scores:
					if score >= 0:
						actual_grade.append(score)
					elif score == -1:
						count_incomplete += 1
				for vl in sb['vocabularyList']:
					if int(vid) ==  int(vl['postId']):
						vocabCount += 1
                
				result = {
				'postId': vid,
				'avg_score': np.mean(actual_grade) if len(actual_grade) > 0 else 'NaN', #avg scores that student has a grade for to see performance so far
				'avg_incomplete': (float(count_incomplete)/float(len(all_scores))) if len(all_scores) > 0 else 'NaN', #avg incomplete sections (count(-1)/total scores)
				'user': int(sb['memberId']),
				'avg_words_saved': (float(vocabCount) / float(video_word_count)), #proportion of num of words saved from entire video vocab
				'video_vocab_count': video_word_count
				}
				#can add max score, min, # of scores which would give the # of video sections
				final.append(result)
			
	return final


def loadExistingPreppedData(ifile, ifile2):
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


def listenScoreStatsByPostID(preppedDataWithSection):
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
	print 'to be implemented'
	

def listenScoreStatsbyUser():
	print 'to be implemented'


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
		#print json.dumps(getMissingVideoVocab(ifile, ifile2), indent = 4)
		#student_data = getAllStudentBehavior(ifile, ifile2)
		#video_data = getVideoData(ifile3)

		#prepped_with_vid_sections = prepDataForAnalysisWithVideoSections(student_data, video_data)
		#print json.dumps(prepped_with_vid_sections, indent = 4)

		#prepped_without_vid_sections = prepDataForAnalysisWithoutVideoSections(student_data, video_data)
		#print json.dumps(prepped_without_vid_sections, indent = 4)


		"""
		LOAD EXISTING PREPPED DATA
		:ifile: prepped without section
		:ifile2: prepped with section
		"""
		print "Loading data.."
		loaded = loadExistingPreppedData(ifile, ifile2)


		"""
		GENERATE STATS
		PARAMS: either from loaded data or prepped data
		"""
		#print "Generating listenScoreStatsByPostID.."
		#print listenScoreStatsByPostID(loaded[1])

		#print "Generating listenScoreStatsByPostIDAndSection.."
		#print listenScoreStatsByPostIDAndSection(loaded[1])

		#print "Generating vocabStatsByPostIDAndScoreRange.."
		#print vocabStatsByPostIDAndScoreRange(loaded[0])

	except arg:
		print 'Arguments parser error ' + arg
	finally:
		print 'Done...'


if __name__ == '__main__':
	main(sys.argv[1:])
