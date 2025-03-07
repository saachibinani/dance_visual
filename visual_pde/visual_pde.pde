import websockets.*;  

WebsocketClient client;  
HashMap<String, PVector> bodyPoints = new HashMap<String, PVector>(); // Stores all body parts

void setup() {  
  size(800, 600);  
  background(0);  
  client = new WebsocketClient(this, "ws://localhost:8766");  
}  

void draw() {  
  background(0);  
  fill(255, 0, 0);
  filter(BLUR, 6);
  
  stroke(255);
  
  // Draw each body part as a circle
  for (String key : bodyPoints.keySet()) {
    PVector pos = bodyPoints.get(key);
    if (pos != null) {
      ellipse(pos.x, pos.y, 20, 20);
      textSize(12);
      fill(255);
      text(key, pos.x + 10, pos.y + 5);  // Display part name
    }
  }
}  

void webSocketEvent(String msg) {  
  String[] parts = msg.split(",");  

  // Ensure even number of values (x,y pairs)
  if (parts.length % 3 != 0) return;

  bodyPoints.clear();  // Clear old positions

  for (int i = 0; i < parts.length; i += 3) {
    String partName = parts[i];  // Extract body part name
    float x = float(parts[i + 1]);  
    float y = float(parts[i + 2]);  

    bodyPoints.put(partName, new PVector(x, y));  // Store updated position
  }
}
