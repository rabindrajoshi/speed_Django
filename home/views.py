from django.shortcuts import render,redirect
from .forms import CreateUserForm
from django.contrib.auth import authenticate,login,logout
from subprocess import call
from home.models import Login
from django.contrib import messages
from django.http import HttpResponse
from .models import *
#import simplejson as json
from django.core.mail import EmailMessage
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import threading
# views.py
from django.http import JsonResponse
import cv2
import dlib
import time
import math

from .models import Speed

# Create your views here.
def index(request):
    return render(request,'index.html')
    
def team(request):
    return render(request,"team.html")

def design(request):
    speeds = Speed.objects.all() # fetching all the speeds from the database
    context = {'speeds': speeds}
    return render(request,"design.html",context)

#def login_in(request):
    if request.method=="POST":
        name= request.POST.get('name')
        email= request.POST.get('email')
        phone= request.POST.get('phone')
        login=Logins(name=name,email=email,phone=phone)
        login.save()
        messages.success(request, 'Successfully sent!!.')
    return render(request,"login.html")

def registerPage(request):
    form= CreateUserForm ( )

    if request.method == "POST":
        form= CreateUserForm(request.POST )
        if form.is_valid():
             form.save()
             user= form.cleaned_data.get("username") # for retreiving the username from form registration
             messages.success(request, 'Account was created for '+ user)
             return redirect('login1')

    context ={'form':form}
    return render(request,'register.html',context)

def loginPage(request):

    if request.method == "POST":
        username=request.POST.get("username")
        password=request.POST.get("password")

        user= authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request, 'Welcome '+username)
            return redirect('home')
        else :
            messages.info(request,"Username OR Password is incorrect")
            

    context ={}
    return render(request,'login1.html',context)
    
def logoutUser(request):
    logout(request)
    return redirect('login1')

#def open_py_file():
    #    call(["python","mains.py"])
#open_py_file()

def push(request):
    p=Login(number_plate="000",speed=50,s_speed="30")
    p.save()
    messages.info(request, 'Successfully Pushed!!.')
    return render(request,"index.html")

carCascade = cv2.CascadeClassifier(r'C:\Users\User\Desktop\Rabi_Document\speed\home\vech.xml')
video = cv2.VideoCapture('carsvideoo.mp4')
WIDTH = 1200
HEIGHT = 700

def estimateSpeed(location1, location2):
    # the logic to estimate speed
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    # ppm = location2[2] /  carWidht
    ppm = 8.8
    d_meters = d_pixels / ppm
    fps = 18
    speed = int(d_meters * fps *3.6)
    return speed

def trackMultipleObjects():
    # logic to track multiple objects
    rectangleColor = (0, 255, 0)
    frameCounter = 0
    currentCarID = 0
    fps = 0
    global speedd
    speedd=[]
    carTracker = {}
    carNumbers = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000

    out = cv2.VideoWriter('outNew.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 10, (WIDTH, HEIGHT))

    while True:
        start_time = time.time()
        rc, image = video.read()
        if type(image) == type(None):
            break

        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()

        frameCounter = frameCounter + 1
        carIDtoDelete = []

        for carID in carTracker.keys():
            trackingQuality = carTracker[carID].update(image)

            if trackingQuality < 7:
                carIDtoDelete.append(carID)

        
        for carID in carIDtoDelete:
            print("Removing carID " + str(carID) + ' from list of trackers. ')
            print("Removing carID " + str(carID) + ' previous location. ')
            print("Removing carID " + str(carID) + ' current location. ')
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)

        
        if not (frameCounter % 10):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

            for (_x, _y, _w, _h) in cars:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)

                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h

                matchCarID = None

                for carID in carTracker.keys():
                    trackedPosition = carTracker[carID].get_position()

                    t_x = int(trackedPosition.left())
                    t_y = int(trackedPosition.top())
                    t_w = int(trackedPosition.width())
                    t_h = int(trackedPosition.height())

                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                        matchCarID = carID

                if matchCarID is None:
                    print(' Creating new tracker' + str(currentCarID))

                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))

                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]

                    currentCarID = currentCarID + 1

        for carID in carTracker.keys():
            trackedPosition = carTracker[carID].get_position()

            t_x = int(trackedPosition.left())
            t_y = int(trackedPosition.top())
            t_w = int(trackedPosition.width())
            t_h = int(trackedPosition.height())

            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)

            carLocation2[carID] = [t_x, t_y, t_w, t_h]

        end_time = time.time()

        if not (end_time == start_time):
            fps = 1.0/(end_time - start_time)

        for i in carLocation1.keys():
            if frameCounter % 1 == 0:
                [x1, y1, w1, h1] = carLocation1[i]
                [x2, y2, w2, h2] = carLocation2[i]

                carLocation1[i] = [x2, y2, w2, h2]

                if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                    if (speed[i] == None or speed[i] == 0) and y1 >= 275 and y1 <= 285:
                        speed[i] = estimateSpeed([x1, y1, w1, h1], [x1, y2, w2, h2])
                        if speed[i]>30:
                            speed_data = Speed(vehicle_number='vehicle_number_xyz', speed=speed[i],s_speed='30') # creating an instance of the Speed model
                            speed_data.save() # saving the instance to the database
                    if speed[i] != None and y1 >= 180:
                        cv2.putText(resultImage, str(int(speed[i])) + "km/h", (int(x1 + w1/2), int(y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 100) ,2)

        cv2.imshow('result', resultImage)

        out.write(resultImage)

        if cv2.waitKey(1) == 27:
            break
    
    cv2.destroyAllWindows()
    out.release()

def vehicle_speed(request):
    trackMultipleObjects()
    #speeds = Speed.objects.all() # fetching all the speeds from the database
    #context = {'speeds': speeds}
    #return render(request, 'vehicle_speed.html', context)
    return render(request, 'index.html')


"""
@gzip.gzip_page

def Home(request):
    try:
        #cam = VideoCamera()
        cam=cv2.VideoCapture('carsvideoo.mp4')
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request, 'app1.html')

#to capture video class
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
"""

