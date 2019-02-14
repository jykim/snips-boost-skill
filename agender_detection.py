#!/usr/bin/env python3

import os
import argparse
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
from imutils.video import FPS
import cv2
import pdb
import cv_utils as cvu

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--confidence", default=.5,
                help="confidence threshold")
ap.add_argument("-d", "--display", type=int, default=0,
                help="switch to display image on screen")
ap.add_argument("-i", "--input_image", type=str,
                help="path to optional input image file")
ap.add_argument("-v", "--input_video", type=str,
                help="path to optional input video file")
args = vars(ap.parse_args())

camera, rawCapture = cvu.init_picamera()

if args.get("input_video"):
    print("[INFO] opening video file...")
    vs = cv2.VideoCapture(args["input_video"])
    frames = []
    for i in range(100):
        try:
            frame = vs.read()[1]
            # print(frame.shape)
            frames.append(frame)
        except AttributeError:
            break
    print("Read %d frames" % len(frames))
elif args.get("input_image"):
    frames = [cv2.imread(args["input_image"])]
else:
    frames = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)

# time.sleep(1)
fps = FPS().start()
fcnt = 0
for frame in frames:
    try:
        if args.get("input_video") or args.get("input_image"):
            image = frame
        else:
            image = frame.array

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        image_for_result = image.copy()

        # use the NCS to acquire predictions
        predictions = cvu.detect_face(image)
        # loop over our predictions
        for (i, pred) in enumerate(predictions):
            # extract prediction data for readability
            (pred_conf, pred_boxpts, agender) = pred

            # filter out weak detections by ensuring the `confidence`
            # is greater than the minimum confidence
            if pred_conf > args["confidence"]:
                # print prediction to terminal
                print("[INFO] Prediction #{}: confidence={}, "
                      "boxpoints={}".format(i, pred_conf,
                                            pred_boxpts))

                # check if we should show the prediction data
                # on the frame
                if args["display"] > 0:
                    # build a label
                    label = "person: {:.2f}%".format(pred_conf * 100)

                    # extract information from the prediction boxpoints
                    (ptA, ptB) = (pred_boxpts[0], pred_boxpts[1])
                    (startX, startY) = (ptA[0], ptA[1])
                    y = startY - 15 if startY - 15 > 15 else startY + 15

                    # display the rectangle and label text
                    cv2.rectangle(image_for_result, ptA, ptB,
                                  (255, 0, 0), 2)
                    cv2.putText(image_for_result, label, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        if args["display"] > 0:
            # display the frame to the screen
            cv2.imshow("Output", image_for_result)

        if fcnt == 100:
            break
        else:
            fcnt += 1
        # update the FPS counter
        fps.update()

    # if "ctrl+c" is pressed in the terminal, break from the loop
    except KeyboardInterrupt:
        break

    # if there's a problem reading a frame, break gracefully
    except AttributeError:
        break

# stop the FPS counter timer
fps.stop()

# destroy all windows if we are displaying them
if args["display"] > 0:
    cv2.destroyAllWindows()


# display FPS information
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
