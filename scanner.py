#coding: utf-8
from autotest import TestScanner, ImageSource, QuestionError
import cv2
import pprint
import pickle
import beep
import json
import os

#Get system camera in index 0
source = ImageSource(1)
w,h = source.get_size()
print w,h
#Set document processing parameters and initialize scanner
scanner = TestScanner(w, h, show_image=True, single_selection=True, answers_id = [0,1,2,3,4,5,6,7,8,9])

tests = {}
#While user does not press the q key
while cv2.waitKey(1) & 0xFF != ord('q'):    
    #Get the scan report of the source image    
    report = scanner.scan(source)   
    #if test recognized OK
    if report.success:
        if not report.test.test_id in tests:
            beep.beep()
            tests[report.test.test_id] = (report.test, report.warnings)
            print "Student:",unicode(report.test.student_id).encode("utf8")
            print "Warnings:"
            for w in report.warnings: print "\t",w    	
    #if recognition went wrong print the reasons
    else:
        for e in [x for x in report.errors if isinstance(x,QuestionError)]: # in this case only the question errors
    		print e


scanner.finalize()
source.release()

for (k,v) in tests.items():
    print unicode(v[0]).encode("utf8")

to_serialize = {}

if os.path.exists('tests_results.txt'):
    f = open('tests_results.txt', 'r')
    current = json.loads(f.read())
    f.close()

    for k,v in current.items():
        k = int(k)
        print('Restoring previous test: {0}'.format(k))
        to_serialize[k] = v

for (k,v) in tests.items():
    test, warnings = v
    print('Saving test: {0}'.format(k))
    to_serialize[k]={'test': test.to_dict(), 'warnings': [w.to_dict() for w in warnings]}

f = file("tests_results.txt",'w') 
json.dump(to_serialize, f) 
f.close()

print "%d exams stored..." % len(to_serialize)

cv2.waitKey()