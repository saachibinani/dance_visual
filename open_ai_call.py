"""Open AI call that gets motion data from motion_tracking, selects best effects, and sends selections to p5 """
import os
import time
import asyncio
import websockets
from openai import OpenAI
import motiontracking.motion_tracking as motion_track



client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)



EFFECTS = ["particle_explosion", "color_shift", "ripple_effect", "spiral_vortex"]

WEBSOCKET_URL = "ws://localhost:8766"

motion_data = motion_track.main()

dance_prompt = f"""
Evaluate the dance video and suggest the best visual effects in real time.
These graphics are the following options: {', '.join(EFFECTS)}.
Motion Data: {motion_data}
Only return the effect name.
"""

async def send_effect_to_p5(effect):
    """Sends the chosen effect to p5.js via WebSocket.py"""
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(effect)

def send_to_openai(prompt: str, model: str):
    message = [
        {"role": "system", "content": "You analyze dance movements and suggest effects."},
        {"role": "user", "content": prompt
         }
    ]
    for trycount in range(3):
        try:
            completion = client.chat.completions.create(model=model,
                                                        messages=message,)
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Response generation error ({str(e)})")
            print("Retrying...")
            time.sleep(2)
            trycount += 1

    return {}

async def main():
    effect = send_to_openai(dance_prompt, "gpt-4-turbo")
    if effect in EFFECTS:
        print(f"Chosen effect: {effect}")
        #await send_effect_to_p5(effect)
    else:
        print("Invalid effect received.")

if __name__ == "__main__":
    asyncio.run(main())