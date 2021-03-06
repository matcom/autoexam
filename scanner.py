#coding: utf-8
from os.path import join, exists, dirname, abspath
from autotest import TestScanner, ImageSource
from os import makedirs, access
from evaluator import get_stats
from scanresults import *
import pprint
import pickle
import beep
import json
import cv2
import os

class Obj:
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            self.__setattr__(k,v)
    def __repr__(self):
        return str(self.__dict__)
    def __str__(self):
        return str(self.__dict__)

def parse_and_check_args():
    import argparse
    parser = argparse.ArgumentParser(description='Scan the test generated by autoexam.')
    parser.add_argument('exams_file', type=str,
                        help='the json file that describes each test. It is created by the exam generator.')
    parser.add_argument('-o','--outfile', type=str, default = "tests_results.json",
                        help='the file name to dump the scan results. If the file exists it will append the results.')
    parser.add_argument('-c','--cameras', type=int, nargs="+", default = [0],
                        help='the list of index of the cameras to be used to scan the tests.')
    parser.add_argument('-f','--folder', type=str, default = "",
                        help='the folder that includes all the images to scann.')
    parser.add_argument('-t','--time', type=float, default = 0.5,
                        help='time in seconds it takes to load the next image on the specified folder.')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='debug mode enabled')
    parser.add_argument('-a', '--autowrite', action='store_true', default=False,
                        help='update the scanner results file every time a document is scanned')
    #TODO: PLEASE REMOVE THIS AS SOON AS POSIBLE
    parser.add_argument('-p', '--poll', action='store_true', default=False,
                        help='if present the margins of the polls are used (REMOVE THIS OPTION PLZ).')
    args = parser.parse_args()

    args.outfile = abspath(args.outfile)

    if not exists(args.exams_file):
        print "The file '%s' does not exists."%args.exams_file
        return None
    #check if can create the output and write to it...
    if not access(dirname(args.outfile), os.W_OK):
        print "You dont have the permissions to write to the file '%s'."%args.outfile
        return None
    #if exists then check if is valid json...
    if exists(args.outfile):
        f = open(args.outfile)
        try:
            json.loads(f.read())
        except Exception, e:
            print "The file '%s' is not a valid json."%args.outfile
            return None
        f.close()

    return args

def main():
    args = parse_and_check_args()
    if not args: return 1

    #Get system camera in index 0
    source = ImageSource(args.cameras if args.folder=="" else args.folder, args.time)
    w, h = source.get_size()
    #Set document processing parameters and initialize scanner
    scanner = TestScanner(w, h, args.exams_file, show_image=True, double_check=True, debug = args.debug, poll = args.poll)

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
                for i, q in enumerate(report.test.questions):
                    print "%d. %s"%(i+1, q)
                if len(report.test.warnings)>0:
                    print "Warnings:"
                    for w in report.test.warnings:
                        print "\t", w
                #this method appends the test results if the file exists...
                if args.autowrite:
                    dump(tests, args.outfile, overwrite = False)
                    stats = get_stats(args.outfile)
                    stats_path = os.path.join(os.path.dirname(os.path.realpath(args.outfile)), "stats.json")
                    with open(stats_path,"wb") as stats_file:
                        json.dump(stats,stats_file,indent=4)

                    print "Exam file updated..."
            else:
                print "The test '%d' was already scanned."%report.test.id
        #if recognition went wrong print the reasons
        else:
            if report.test and report.test.id and report.test.id in tests:
                print "The test '%d' was already scanned."%report.test.id
            else:
                # show only the question detection errors and the
                # errors in the format of the qrcodes
                for e in [x for x in report.errors
                            if isinstance(x, QuestionError) or
                            (isinstance(x, QrcodeError) and x.err_type == QRCodeErrorTypes.FORMAT) or args.debug ]:
                    print e

    scanner.finalize()
    source.release()

    #this method appends the test results if the file exists...
    dump(tests, args.outfile, overwrite = False)

    print "%d exams stored..." % len(tests)

    cv2.waitKey()

if __name__ == '__main__':
    main()
