my final submission for cmpm 180!! this code generates motion data from the sample_video.mov, sends it to open_ai_call.py. open_ai_call.py passes the data through an ai call, and generates effects. using websocket, these effects are sent to sketch.js, where they are overlayed on a video.

to run:
python3 open_ai_call.py
open index.html in a live server
