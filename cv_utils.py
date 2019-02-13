import os
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import pdb

agenet = cv2.dnn.readNet('models/age-gender-recognition-retail-0013.xml', 'models/age-gender-recognition-retail-0013.bin')
agenet.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

def detect_agender(frame):
    
    blob = cv2.dnn.blobFromImage(frame, size=(62, 62), ddepth=cv2.CV_8U)
    agenet.setInput(blob)
    out = agenet.forward()
    print(out)
    # pdb.set_trace()
    print("age: %2.2f" % out[0][0][0][0] * 100)
    print("pct_male: %2.2f" % out[0][1][0][0] * 100)
    return out

facenet = cv2.dnn.readNet('models/face-detection-adas-0001.xml', 'models/face-detection-adas-0001.bin')
facenet.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

def detect_face(frame, thr_conf=.5):
    blob = cv2.dnn.blobFromImage(frame, size=(672, 384), ddepth=cv2.CV_8U)
    facenet.setInput(blob)
    out = facenet.forward()

    predictions = []

    # Draw detected faces on the frame
    for detection in out.reshape(-1, 7):
        conf = float(detection[2])
        xmin = int(detection[3] * frame.shape[1])
        ymin = int(detection[4] * frame.shape[0])
        xmax = int(detection[5] * frame.shape[1])
        ymax = int(detection[6] * frame.shape[0])

        if conf > thr_conf:
            pred_boxpts = ((xmin, ymin), (xmax, ymax))

            frame_face = frame[ymin:ymax, xmin:xmax]
            print(detection, frame.shape, frame_face.shape)
            # print(frame_face)
            frame_face_small = cv2.resize(frame_face, (62, 62))
            cv2.imshow("Cropped", frame_face_small)
            agender = detect_agender(frame_face_small)
            prediction = (conf, pred_boxpts, agender)
            predictions.append(prediction)


    # return the list of predictions to the calling function
    return predictions

# initialize the camera and grab a reference to the raw camera capture
def init_picamera(res = (640, 480)):
    camera = PiCamera()
    camera.resolution = res
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=res)
    camera.rotation = 180
    time.sleep(0.1)

    return (camera, rawCapture)
