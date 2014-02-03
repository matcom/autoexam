#coding: utf-8
from autotest import TestScanner, ImageSource
from scanresults import *
import cv2
import pprint
import pickle
import beep
import json
import os

#Get system camera in index 0
source = ImageSource(0)
w,h = source.get_size()
#Set document processing parameters and initialize scanner
scanner = TestScanner(w, h, "testslayout.json", show_image=True, single_selection=True, answers_id = [0,1,2,3,4,5,6,7,8,9])

tests = {}
#While user does not press the q key
while cv2.waitKey(1) & 0xFF != ord('q'):    
    #Get the scan report of the source image    
    report = scanner.scan(source)   
    #if test recognized OK
    if report.success:
        if not report.test.id in tests:
            beep.beep()
            tests[report.test.id] = report.test
            print "Student:",unicode(report.test.student_id).encode("utf8")
            print "Warnings:"
            for w in report.test.warnings: print "\t",w    	
    #if recognition went wrong print the reasons
    else:
        for e in [x for x in report.errors if isinstance(x,QuestionError)]: # in this case only the question errors
    		print e


scanner.finalize()
source.release()

#dummy test
tests[1] = Test(1,1,{22:Question(22,4,True,[2,1,6]), 23:Question(23,4,False,[2])},[Warning(23,2,WarningTypes.UNCERTANTY), Warning(22,[1,0],WarningTypes.MULT_SELECTION)])
#dump_single(tests[34])
for (k,v) in tests.items():
    print unicode(v).encode("utf8")

dump(tests,"tests_results.json")

print "%d exams stored..." % len(tests)

cv2.waitKey()