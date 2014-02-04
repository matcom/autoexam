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
w, h = source.get_size()
#Set document processing parameters and initialize scanner
scanner = TestScanner(w, h, "generated/v1/Order.txt", show_image=True)

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
            print "Test ID:", unicode(report.test.id).encode("utf8")
            for q in report.test.questions:
                print "%d%s -> %s"%(q.id,"m" if q.multiple else "s",q.answers)
            if len(report.test.warnings)>0:
                print "Warnings:"
                for w in report.test.warnings: print "\t", w    	
    #if recognition went wrong print the reasons
    else:
        for e in [x for x in report.errors if isinstance(x, QuestionError)]: # in this case only the question errors
            print e


scanner.finalize()
source.release()

dump(tests, "tests_results.json")

print "%d exams stored..." % len(tests)

cv2.waitKey()
