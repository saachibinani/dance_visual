"""This program tracks different body parts detected from a video and compiles the data"""

import cv2 as cv
import numpy as np
import argparse
import asyncio
import websockets
import time

# Defines which body parts to map
BODY_PARTS = {
    "RShoulder": 0, "RElbow": 1, "RWrist": 2,
    "LShoulder": 3, "LElbow": 4, "LWrist": 5, "RKnee": 6,
    "RAnkle": 7, "LKnee": 8, "LAnkle": 9
}

# Load OpenPose model
net = cv.dnn.readNetFromTensorflow("motiontracking/graph_opt.pb")


def get_motion_data(cap):
    if not cap.isOpened():
        print("Error opening video file")
        exit()
    frame_number = 0
    recorded_frames  = []
    while True:
        hasFrame, frame = cap.read()
        if not hasFrame:
            break
        #only processing every 10 frames, otherwise it takes too long
        if frame_number % 10 == 0:
            frameWidth = frame.shape[1]
            frameHeight = frame.shape[0]

            # Process frame through OpenPose
            net.setInput(cv.dnn.blobFromImage(frame, 1.0, (368, 368), (127.5, 127.5, 127.5), swapRB=True, crop=False))
            out = net.forward()
            out = out[:, :19, :, :]  # Extract first 19 parts

            points = {}

            # Extract keypoints
            for part, idx in BODY_PARTS.items():
                heatMap = out[0, idx, :, :]
                _, conf, _, point = cv.minMaxLoc(heatMap)
                x = (frameWidth * point[0]) / out.shape[3]
                y = (frameHeight * point[1]) / out.shape[2]

                if conf > 0.5:
                    points[part] = (int(x), int(y))

            # Format data as "RWrist,x,y,frame_number"
            data = []
            for part in BODY_PARTS.keys(): 
                x, y = points.get(part, (-1, -1))
                if (x,y) != (-1, -1):
                    data.append(f"{part},{x},{y},{frame_number}")
            if data:
                recorded_frames.append(data)
                print(f"Frame {frame_number}: {data}")

        frame_number += 1
    
    cap.release()
    return recorded_frames

def main():
    video_path = "sample_dance.mov"
    cap = cv.VideoCapture(video_path) 
    return get_motion_data(cap)


cv.destroyAllWindows()
