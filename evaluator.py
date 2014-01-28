# coding: utf8

import json
import os
import sys


version = sys.argv[1]


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
			options = [(int(i.split("-")[0]),int(i.split("-")[1])) for i in line.strip().split(" ")]
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




def evaluator():
    tmp_file = open('tests_results.txt')
    if os.path.exists('grades.txt'):
        raise Exception('Ya existe el archivo: grades.txt')
        
    result = open('grades.txt', 'w')   
    tests= json.load(tmp_file)
    
    gs = {}
    
    for i in sorted(tests):
        sol = open(os.path.join( "generated", version ,u"TestSolution-" + str(i) + u".txt"))
        f = read_evaluate_test(sol)
        gs[tests[i]["test"]["student_id"]] = (evaluate_test(result, f, tests[i]["test"], tests[i]["warnings"]))
        
    result.close()

    
def read_evaluate_test(file_test):
    
    file_test = file_test.readlines()
    f = []    
    
    for i in file_test:
        f_i = i.strip()                   
        if f_i:
            f.append(int(f_i))
    
    return f
    
    
def evaluate_test(result, answers, test, warnings):
 
    g = 0
    
    uctys = set()    
    
    for w in warnings:
        uctys.add(w["question"])
        
    if warnings:
        print("STUDENT: {0} ({1})".format(test["student_id"], test["test_id"]))
    
    for i in range(len(answers)):
        if i in uctys:
            print(u"Ambigüedad en la pregunta {0}".format(i))
            print(u"  La respuesta correcta era: {0}".format(answers[i]))
            while 1:
                r = raw_input(u"  Aceptar respuesta? ([s]í / [n]o): ")
                if r == 's':
                    g += 1
                    break
                elif r == 'n':
                    break
                
        elif answers[i] == test["questions"][str(i+1)]["answers"][0]:
            g += 1
            
    result.write(u'{0}: {1}\n'.format(test["student_id"], g))
            
    return g
            
evaluator()
            
