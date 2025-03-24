My first working iteration of this project, submitted for CMPM 180! This code generates motion data from the sample_video.mov, and sends it to open_ai_call.py. open_ai_call.py passes the data through an AI call, and selects effects based on a preexisting dictionary of graphics. Using Websocket, these effects are sent to sketch.js, where they are overlayed on a video.

The intention behind this project is to address integrations of AI in live performance and art. My goal was to demonstrate how AI can be used as an extension of an artist, and help the artist in furthering their vision while remaining ethical when it comes to art generation. I am excited to continue on refining this project in the future, and hopefully implementing a live dance performance aspect at some point.

to run:
python3 open_ai_call.py,
open index.html in a live server
