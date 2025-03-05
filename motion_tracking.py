import cv2
import mediapipe as mp
import asyncio
import websockets
from functools import partial

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(1)

async def send_motion_data(websocket, path):
    while cap.isOpened():
        ret, frame = cap.read()
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            # Extract wrist position (as an example)
            right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            x1, y1 = int(right_wrist.x * frame.shape[1]), int(right_wrist.y * frame.shape[0])

            left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
            x2, y2 = int(left_wrist.x * frame.shape[1]), int(left_wrist.y * frame.shape[0])

            motion_data = f"{x1},{y1}"

            await websocket.send(motion_data)

        await asyncio.sleep(0.05)  # Limit data transmission speed

async def main():
    start_server = websockets.serve(partial(send_motion_data, path = "visual_pde"), "localhost", 8765)
    await start_server
    await asyncio.Future()  # Keep running forever

if __name__ == "__main__":
    asyncio.run(main())  # Explicitly start event loop

cap.release()
cv2.destroyAllWindows()
