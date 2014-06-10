# coding: utf8

import json
import scanresults as sr

class QuestionGrader(object):
	
	def __init__(self,id_question,multiple,total_value,options_values):
		self.id_question = id_question
		self.multiple = multiple
		self.total_value = total_value
		self.options_values = options_values
		
	def getId(self):
		return self.id_question
		
	def isMultiple(self):
		return False
		
	def getTotalValue(self):
		return self.total_value
		
	def getNumberOfOptions(self):
		return len(options_values)

	def getOptionValue(self,option):
		return self.options_values[option]
		
	def evaluate(self,answers):
		value = 0
		count = 0
		for a in answers:
			if a[1]:
				count += 1
				if (not self.isMultiple) and (count>1):
					return 0
				value += self.getOptionValue(a[0])[0]
			else:
				value += self.getOptionValue(a[0])[1]
		return value
		
		
class Grader(object):
	
	def __init__(self,id_exam):
		self.id_exam = id_exam
		self.questions = {}
		
	def addQuestionGrader(self,question):
		self.questions[question.getId()] = question
		
	def getQuestionGrader(self,id_question):
		return self.questions[id_question]

def parse_grader_sheet(grader_sheet_file):
	gs_file = open(grader_sheet_file,"rb")
	id_exam = (gs_file.readline()).strip()
	grader = Grader(id_exam)
	blank_line = True
	id_question_line = False
	id_question = None
	multiple = None
	total_line = False
	total = None
	options_line = False
	options = None
	for line in gs_file:
		if options_line:
			options_line = False
			blank_line = True
			options = [(int(i.split(":")[0]),int(i.split(":")[1])) for i in line.strip().split(" ")]
			grader.addQuestionGrader(QuestionGrader(id_question,multiple,total,options))
		if total_line:
			total_line = False
			options_line = True
			total = int(line.strip()[6:])
		if id_question_line:
			id_question_line = False
			total_line = True
			temp = line.strip()
			multiple = temp.endswith("*")
			id_question = temp[:-1] if multiple else temp
		if blank_line and line.strip()=='':
			blank_line = False
			id_question_line = True
	return grader

def evaluate(grader_sheet_file,results_json_file):
	grader = parse_grader_sheet(grader_sheet_file)
	tests_scans = sr.parse(results_json_file)
	grades = {}
	for test_id, exam in tests_scans.items():
		if str(grader.id_exam) == str(exam.exam_id):
			total_grade = 0
			q_grades = {}
			for question in exam.questions:
				answers = [(i, i in question.answers) for i in range(0,question.total_answers)]
				q_grade = grader.getQuestionGrader(str(question.id)).evaluate(answers)
				total_grade += q_grade
				q_grades[str(question.id)]=q_grade
			grades[test_id]={"total_grade":total_grade,"questions_grades":q_grades}
		else:
			pass
	return grades


def main():
	import argparse
	parser = argparse.ArgumentParser(description='Autoexam evaluator')
	parser.add_argument("gradersheet", help="Gradersheet file")
	parser.add_argument("scansjson", help="Scans json file")
	parser.add_argument("resultsjson", help="Results json file")
	args = parser.parse_args()
	result = evaluate(args.gradersheet,args.scansjson)
	json.dump(result,open(args.resultsjson,"wb"))
	return 0

if __name__ == '__main__':
	main()