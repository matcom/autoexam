#coding: utf-8
import os
import cv2
import zbar
import numpy as np
import sys
import copy
import time
from scanresults import *

import math
import re

report = None
doc_parameters = {
    "debug": False, #Show images of all the recognition process
    "show_image": True, #if it is a camera it shows a window with the images, and if it is an image it shows the image #not in use
    "is_camera": False,
    "double_check": True, #Makes a double confirmation before to return a success report
    "marker_image": "latex/marker.png", #Image of the marker to use in the borders
    "answer_cols": 5, ##the number of questions per column, this value is fixed
    "marker_match_min_quality": 0.6, #threshold level to apply to the template matching results
    "marker_size": 0.25, #size of the marker with respect to the qrcode width
    #TODO try to recode this to use percent and not pixel units as they are now
    "qrcode_width": 100, #qrcode final width in pixels after perspective transformation
    "margin" : 60, #margin used to crop image after the rotation rectification
    "work_size": 800, #resolution of the smaller side of the image after rectification, like saying 1000p

    #---------------------------------------------REMOVE ALL OF THIS---------------------------------------------
    "poll": False, #if we are scanning a poll or not

    "p_answer_cols": 1, ##the number of questions per column, this value is fixed

    #padding between the answers area rectangle and the inner answers area (used to rectify any misalignment within the answer area)
    "p_up_margin": 0.13,
    "p_down_margin": 0.15,
    "p_left_margin": 0.2,
    "p_right_margin": 0.2,

    #padding between the rectangle with the selection cells and the inner cell area (used to rectify any misalignment within the answer selection rectangle)
    "p_cell_up_margin": 0.0,
    "p_cell_down_margin": 0.0,
    "p_cell_left_margin": 0.0,
    "p_cell_right_margin": 0.0,
    #-----------------------------------------------------------------------------------------------------------

    #padding between the answers area rectangle and the inner answers area (used to rectify any misalignment within the answer area)
    "up_margin": 0.0145,
    "down_margin": 0.012,
    "left_margin": 0.00,
    "right_margin": 0.00,

    #padding between the rectangle with the selection cells and the inner cell area (used to rectify any misalignment within the answer selection rectangle)
    "cell_up_margin": 0.05,
    "cell_down_margin": 0.05,
    "cell_left_margin": 0.72,
    "cell_right_margin": 0.05,

    "squares": False, #if it is a square or a circle
    "distance_threshold": 0.8, #threshold of the allowed distance between the selection boxes over the mean distance
    "aligned_threshold": 0.5, #threshold of the alignment allowed between the selection boxes over the mean displacement
    "circle_ratio_threshold": 0.4, #a perfect circle is of ratio 1.0, this number the max deviation from 1.0, it is w/h
    "circle_size_difference": 0.4, #the percent of the median size allowed
    "circle_aligment_percent": 1.0, #the percent over the radius that is allowed as a displacement over the median x coodinate
    "selection_box_padding":0.5, #padding used to select the inner area of the selection boxes
    "selection_circle_padding":0.35, #padding used to select the inner area of the selection circles
    "selection_threshold": 130, #threshold that is used to decide if the answer is selected based on the mean intensity range:[0,255]
    "selection_error": 30, #threshold around the selection_threshold that marks the uncertainty range:[0,255]
    "merge_size_factor": 1.2, #Size factor to decide if a merge is needed in the scattered squares
    #this is the parameter that cretaes most of the problems with the presision of the system
    "adaptative_threshold_size": 12, #size of the kernel in the adaptive threshold to highlight the circle, smaller makes it more sensitive
    "version": 1 #version control to reject invalid qrcodes
}

class TestScanner:
    def __init__(self, w, h, testsfile, **kw):
        for (k,v) in kw.items():
            doc_parameters[k]=v
        doc_parameters["scanner"] = QRScanner(w,h);
        marker_path = os.path.join(os.environ['AUTOEXAM_FOLDER'], doc_parameters["marker_image"])
        doc_parameters["loaded_marker"] = cv2.imread(marker_path,0)
        doc_parameters["init"] = True
        doc_parameters["tests"] = parse(testsfile)

        #---------------------REMOVE ALL THIS---------------------
        if doc_parameters["poll"]:
            doc_parameters["up_margin"] = doc_parameters["p_up_margin"]
            doc_parameters["down_margin"] = doc_parameters["p_down_margin"]
            doc_parameters["left_margin"] = doc_parameters["p_left_margin"]
            doc_parameters["right_margin"] = doc_parameters["p_right_margin"]

            doc_parameters["cell_up_margin"] = doc_parameters["p_cell_up_margin"]
            doc_parameters["cell_down_margin"] = doc_parameters["p_cell_down_margin"]
            doc_parameters["cell_left_margin"] = doc_parameters["p_cell_left_margin"]
            doc_parameters["cell_right_margin"] = doc_parameters["p_cell_right_margin"]

            doc_parameters["answer_cols"] = doc_parameters["p_answer_cols"]
        #---------------------------------------------------------


    def scan(self, source):
        return get_scan_report(source)

    def finalize(self):
        doc_parameters["scanner"] = None
        doc_parameters["loaded_marker"] = None
        doc_parameters["init"] = False
        cv2.destroyAllWindows()

def get_scan_report(source):
    if not doc_parameters["init"]: return Report()

    global report
    # do always a single check if it is not a camera
    if not doc_parameters["double_check"] or not doc_parameters['is_camera']:
        report = Report()
        frame = source.get_next()
        return get_image_report(frame)
    #if double check is enabled...
    first = None
    while True:
        if not first:
            report = Report()
            frame = source.get_next()
            first = get_image_report(frame)
        if not first.success:
            return first
        else:
            report = Report()
            frame = source.get_next()
            second = get_image_report(frame)
            if not second.success or second.test==first.test:
                return second
            else:
                first = second
                continue

def get_image_report(frame):
    scanner = doc_parameters.get("scanner")
    marker = doc_parameters.get("loaded_marker")
    #TODO reject blurred images
    # Set it to gray scale
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # make it binary
    image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 21, 5)
    # Scan for QRcodes
    qrcodes = scanner.get_qrcodes(image)
    # Check qrcode validity
    qr_is_ok, err_msg = qrcode_ok(qrcodes)
    if qr_is_ok:
        qrcode = qrcodes.pop()
        report.test = get_test_from_qrcode(qrcode)
        #paint the qrcode in white to lower the chances of getting wrong matches
        cv2.fillConvexPoly(image,np.int32([list(x) for x in qrcode.location]) ,(255))
        show_debug_image(image,"QR filled.")
        size = int(doc_parameters["marker_size"] * dist(qrcode.location[0],qrcode.location[1]));
        rotated, gray_image =  fix_rotation(qrcode.location, image, gray_image)
        #detect_lines(rotated) #Search for lines
        show_debug_image(rotated,"After rotation.")
        show_debug_image(gray_image,"Gray after rotation")
        small_marker = cv2.resize(marker,(size,size))
        markers = get_marker_positions(rotated, small_marker, doc_parameters["marker_match_min_quality"])
        if len(markers)==4 and rectangle_sort(markers,rotated):
            answer_area = perspective_transform(gray_image, markers)
            show_debug_image(answer_area,"All Answer area cropped.")
            cols = doc_parameters["answer_cols"]
            total_q = len(report.test.questions)
            rows = total_q/cols if total_q%cols==0 else (total_q/cols)+1

            #TODO make a parameter out of wish order to scan the tests
            answer_imgs = get_answer_images(answer_area, cols, rows, len(report.test.questions))
            question=0
            bad_data = False
            for img in answer_imgs:
                correct, selection = get_selections(img, report.test.questions[question], question)
                if correct:
                    report.test.questions[question].answers = selection
                else:
                    bad_data = True
                question+=1
            #TODO debug
            show_debug_image(answer_area,"Answer area marked.", False)

            if not bad_data:
                report.success = True
                return report

        else:
            report.errors.append(MarkersError())
    else:
        report.errors.append(err_msg)

    return report

#   exam id | test id | version
DATA_RE = re.compile(r'''[0-9]+\|[0-9]+\|[0-9]+''',re.UNICODE)

def qrcode_ok(qrcodes):
    if len(qrcodes)!=1:
        return False, QrcodeError()
    data = qrcodes[0].data
    #the qrcode matches the format
    if DATA_RE.match(data):
        version = int(data.split('|')[2])
        test_id = int(data.split('|')[1])
        exam_id = int(data.split('|')[0])
        #has the correct version
        if doc_parameters["version"]!=version:
            return False, QrcodeError(  err_type=QRCodeErrorTypes.FORMAT,
                                        msg = "The test was created with a different version of this software.")
        #the id is in the tests pool
        if test_id not in doc_parameters["tests"]:
            return False, QrcodeError(  err_type=QRCodeErrorTypes.FORMAT,
                                        msg = "The metadata of the test is not on the input file.")
        #get the test and check the if is has the correct exam id
        test = doc_parameters["tests"][test_id]
        if test.exam_id != exam_id:
            return False, QrcodeError(  err_type=QRCodeErrorTypes.FORMAT,
                                        msg = "The test is from the exam: %d and the metadata is for the exam: %d"%(exam_id,test.exam_id))
        return True, "Ok"
    else:
        return False, QrcodeError(  err_type=QRCodeErrorTypes.FORMAT,
                                    msg = "The QRCode has a wrong format")

def get_test_from_qrcode(qrcode):
    info = qrcode.data.split('|')
    test_id = int(info[1])
    return copy.deepcopy(doc_parameters["tests"][test_id])

class QRCode(object):
    """QRCode class"""
    def __init__(self, data, location):
        self.data = data
        self.location = list(location)

class QRScanner(object):
    """Zbar qrcode scanner wrapper class"""
    def __init__(self, width, height):
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')
        self.width = width
        self.height = height

    def get_qrcodes(self, image):
        zbar_img = self.cv2_to_zbar_image(image)
        self.scanner.scan(zbar_img)
        result=[]
        for symbol in zbar_img:
            if symbol.type!=zbar.Symbol.QRCODE: continue

            #TODO remove this sui fix
            fixed_data = symbol.data.decode("utf8").encode("shift_jis").decode("utf8")

            result.append(QRCode(fixed_data,symbol.location))
        del(zbar_img)
        return result

    def cv2_to_zbar_image(self, cv2_image):
        return zbar.Image(self.width, self.height, 'Y800',cv2_image.tostring())

def detect_lines(gray):
    #edges = cv2.Canny(gray,50,150,apertureSize = 3)
    edges = gray
    lines = cv2.HoughLines(edges,1.0,np.pi/200.0,850)
    color = cv2.cvtColor(edges,cv2.COLOR_GRAY2BGR)
    if not lines.any() or len(lines)==0: return
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(color,(x1,y1),(x2,y2),(0,0,255),2)

    show_debug_image(color,"lines")

def fix_rotation_with_perspective(qr_rect, image):
    """Fixes the rotation of the image using the qrcode rectangle. -> cv2.image"""
    qrcode_w = doc_parameters["qrcode_width"]
    margin = doc_parameters["margin"]
    pts1 = np.float32([list(x) for x in qr_rect])
    pts2 = np.float32([[margin,margin],[margin,qrcode_w+margin],[qrcode_w+margin,qrcode_w+margin],[qrcode_w+margin,margin]])

    w, h = image.shape[::-1]

    old_dist = dist(qr_rect[0],qr_rect[1])
    result_h = h*qrcode_w/old_dist
    result_w = w*qrcode_w/old_dist

    M = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(image, M, (int(result_w), int(result_h)))

    return result,((margin,margin), (margin,qrcode_w+margin), (qrcode_w+margin,qrcode_w+margin), (qrcode_w+margin,margin))

def fix_rotation(qr_rect, image, aux_image):
    """Fixes the rotation of the image using the qrcode rectangle. -> cv2.image"""
    actual_down = np.array( [   float(qr_rect[1][0]-qr_rect[0][0]) ,
                                float(qr_rect[1][1]-qr_rect[0][1]) ] )
    actual_down = actual_down/np.linalg.norm(actual_down)
    real_down = np.array([0,1])

    angle = np.arccos(np.dot(actual_down, real_down))

    if np.isnan(angle):
        if (actual_down == real_down).all(): angle = 0.0
        else: angle = np.pi

    if actual_down[0]>0: angle = 2*np.pi-angle
    #calculate the size of the borders to make it squared
    w, h = image.shape[::-1]
    if w>h:
        top, bott, left, right = (w-h)/2, (w-h)/2, 0, 0
    else:
        top, bott, left, right = (h-w)/2, (h-w)/2, 0, 0
    #add the borders
    bigger_img = cv2.copyMakeBorder(image,top,bott,left,right,cv2.BORDER_CONSTANT,value=[0,0,0])
    bigger_aux = cv2.copyMakeBorder(aux_image,top,bott,left,right,cv2.BORDER_CONSTANT,value=[0,0,0])
    #calculate the tramsformation
    w, h = bigger_img.shape[::-1]
    M = cv2.getRotationMatrix2D((w/2,h/2),180*angle/np.pi,1.0)
    #TODO o not use the variable margin here, try to find the real w, h that accounts for the new transformation
    #margin = doc_parameters["margin"]
    return ( cv2.warpAffine(bigger_img,M,(w,h)), cv2.warpAffine(bigger_aux,M,(w,h)) )

def get_marker_positions(image, marker,threshold):
    """Finds the 4 markers that surround the answer area in the image. -> list of tuples"""
    res = cv2.matchTemplate(image,marker,cv2.TM_CCOEFF_NORMED)
    if doc_parameters["debug"]: cv2.imshow("Template Matching",res)
    loc = np.where( res >= threshold)
    w, h = marker.shape[::-1]
    points = [ (pt[0]+w/2,pt[1]+h/2) for pt in zip(*loc[::-1]) ]

    if len(points)<=4: return points
    #do kmeans and separate the four corners
    # convert to np.float32
    points = np.float32(points)
    # define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    compactness,labels,centers=cv2.kmeans(points,4,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    if compactness/float(len(points)) > 10: return []
    points = [(p[0],p[1]) for p in centers]
    return points

def get_mean_point(points):
    mean = (0,0)
    for p in points:
        mean = (mean[0]+p[0], mean[1]+p[1])
    return (mean[0]/len(points), mean[1]/len(points) )


def rectangle_sort(markers,image):
    result = [0,0,0,0]

    mid_x, mid_y = get_mean_point(markers)

    for p in markers:
        if p[0]<mid_x:
            if p[1]<mid_y: result.insert(0,p), result.pop(1) #first quadrant
            else: result.insert(1,p), result.pop(2) #third quadrant
        else:
            if p[1]>mid_y: result.insert(2,p), result.pop(3) #forth quadrant
            else: result.insert(3,p), result.pop(4) #second quadrant

    #result layout
    # 0 | 3
    #---|---
    # 1 | 2
    if 0 in result: return False

    #check with the dot product and the length of the sides
    # print np.dot( np.subtract(result[1],result[0]), np.subtract(result[0],result[3]) )
    # print np.dot( np.subtract(result[1],result[0]), np.subtract(result[1],result[2]) )
    # print np.dot( np.subtract(result[3],result[2]), np.subtract(result[0],result[3]) )
    # print np.dot( np.subtract(result[3],result[2]), np.subtract(result[1],result[2]) )


    #copy result to markers
    for n in range(0,4): markers.pop()
    markers.extend(result)
    return True

def perspective_transform(image, markers):
    """Makes the perspective transformation to remove possible deformations of the answer area"""
    pts_area = np.float32([list(x) for x in markers])
    area_w = np.linalg.norm(pts_area[1] - pts_area[2])
    area_h = np.linalg.norm(pts_area[0] - pts_area[1])
    w_s = doc_parameters["work_size"]
    if area_w>area_h:
        final_h = w_s
        final_w = int(w_s*area_w/area_h)
    else:
        final_h = int(w_s*area_h/area_w)
        final_w = w_s

    w, h = image.shape[::-1]
    pts2 = np.float32([[0,0],[0,final_h],[final_w,final_h],[final_w,0]])

    M = cv2.getPerspectiveTransform(pts_area,pts2)
    return cv2.warpPerspective(image,M,(final_w,final_h))

def get_answer_images(image, cols, rows, total):
    """Crops the rectangle between the markers that should contain the answers. -> list of cv2.image"""
    result = []
    w, h = image.shape[::-1]

    u_margin = int(doc_parameters["up_margin"]*h)
    d_margin = int(doc_parameters["down_margin"]*h)
    l_margin = int(doc_parameters["left_margin"]*w)
    r_margin = int(doc_parameters["right_margin"]*w)

    cell_w = (w-(l_margin+r_margin))/cols
    cell_h = (h-(u_margin+d_margin))/rows

    cell_u_margin = int(doc_parameters["cell_up_margin"]*cell_h)
    cell_d_margin = int(doc_parameters["cell_down_margin"]*cell_h)
    cell_l_margin = int(doc_parameters["cell_left_margin"]*cell_w)
    cell_r_margin = int(doc_parameters["cell_right_margin"]*cell_w)

    cell_h = int(cell_h)
    cell_w = int(cell_w)
    for question in range(0,total):

        r = int(math.floor(question/cols))
        c = int(question%cols)

        y1= cell_h*r    +u_margin+cell_u_margin
        y2= y1+cell_h   -cell_u_margin-cell_d_margin
        x1= cell_w*c    +l_margin+cell_l_margin
        x2= x1+cell_w   -cell_l_margin-cell_r_margin

        result.append( image[ y1:y2 , x1:x2 ] )

    return result

def get_selections(image, question, index):
    """Finds the answers selected by the student. -> (bool correctness, list of answers)"""
    success, contours = get_contours(image,question.total_answers,index)
    if not success:
        report.success = False
        return False,[]

    thresh = doc_parameters["selection_threshold"]
    error = doc_parameters["selection_error"]

    master_answers = []
    local_answers = []

    vis = None
    # if doc_parameters["poll"]:
    vis = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    a=0
    for data in contours:
        mean = data["mean_intensity"]
        color = (0,0,255)# to visualize the default color is red
        if mean > thresh:
            master_answers.append(question.order[a])
            local_answers.append(a+1)
            color = (0,255,0) #to visualize select the green color
            if mean-thresh <= error:
                w = Warning(index + 1, a + 1, WarningTypes.UNCERTANTY, selected=True)
                report.test.warnings.append(w)
        elif thresh-mean <= error:
            w = Warning(index + 1, a + 1, WarningTypes.UNCERTANTY, selected=False)
            report.test.warnings.append(w)
        a += 1
        # if doc_parameters["poll"]: #if visualization
        center = data["center"]
        radius = data["radius"]
        cv2.ellipse(vis, (int(center[0])+2*int(radius),int(center[1])), (int(radius), int(radius)), 0, 0, 360, color, -1)


    if not question.multiple:
        if len(master_answers)>1:
            w = Warning(index + 1, local_answers, WarningTypes.MULT_SELECTION, selected = False)
            report.test.warnings.append(w)

        if len(master_answers)==0:
            w = Warning(index + 1, local_answers, WarningTypes.EMPTY_SELECTION, selected = False)
            report.test.warnings.append(w)

    #show the image
    # if doc_parameters["poll"]:
    cv2.imshow("Result", vis)

    return True, master_answers

def get_contours(image, total, question):
    #Otsu's thresholding
    #cv2.threshold(image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU,image)
    w, h = image.shape[::-1]
    block_size = w
    if block_size%2==0: block_size+=1
    cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,block_size,doc_parameters["adaptative_threshold_size"],image)

    contours, hierarchy = cv2.findContours(image.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours.reverse()
    if cv2.__version__=="2.4.3": #a bug in opencv 2.4.3, the fix is to add .astype("int") in the contour element
      contours = [get_contour_data(c.astype('int'), image) for c in contours]
    else:
      contours = [get_contour_data(c, image) for c in contours]
    contours = [c for c in contours if not c["empty"]]
    for i in range(len(contours)): contours[i]["index"]=i

    if len(contours) < total:
        return False,[]

    #if there are more contours than expected try merge them
    if len(contours)>total:
        contours = merge_contours_kmeans(contours, total, image)

    if len(contours)>1:
        if not same_size(contours, image):
            report.errors.append(QuestionError(question,"The circles don't have the same size or are too big"))
        else:
            mean_rad = 0
            for c in contours:
                mean_rad+=c["radius"]
            mean_rad=mean_rad/float(len(contours))
            for c in contours:
                c["radius"] = mean_rad
                recalculate_intensity(c,image)

    if len(contours)!= total:
        report.errors.append(QuestionError(question,"The number of circles do not match"))
    if not doc_parameters["squares"] and not are_circular(contours):
        report.errors.append(QuestionError(question,"All the circles don't have the correct shape"))

    if len(contours)>1:
        if not same_distance(contours,doc_parameters["distance_threshold"]):
            report.errors.append(QuestionError(question,"All the circles are not within the same distance"))

        if not are_aligned(contours, doc_parameters["circle_aligment_percent"]):
            report.errors.append(QuestionError(question,"All the boxes are not aligned"))

    if doc_parameters["debug"]:
        debug_contour_detection(contours, image)

    if doc_parameters["debug"]:
        errors = [e for e in report.errors if e.question == question]
        if len(errors)==0: print "-----OK-----"
        else:
            for e in errors:
                print e.message
            print "------------"
        cv2.waitKey()

    if len(report.errors)>0: return False,[]
    return True, contours

def merge_contours_kmeans(contours, centroids, image):
    points = np.float32([p["center"] for p in contours])
    # define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    compactness, labels, centers = cv2.kmeans(points,centroids,criteria,20,cv2.KMEANS_PP_CENTERS)
    groups = {}
    for c in xrange(len(points)):
        label = int(labels[c])
        if label in groups:
            groups[label] = get_contour_data(merge_contours(groups[label], contours[c]),image)
        else:
            groups[label] = contours[c]

    merged = groups.values()
    list.sort(merged, key = lambda x: x["center"][1], reverse = False)
    # list.sort(merged, key = lambda x: x["center"][0], reverse = True)

    for i, c in enumerate(merged):
        c["index"] = i

    return merged

def try_merge_nearby_contours(contours,image):
    for c1 in contours:
        for c2 in contours:
            if c1["index"]==c2["index"]: continue
            big = c1
            small = c2
            if c1["size"]<c2["size"]:
                big = c2
                small = c1
            if dist(big["center"],small["center"])<big["size"]*doc_parameters["merge_size_factor"]:
                contours[big["index"]] = get_contour_data(merge_contours(big,small),image)
                contours.pop(small["index"])
                return 1
    return 0

def merge_contours(big,small):
    result = []
    for c in [big,small]:
        for p in c["points"]:
            result.append(p)
    return np.array([[p] for p in result],dtype=np.int32)

def same_size(contours, image):
    sizes = [c["radius"]*2 for c in contours]
    sizes.sort()
    median_size = sizes[len(sizes)/2]
    w, h = image.shape[::-1]
    max_size = min(w,h)
    for size in sizes:
        if size >= max_size:
            return False
        if abs(size/float(median_size) - 1.0) > doc_parameters["circle_size_difference"]:
            return False
    return True

def are_aligned(contours, threshold):
    centers = [c["center"][0] for c in contours]
    centers.sort()
    median_center = centers[len(centers)/2]

    sizes = [c["radius"] for c in contours]
    sizes.sort()
    median_size = sizes[len(sizes)/2]

    for center in centers:
        difference = abs(median_center-center)
        percent = difference/float(median_size)
        if percent > threshold:
            return False
    return True

    all_points = []
    for c in contours:
        for p in c["points"]:
            all_points.append(p)

    x,y,w,h = cv2.boundingRect(np.array(all_points))
    mean = 0;
    for c in contours: mean+=c["rect"][2]
    mean = float(mean)/len(contours)

    return abs(w-mean)<threshold*mean

def same_distance(contours, threshold):
    mean = 0;
    for i in range(0,len(contours)-1): mean+= dist(contours[i]["center"],contours[i+1]["center"])
    mean = float(mean)/(len(contours)-1)

    for i in range(0,len(contours)-1):
        if abs(dist(contours[i]["center"],contours[i+1]["center"])-mean)>threshold*mean: return False

    return True

def are_circular(contours):
    for c in contours:
        x,y,w,h = c["rect"]
        ratio = float(w)/float(h)
        if abs(1-ratio) > doc_parameters["circle_ratio_threshold"]:
            return False
    return True


def debug_contour_detection(contours, image):
    vis = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    for contour in contours:
        new_radius = int((1-doc_parameters["selection_circle_padding"])*contour["radius"])

        print 'vis: ', vis
        print 'int(contour["center"][0]) ', int(contour["center"][0])
        print 'int(contour["center"][1]) ', int(contour["center"][1])
        print '(int(new_radius), int(new_radius))', (int(new_radius), int(new_radius))

        cv2.ellipse(vis, (int(contour["center"][0]), int(contour["center"][1])), (int(new_radius), int(new_radius)), 0, 0, 360, (0,0,255), 1)
        cv2.ellipse(vis, (int(contour["center"][0]), int(contour["center"][1])), (int(contour["radius"]), int(contour["radius"])), 0, 0, 360, (0,255,0), 1)

    cv2.imshow("Selection Area", vis)

def recalculate_intensity(contour, image):
    if not doc_parameters["squares"]:
        radius = contour["radius"]
        center = contour["center"]
        new_radius = int((1-doc_parameters["selection_circle_padding"])*radius)
        mask = np.zeros(image.shape,np.uint8)
        cv2.ellipse(mask, (int(center[0]),int(center[1])), (new_radius, new_radius), 0, 0, 360, 255, -1)
        contour["mean_intensity"] = cv2.mean(image,mask = mask)[0]

    else:
        x,y,w,h = contour["rect"]
        b = doc_parameters["selection_box_padding"]/2.0
        fillarea = np.array([ [[x+b*w,y+b*h]] , [[x+b*w,y+h-b*h]] , [[x+w-b*w,y+h-b*h]] , [[x+w-b*w,y+b*h]] ], dtype=np.int32 )
        mask = np.zeros(image.shape,np.uint8)
        cv2.drawContours(mask,[fillarea],0,255,-1)
        #improve the calculation of the intensity that decides if it is selected or not.
        contour["mean_intensity"] = cv2.mean(image,mask = mask)[0]


def get_contour_data(contour, image):
    data = {}
    data["empty"] = cv2.contourArea(contour)<=3
    data["convex"] = cv2.isContourConvex(contour)
    data["rect"] = cv2.boundingRect(contour)
    x,y,w,h = data["rect"]
    data["size"] = max(w,h)#float(w+h)/2
    data["radius"] = math.sqrt(w**2+h**2)/2.0
    data["points"] = [(x,y),(x,y+h),(x+w,y+h),(x+w,y)]
    M = cv2.moments(np.array([[p] for p in data["points"]],dtype=np.int32))
    data["center"] = (M['m10']/(M['m00']+0.00001), M['m01']/(M['m00']+0.00001))
    #if the contours are circles instead of squares
    if not doc_parameters["squares"]:
        center, radius = cv2.minEnclosingCircle(contour)
        data["center"] = (int(center[0]),int(center[1]))
        data["radius"] = int(radius)
        new_radius = int((1-doc_parameters["selection_circle_padding"])*radius)

        mask = np.zeros(image.shape,np.uint8)
        cv2.ellipse(mask, (int(center[0]),int(center[1])), (new_radius, new_radius), 0, 0, 360, 255, -1)
        data["mean_intensity"] = cv2.mean(image,mask = mask)[0]

    else:
        b = doc_parameters["selection_box_padding"]/2.0
        fillarea = np.array([ [[x+b*w,y+b*h]] , [[x+b*w,y+h-b*h]] , [[x+w-b*w,y+h-b*h]] , [[x+w-b*w,y+b*h]] ], dtype=np.int32 )
        mask = np.zeros(image.shape,np.uint8)
        cv2.drawContours(mask,[fillarea],0,255,-1)
        #improve the calculation of the intensity that decides if it is selected or not.
        data["mean_intensity"] = cv2.mean(image,mask = mask)[0]

    # if doc_parameters["debug"]: print data["mean_intensity"]


    return data

def dist(x,y):
    return math.sqrt( (x[0] - y[0])**2 + (x[1] - y[1])**2 )

def show_debug_image(img, window_name, check_debug=True):
    if not check_debug or doc_parameters["debug"]:
        cv2.imshow(window_name,img.copy())

def nothing(x):pass

class ImageSource(object):
    """Wrapper class to abstract the fact that the camera feed may come from a single image"""
    def __init__(self, source, time=3):
        self.time = time
        self.is_camera = type(source)==list
        doc_parameters['is_camera'] = self.is_camera
        if self.is_camera:
            print "Loading cameras "+str(source)
            self.sources = [cv2.VideoCapture(cam) for cam in source]
            for s in self.sources:
                s.set(3,800)
                s.set(4,600)
        else:
            self.sources = self.load_file_list(source)

        self.finished = False
        self.current_index = -1
        self.update_current()

    def load_file_list(self, path):
        capture = [os.path.join(path,f) for f in os.listdir(path)]
        if len(capture)==0:
            print "Could not load pictures to simulate a camera."
        return capture


    def get_size(self):
        if self.is_camera:
            return (int(self.current_source.get(3)),int(self.current_source.get(4)))
        else:
            return (self.current_source.shape[1],self.current_source.shape[0])
            #return (self.width, self.height)

    def get_next(self):
        if time.time() - self.start_time > self.time:
                self.update_current()
        if self.is_camera:
            img = self.current_source.read()[1]
            cv2.imshow("Camera "+str(self.current_index),cv2.flip(img, 1))
            return img
        else:
            # img = self.current_source.copy()
            return self.current_source

    def update_current(self):
        self.current_index += 1
        if self.current_index>=len(self.sources):
            self.current_index = 0
            self.finished = True
        if self.is_camera:
            self.current_source = self.sources[self.current_index]
        else:
            self.current_source = cv2.imread(self.sources[self.current_index],1)
            # self.current_source = Image.open(self.sources[self.current_index]).convert('L')
            # self.width, self.height = self.current_source.size
        self.start_time = time.time()

    def release(self):
        if self.is_camera:
            for s in self.sources:
                s.release()
