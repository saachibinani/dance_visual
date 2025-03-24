"""Open AI call with formatted motion data, outputs selected effects"""

import asyncio
import websockets
import json
import os
import openai
import time
import motiontracking.motion_tracking as motion_tracking

# Start OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

#Graphics library, in the future could have more description on what the graphics actually are
effect_library = {
    "particle_explosion": {"color": "#FF0000", "size": 10},
    "color_shift": {"hue": 180},
    "ripple_effect": {"speed": 5, "amplitude": 20},
    "spiral_vortex": {"radius": 50, "color": "#00FF00"}
}

motion_data = []

intention = "Portray a sense of love"

async def get_motion_data():
    #Gets motion data from motion_tracking
    print("Fetching motion data...")
    try:
        motion_data = motion_tracking.main()
        if not motion_data:
            print("Warning: No motion data received from motion_tracking.")
        return motion_data
    except Exception as e:
        print(f"Error fetching motion data: {e}")
        return None

async def send_to_openai(motion_data):
    if not motion_data:
        print("Error: No motion data available to send to OpenAI.")
        return {}
    #Defining AI's responsibilities and example formatted output
    sys_prompt = f"""You analyze dance movements and suggest background effects at numerous different times. 
    You can only select effects from {effect_library}, and you can suggest changes to color, location, and time.
    Ensure your response is **100% valid JSON**. Never include extra text. Produce at least 7 effects throughout the entirety of the video.

    Example valid output:
    {{
    "effects": [
        {{
        "effectType": "ripple_effect",
        "time": 5,
        "location": {{"x": 300, "y": 400}},
        "color": "#00FF00"
        }}
    ]
    }}
    """

    #Place to get relevant motion data, as well as user intention.    
    user_prompt = f"""Motion data: {json.dumps(motion_data, indent=2)} is provided here. The intention for the effects should be {intention}"""
    message = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ]
    for trycount in range(3):
        try:
            completion = client.chat.completions.create(model="gpt-4-turbo",
                                                        messages=message,
                                                        response_format={"type": "json_object"}
                                                        )
            
            raw_response = completion.choices[0].message.content
            print(f"Raw OpenAI response:", raw_response)

            #Error handling for when the data wouldn't be outputted properly
            try:
                response = json.loads(raw_response.strip())  # Strip whitespace and parse
                print(f"Successfully parsed OpenAI response: {json.dumps(response, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Failed JSON response:\n{raw_response}")
                return {}

            effects = response.get("effects", [])
            if not effects:
                print("Warning: OpenAI returned an empty effects list.")

            for effect in response.get("effects", []):
                if "time" not in effect:
                    effect["time"] = effect.get("frame", 0) / 30  
            
            return effects

        except Exception as e:
            print(f"Response generation error ({str(e)})")
            print("Retrying...")
            time.sleep(2)
            trycount += 1

async def send_effects(websocket):
    #Sends AI output through Websocket

    print("Starting motion data collection...")
    motion_data = await get_motion_data()

    if not motion_data:
        print("Error: No motion data collected!")
        await websocket.send(json.dumps({"effects": []}))  # Send empty array
        return

    print(f"Motion data collected: {json.dumps(motion_data, indent=2)}")

    print("Sending motion data to OpenAI...")
    effects = await send_to_openai(motion_data)

    if effects is None:
        print("Error: Effects returned as None. Fixing to empty list.")
        effects = []

    if not effects:  #Ensure effects exist before sending
        print("Error: No effects received from OpenAI. Aborting.")
        await websocket.send(json.dumps({"effects": []}))  # Send empty array
        return

    #Print the final effects before sending for debugging
    print(f"Final effects to be sent: {json.dumps(effects, indent=2)}")

    try:
        message = json.dumps({"effects": effects}, ensure_ascii=False)
        print(f"WebSocket preparing to send message: {message}")

        await websocket.send(message)  #Sending the message

        print("Effects successfully sent to WebSocket.")  #Debugging confirmation

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected before message was sent.")

    except Exception as e:
        print(f"Unexpected WebSocket Error: {e}")

    await websocket.close()  #Close WebSocket after sending so that the data doesn't keep showing up


async def main():
    #setting up websocket
    start_server = await websockets.serve(send_effects, "localhost", 8766)

    print("WebSocket server started on ws://localhost:8766")
    
    try:
        await start_server.wait_closed()  #Keep server running
    except KeyboardInterrupt:
        print("Server shutting down...")


if __name__ == "__main__":
    asyncio.run(main())