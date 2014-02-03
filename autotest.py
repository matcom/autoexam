#coding: utf-8
import cv2
import zbar
import numpy as np
import sys
from scanresults import *

import math
import re

report = None
doc_parameters = {
    "show_image": True, #if it is a camera it shows a window with the images, and if it is an image it shows the image
    "double_check": True, #Makes a double confirmation before to return a success report
    "marker_image": "marker.png", #Image of the marker to use in the borders
    "answer_rows": 4, #answers rows     
    "answer_cols": 5, #answers cols
    "marker_match_min_quality": 0.6, #threshold level to apply to the template matching results
    "marker_size": 0.25, #size of the marker with respect to the qrcode width
    "answers_id": ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"], #the id used to identify the answers in order
    #TODO try to recode this to use percent and not pixel units as they are now
    "qrcode_width": 100, #qrcode final width in pixels after perspective transformation
    "margin" : 60, #margin used to crop image after the rotation rectification 

    #padding between the answers area rectangle and the inner answers area (used to rectify any misalignment within the answer area)
    "up_margin": 0.058, 
    "down_margin": 0.033,
    "left_margin": 0.0,
    "right_margin": 0.0,

    #padding between the rectangle with the selection cells and the inner cell area (used to rectify any misalignment within the answer selection rectangle)
    "cell_up_margin": 0.07,
    "cell_down_margin": 0.07,
    "cell_left_margin": 0.75,
    "cell_right_margin": 0.05,    

    "distance_threshold": 0.5, #threshold of the allowed distance between the selection boxes over the mean distance    
    "aligned_threshold": 0.5, #threshold of the alignment allowed between the selection boxes over the mean displacement    
    "selection_box_padding":0.5, #padding used to select the inner area of the selection boxes       
    "selection_threshold": 130, #threshold that is used to decide if the answer is selected based on the mean intensity range:[0,255]
    "selection_error": 30, #threshold around the selection_threshold that marks the uncertainty range:[0,255]
    "single_selection": False #if it's true it will return the answer with the highest mean value (it still uses the selection_threshold and selection_error to display warnings)    
}

class TestScanner:
    def __init__(self, w, h, testsfile, **kw):
        for (k,v) in kw.items():        
            doc_parameters[k]=v
        doc_parameters["scanner"] = QRScanner(w,h);
        doc_parameters["loaded_marker"] = cv2.imread(doc_parameters["marker_image"],0)
        doc_parameters["init"] = True
        doc_parameters["tests"] = scanresults.parse(testsfile)

    def scan(self, source):
        return get_scan_report(source)

    def finalize(self):
        doc_parameters["scanner"] = None
        doc_parameters["loaded_marker"] = None
        doc_parameters["init"] = False
        cv2.destroyAllWindows() 

def get_scan_report(source):
    show = doc_parameters["show_image"]
    if show:
        window_name = "Input"
        cv2.namedWindow(window_name)        

    if not doc_parameters["init"]: return Report()

    global report

    if not doc_parameters["double_check"]:
        report = Report()
        frame = source.get_next()  
        if show: 
            flipped = cv2.flip(frame, 1)
            cv2.imshow(window_name,flipped)
        return get_image_report(frame)
    #if double check is enabled...
    while True:
        report = Report()
        frame = source.get_next()  
        if show: 
            flipped = cv2.flip(frame, 1)
            cv2.imshow(window_name,flipped)
        first = get_image_report(frame)
        if not first.success: 
            return first
        else:
            report = Report()
            frame = source.get_next()  
            if show: 
                flipped = cv2.flip(frame, 1)
                cv2.imshow(window_name,flipped)
            second = get_image_report(frame)
            if not second.success or second.test==first.test:
                return second
            else:
                continue

def get_image_report(frame):
    scanner = doc_parameters.get("scanner")
    marker = doc_parameters.get("loaded_marker")
    #TODO reject blurred images       
    # Set it to gray scale
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # make it binary
    image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,21,5)
    # Scan for QRcodes
    qrcode = scanner.get_qrcodes(image)
    # Check qrcode validity
    if len(qrcode)==1 and qrcode_ok(qrcode[0]):
        qrcode = qrcode.pop()
        report.test = get_test_from_qrcode(qrcode)
        #paint the qrcode in white to lower the chances of getting wrong matches
        cv2.fillConvexPoly(image,np.int32([list(x) for x in qrcode.location]) ,(255))
        size = int(doc_parameters["marker_size"]*dist(qrcode.location[0],qrcode.location[1]));
        rotated, gray_image =  fix_rotation(qrcode.location, image, gray_image)  
        small_marker = cv2.resize(marker,(size,size))
        markers =  get_marker_positions(rotated, small_marker, doc_parameters["marker_match_min_quality"])

        if len(markers)==4 and rectangle_sort(markers,rotated):

            answer_area = perspective_transform(gray_image, markers) 
            cols = doc_parameters["answer_cols"]
            rows = doc_parameters["answer_rows"]
            #TODO make a parameter out of wish order to scan the tests 
            answer_imgs = get_answer_images(answer_area,cols,rows)
            n=0
            bad_data = False
            for img in answer_imgs:                           
                correct, selection = get_selections(img, report.test.questions[n]["total_answers"], n)
                if correct: report.test.questions[n]["answers"] = selection                        
                else: 
                    bad_data = True
                n+=1
            #TODO debug
            cv2.imshow("answer_area",answer_area)

            if not bad_data:
                report.success = True
                return report

        else:
            report.errors.append(MarkersError())
            pass
    else:
        report.errors.append(QrcodeError())
        pass

    return report  

#   exam id | test id
DATA_RE = re.compile(r'''[0-9]+\|[0-9]+''',re.UNICODE)

def qrcode_ok(qrcode):
    data = qrcode.data
    #if the data matches the rege and the test_id is in the test set
    return DATA_RE.match(data) and data.split('|')[1] in doc_parameters["tests"]

def get_test_from_qrcode(qrcode):
    info = qrcode.data.split('|')  
    exam_id = int(info[0]) #not used right now
    test_id = int(info[1])
    return doc_parameters["tests"][test_id]
  
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

    M = cv2.getPerspectiveTransform(pts1,pts2)
    result = cv2.warpPerspective(image,M,(int(result_w),int(result_h)))

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

    w, h = image.shape[::-1] 
    M = cv2.getRotationMatrix2D((w/2,h/2),180*angle/np.pi,1)    
    #TODO o not use the variable margin here, try to find the real w, h that accounts for the new transformation
    margin = doc_parameters["margin"]
    return ( cv2.warpAffine(image,M,(w+2*margin,h+2*margin)), cv2.warpAffine(aux_image,M,(w+2*margin,h+2*margin)) )

def get_marker_positions(image, marker,threshold):
    """Finds the 4 markers that surround the answer area in the image. -> list of tuples"""
    res = cv2.matchTemplate(image,marker,cv2.TM_CCOEFF_NORMED)
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

    return [(p[0],p[1]) for p in centers]

def rectangle_sort(markers,image):
    result = [0,0,0,0]
    w, h = image.shape[::-1]  
    mid_x = w/2.0
    mid_y = h/2.0
    for p in markers:
        if p[0]<mid_x:
            if p[1]<mid_y: result.insert(0,p), result.pop(1)
            else: result.insert(1,p), result.pop(2)
        else:
            if p[1]>mid_y: result.insert(2,p), result.pop(3)
            else: result.insert(3,p), result.pop(4)

    if 0 in result: return False
    #copy result to markers
    for n in range(0,4): markers.pop()
    markers.extend(result)
    return True
  
def perspective_transform(image, markers):
    """Makes the perspective transformation to remove possible deformations of the answer area"""
    w, h = image.shape[::-1] 
    pts1 = np.float32([list(x) for x in markers])    
    pts2 = np.float32([[0,0],[0,h],[w,h],[w,0]])

    M = cv2.getPerspectiveTransform(pts1,pts2)
    return cv2.warpPerspective(image,M,(w,h))

def get_answer_images(image, cols, rows):
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

    for c in range(0,cols):
        for r in range(0,rows):

            y1= cell_h*r    +u_margin+cell_u_margin
            y2= y1+cell_h   -cell_u_margin-cell_d_margin
            x1= cell_w*c    +l_margin+cell_l_margin
            x2= x1+cell_w   -cell_l_margin-cell_r_margin

            result.append( image[ y1:y2 , x1:x2 ] )

    return result

def get_selections(image, total, question):
    """Finds the answers selected by the student. -> (bool correctness, list of answers)"""   
    success, contours = get_contours(image,total,question)
    if not success:
        report.success = False
        return False,[]

    thresh = doc_parameters["selection_threshold"]
    error = doc_parameters["selection_error"]

    answers = []
    if not doc_parameters["single_selection"]:
        a=0
        for data in contours:
            mean = data["mean_intensity"]
            if mean>thresh:
                answers.append(doc_parameters["answers_id"][a])
            if abs(thresh-mean)<=error:
                w = Warning(question,doc_parameters["answers_id"][a],WarningTypes.UNCERTANTY)
                report.test.warnings.append(w)
            a+=1
    else:
        contours.sort(key = lambda cont: cont["mean_intensity"], reverse = True)#sort contours using mean intensity values from high to low
        best_contour = contours[0]
        answers.append(doc_parameters["answers_id"][best_contour["index"]])

        max_mean =      contours[0]["mean_intensity"]
        sec_max_mean =  contours[1]["mean_intensity"]

        if max_mean<thresh or abs(max_mean-sec_max_mean)<=error:
            w = Warning(question,doc_parameters["answers_id"][best_contour["index"]],WarningTypes.UNCERTANTY);
            report.test.warnings.append(w)

        posible_selected = [doc_parameters["answers_id"][c["index"]] for c in contours if c["mean_intensity"]>thresh and c["index"]!=contours[0]["index"]]
        
        if len(posible_selected)>0:
            w = Warning(question,posible_selected,WarningTypes.MULT_SELECTION)
            report.test.warnings.append(w)     

    return True, answers

def get_contours(image, total, question):    
    #Otsu's thresholding
    #cv2.threshold(image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU,image) 
    w, h = image.shape[::-1]
    block_size = w
    if block_size%2==0: block_size+=1
    cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,block_size,10,image)

    contours, hierarchy = cv2.findContours(image.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours.reverse()
    if cv2.__version__=="2.4.3": #a bug in opencv 2.4.3, the fix is to add .astype("int") in the contour element
      contours = [get_contour_data(c.astype('int'), image) for c in contours]
    else: 
      contours = [get_contour_data(c, image) for c in contours]
    contours = [c for c in contours if not c["empty"]]
    for i in range(0,len(contours)): contours[i]["index"]=i

    if len(contours)>total: 
        while True:
            merged = try_merge_nearby_contours(contours,image)
            if merged == 1: 
                for i in range(0,len(contours)): contours[i]["index"]=i
            if merged == 0 or len(contours)<=total: break

    if len(contours)!= total:
        report.errors.append(QuestionError(question,"The number of boxes do not match"))        
    if not are_squared(contours):
        report.errors.append(QuestionError(question,"Not all the boxes are squared"))        
    if len(contours)>1:
        if not same_distance(contours,doc_parameters["distance_threshold"]):
            report.errors.append(QuestionError(question,"Not all the boxes are within the same distance"))        
        if not are_sorted(contours): 
            report.errors.append(QuestionError(question,"The boxes are not sorted")) 
        #if not are_aligned(contours,doc_parameters["aligned_threshold"]):
        #    report.errors.append(QuestionError(question,"Not all the boxes are aligned")) 

    if len(report.errors)>0: return False,[]
    return True, contours

def try_merge_nearby_contours(contours,image):    
    for c1 in contours:
        for c2 in contours:
            if c1["index"]==c2["index"]: continue
            big = c1
            small = c2
            if c1["size"]<c2["size"]: 
                big = c2
                small = c1
            if dist(big["center"],small["center"])<big["size"]:                
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
    
def are_sorted(contours):
    for i in range(0,len(contours)-1): 
        if contours[i]["center"][1]>contours[i+1]["center"][1]: return False
    return True

def get_contour_data(contour, image):
    data = {}           
    data["empty"] = cv2.contourArea(contour)==0
    data["convex"] = cv2.isContourConvex(contour)
    data["rect"] = cv2.boundingRect(contour)    
    x,y,w,h = data["rect"]
    data["size"] = max(w,h)#float(w+h)/2
    data["points"] = [(x,y),(x,y+h),(x+w,y+h),(x+w,y)] 
    M = cv2.moments(np.array([[p] for p in data["points"]],dtype=np.int32))    
    data["center"] = (M['m10']/(M['m00']+0.00001), M['m01']/(M['m00']+0.00001))     
    b = doc_parameters["selection_box_padding"]/2.0 
    fillarea = np.array([ [[x+b*w,y+b*h]] , [[x+b*w,y+h-b*h]] , [[x+w-b*w,y+h-b*h]] , [[x+w-b*w,y+b*h]] ], dtype=np.int32 )
    mask = np.zeros(image.shape,np.uint8)
    cv2.drawContours(mask,[fillarea],0,255,-1)       
    data["mean_intensity"] = cv2.mean(image,mask = mask)[0]    
    return data

def are_squared(contours):
    return True

def are_aligned(contours, threshold):
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
      
def dist(x,y):
    return math.sqrt( (x[0] - y[0])**2 + (x[1] - y[1])**2 )

def nothing(x):pass

class ImageSource(object):
    """Wrapper class to abstract the fact that the camera feed may come from a single image"""
    def __init__(self,source):
        self.is_camera = type(source)==int
        if self.is_camera:
            self.source = cv2.VideoCapture(source)
            self.source.set(3,640)
            self.source.set(4,480)
        else:
            self.source = cv2.imread(source,1)

    def get_size(self):
        if self.is_camera:
            return (int(self.source.get(3)),int(self.source.get(4)))
        else:
            return (self.source.shape[1],self.source.shape[0])

    def get_next(self):
        if self.is_camera:            
            return self.source.read()[1]
        else:
            return self.source     

    def release(self):
        if self.is_camera:
            self.source.release()