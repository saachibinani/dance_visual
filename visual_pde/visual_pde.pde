import websockets.*;  

WebsocketClient client;  
int posX = 0, posY = 0;  

void setup() {  
  size(800, 600);  
  background(0);  
  client = new WebsocketClient(this, "ws://localhost:8765");  
}  

void draw() {  
  background(0);  
  fill(255, 0, 0);  
  ellipse(posX, posY, 50, 50);  // Draws a circle following motion tracking  
}  

void webSocketEvent(String msg) {  
  String[] parts = msg.split(",");  
  posX = int(parts[0]);  
  posY = int(parts[1]);  
}
