"""This program tracks different body parts detected from a video, compiles the data, and sends it through a websocket"""

import cv2 as cv
import numpy as np
import argparse
import asyncio
import websockets
import time

# Define body part mapping
BODY_PARTS = {
    "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
    "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
    "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
    "LEye": 15, "REar": 16, "LEar": 17, "Background": 18
}

# Load OpenPose model
net = cv.dnn.readNetFromTensorflow("motiontracking/graph_opt.pb")


def get_motion_data(cap):
    """print("Waiting for 3 seconds before starting processing...")
    time.sleep(3)  # Wait for 3 seconds before processing"""

    while cap.isOpened():
        hasFrame, frame = cap.read()
        if not hasFrame:
            break

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

            if conf > 0.2:
                points[part] = (int(x), int(y))
            else:
                points[part] = (-1, -1)  # If not detected, send (-1, -1)

        # Format data as "RWrist,x,y,RShoulder,x,y,..."
        data = []
        for part in ["RWrist", "RShoulder", "Neck", "Nose"]:  # You can add more body parts
            x, y = points.get(part, (-1, -1))
            data.append(f"{part},{x},{y}")

        if cv.waitKey(1) & 0xFF == ord('q'):
            break  # Press 'q' to exit

        return data

async def send_motion_data(websocket):
    print("Waiting for 3 seconds before starting processing...")
    time.sleep(3)  # Wait for 3 seconds before processing

    while cap.isOpened():
        hasFrame, frame = cap.read()
        if not hasFrame:
            break

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

            if conf > 0.2:
                points[part] = (int(x), int(y))
            else:
                points[part] = (-1, -1)  # If not detected, send (-1, -1)

        # Format data as "RWrist,x,y,RShoulder,x,y,..."
        data = []
        for part in ["RWrist", "RShoulder", "Neck", "Nose"]:  # You can add more body parts
            x, y = points.get(part, (-1, -1))
            data.append(f"{part},{x},{y}")

        # Send data via WebSocket
        await websocket.send(",".join(data))


        """# Show video with OpenPose skeleton (for debugging)
        for part in ["RWrist", "RShoulder", "Neck", "Nose"]:
            if points[part][0] != -1:  # Draw only detected points
                cv.circle(frame, points[part], 5, (0, 255, 0), -1)"""

        cv.imshow("Pose Estimation", frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break  # Press 'q' to exit

        return data;
        await asyncio.sleep(0.05)

def main():
    #start_server = websockets.serve(send_motion_data, "localhost", 8766)
    #await start_server
    video_path = input("Enter video path: ")
    # Load video
    cap = cv.VideoCapture(video_path) 
    return get_motion_data(cap)
    #await asyncio.Future()  # Keep running forever

"""
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())"""

#cap.release()
cv.destroyAllWindows()
