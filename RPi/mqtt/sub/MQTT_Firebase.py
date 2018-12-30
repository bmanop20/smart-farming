#!/usr/bin/env python

"""
   File name: MQTT_Firebase.py
   Author: Emerson Navarro
   Date created: 12/11/2018
   Date last modified: 12/12/2018
   Python version: 2.7
"""

import CONSTANT
import CONFIG
import pyrebase
from FirebaseAlert import FirebaseAlert
from FirebaseOutput import FirebaseOutput
from FirebaseThreshold import FirebaseThreshold

config = CONFIG.config

firebase = pyrebase.initialize_app(config)
firebase.auth()

db = firebase.database()

def getModuleAlerts(broker,module,sensorType):
    return db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_ALERTS).get()

def getModuleAlertForSensor(broker,module,sensorType):
    return db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_ALERTS).child(sensorType).get().val()

def getModuleOutputStatus(broker,module):
    status = {}
    outputStatus = db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_OUTPUTS).get()
    for output in outputStatus.each():
        status[output.key()] = output.val()
    return status

def postAlertToFirebase(broker,module,alertType,value):
    #alert: Temperature or Moisture
    #value: 0 or 1
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_ALERTS).update({alertType : value})

def setOutputOnFirebase(broker,module,outputType,value):
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_OUTPUTS).child(outputType).update({"State" : value})

def getTresholdsFromFirebase(broker, thresholdType):
    threshold = {}
    limits = db.child(broker).child(CONSTANT.F_THRESHOLD).child(thresholdType).get()
    for limit in limits.each():
        threshold[limit.key()] = limit.val()
    return threshold

def postMessageToFirebase(broker,module,sensorType,data):
    print("sending message to Firebase with Broker: " + str(broker) + ", Module: " + str(module) + ", SensorType: " + str(sensorType) + ", Value: " + str(data))
    db.child(broker+"-HIST").child("DevicesMeasurements").child(module).child(CONSTANT.F_INPUTS).child(sensorType).push(data)
    
def stream_handler(message):
    if (str(message["stream_id"]) == "Output" and len(str(message['path'])) > 1 ):
        outputType = str(message['path']).split("/")
        print ('Sending command to ESP: '+ str(outputType[1]) + '. SET the ' + str(outputType[3]) + ' system with the value ' + str(message['data']) )
        #sendCommandToEsp(outputType[1],outputType[3],'SET',message['data'])
        print("################################################")

# Start a listerner that handles the Threshold node
def startListener(broker):
    db.child(broker).child(CONSTANT.F_THRESHOLD).stream(stream_handler, stream_id="Threshold")
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).stream(stream_handler, stream_id="Output")

#Handle treshold value
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Moisture")
moistThreshold = FirebaseThreshold("Moisture",current_threshold["High"],current_threshold["Low"]) 
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Temperature")
tempThreshold = FirebaseThreshold("Temperature",current_threshold["High"],current_threshold["Low"])

#startListener(CONSTANT.BROKER_ID)