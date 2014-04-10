# coding: utf8

import json
import os
import sys


version = sys.argv[1]


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
            