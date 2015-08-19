from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from multiprocessing import Process, Queue
from time import sleep
import RPi.GPIO as GPIO
import socket
import sys

# Upper limit
_Servo0UL = 360

# Lower Limit
_Servo0LL = 0

ServoBlaster = open('/dev/servoblaster', 'w')

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
GPIO.setup(37, GPIO.OUT)

frontLF = GPIO.PWM(11, 100)
frontLB = GPIO.PWM(12, 100)
frontRF = GPIO.PWM(16, 100)
frontRB = GPIO.PWM(18, 100)
backRF = GPIO.PWM(38, 100)
backRB = GPIO.PWM(40, 100)
backLF = GPIO.PWM(35, 100)
backLB = GPIO.PWM(37, 100)

camera0Position = 50
speed = 0
state = "stop"

def setCam0Position(position):
    global camera0Position
    print "position: " + str(camera0Position)
    if position >= _Servo0LL and position <= _Servo0UL:
        ServoBlaster.write('0=' + str(position) + '%\n')
        ServoBlaster.flush()
        camera0Position = position
    return;

def setSpeed(newSpeed):
    global speed, state
    speed = newSpeed
    if state == "forward":
        state = "stop"
        goForward()
    elif state == "backward":
        state = "stop"
        goBackward()
    elif state == "left":
        state = "stop"
        pivotLeft()
    elif state == "right":
        state = "stop"
        pivotRight()

def stop():
    global state
    frontLF.stop()
    frontLB.stop()
    frontRF.stop()
    frontRB.stop()
    backRF.stop()
    backRB.stop()
    backLF.stop()
    backLB.stop()
    state = "stop"

def goForward():
    global state
    if state == "stop":
        print "forward"
        frontLF.start(speed)
        frontRF.start(speed)
        backRF.start(speed)
        backLF.start(speed)
    state = "forward"

def goBackward():
    global state
    if state == "stop":
        frontLB.start(speed)
        frontRB.start(speed)
        backRB.start(speed)
        backLB.start(speed)
    state = "backward"

def pivotLeft():
    global state
    if state == "stop":
        frontLB.start(speed)
        frontRF.start(speed)
        backRF.start(speed)
        backLB.start(speed)
    if state == "forward":
        frontLF.ChangeDutyCycle(speed * 0.25)
        backLF.ChangeDutyCycle(speed * 0.25)
        backRF.ChangeDutyCycle(speed * 1.25)
        frontRF.ChangeDutyCycle(speed * 1.25)
    if state == "backward":
        frontLB.ChangeDutyCycle(speed * 0.25)
        backLB.ChangeDutyCycle(speed * 0.25)
        backRB.ChangeDutyCycle(speed * 1.25)
        frontRB.ChangeDutyCycle(speed * 1.25)
    state = "left"

def pivotRight():
    global state
    if state == "stop":
        frontLF.start(speed)
        frontRB.start(speed)
        backRB.start(speed)
        backLF.start(speed)
    if state == "forward":
        frontRF.ChangeDutyCycle(speed * 0.25)
        backRF.ChangeDutyCycle(speed * 0.25)
        backLF.ChangeDutyCycle(speed * 1.25)
        frontLF.ChangeDutyCycle(speed * 1.25)
    if state == "backward":
        frontRB.ChangeDutyCycle(speed * 0.25)
        backRB.ChangeDutyCycle(speed * 0.25)
        backLB.ChangeDutyCycle(speed * 1.25)
        frontLB.ChangeDutyCycle(speed * 1.25)
    state = "right"

def ping():
    return True

setSpeed(40)
for x in xrange(_Servo0UL, _Servo0LL, -1):
    setCam0Position(x)
    sleep(.01)
for x in xrange(_Servo0LL, 50):
    setCam0Position(x)
    sleep(.01)


if __name__=="__main__":


    server = SimpleJSONRPCServer((([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]), 10101))
    
    server.register_function(setSpeed)
    server.register_function(stop)
    server.register_function(goForward)
    server.register_function(goBackward)
    server.register_function(pivotLeft)
    server.register_function(pivotRight)
    server.register_function(ping)
    server.register_function(setCam0Position)

    try:
        print "Server listening..."
        server.serve_forever()
    except KeyboardInterrupt:
        GPIO.cleanup()
    pass



    

