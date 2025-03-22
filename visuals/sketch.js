let video;
let effects = []; //stores AI-selected effects
let effectObjects = [];
let recorder;
let recording = false;

//Effect classes

class ParticleExplosion {
    constructor(location, color) {
        this.x = location.x || random(width);
        this.y = location.y || random(height);
        this.particles = [];
        this.color = color;
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: this.x, y: this.y,
                vx: random(-2, 2),
                vy: random(-2, 2),
                alpha: 255
            });
        }
    }

    update() {
        for (let p of this.particles) {
            fill(this.color, 127);
            noStroke();
            ellipse(p.x, p.y, 10);
            p.x += p.vx;
            p.y += p.vy;
            p.alpha -= 5;
        }
    }
}

class ColorShift {
    constructor(color) {
        this.color = color;
    }
    update() {
        tint(this.color);
    }
}

class RippleEffect {
    constructor(location, color) {
        this.x = location.x || width / 2;
        this.y = location.y || height / 2;
        this.r = 10;
        this.color = color;
    }

    update() {
        noFill();
        stroke(this.color);
        ellipse(this.x, this.y, this.r);
        this.r += 2;
    }
}

class SpiralVortex {
    constructor(location, color) {
        this.x = location.x || width / 2;
        this.y = location.y || height / 2;
        this.angle = 0;
        this.color = color;
    }

    update() {
        stroke(this.color);
        for (let i = 0; i < 10; i++) {
            let x = this.x + cos(this.angle + i) * i * 5;
            let y = this.y + sin(this.angle + i) * i * 5;
            point(x, y);
        }
        this.angle += 0.1;
    }
}

function setup() {
    //Display video on server
    createCanvas(1400, 600);
    video = createVideo('../sample_dance.mov', videoLoaded);
    video.hide();
    video.volume();
    let startButton = createButton("Start Video");
    startButton.position(width / 2 - 50, height / 2);
    startButton.mousePressed(() => {
        startButton.hide();
        video.play();
    });
    setupWebSocket();
}


let socket;
//Creating the receiving Websocket
function setupWebSocket() {
    socket = new WebSocket("ws://localhost:8766"); //connect to open_ai_call.py

    socket.onopen = function() {
        console.log("Connected to WebSocket server.");
    };

    socket.onmessage = function(event) {
        try {
            console.log("WebSocket received raw data:", event.data);  //Log the raw message received
    
            let data = JSON.parse(event.data);
            
            if (data.effects && Array.isArray(data.effects)) {
                effects = data.effects;
                console.log(" Effects stored:", effects);
                restartEffects();
            } else {
                console.error("Unexpected WebSocket data format or empty effects array:", data);
            }
    
        } catch (error) {
            console.error("Error parsing WebSocket message:", error);
        }
    }; 

    socket.onclose = function() {
        console.log("WebSocket closed.");
    };

    socket.onerror = function(error) {
        console.error("WebSocket Error:", error);
    };
}

function videoLoaded() {
    video.loop();
    video.onended(restartVideo);  //Reset effects when video loops (not working right now)
}

function restartVideo(){
    console.log("Video restarted.");
    video.time(0);
    video.play();
}

function draw() {
    background(0);
    image(video, 0, 0, width, height); //Keep drawing the video

    let currentTime = video.time(); //Get current video time

    //Apply effects at the right time
    effects.forEach((effect, index) => {
        if (currentTime >= effect.time && !effectObjects[index]) {
            applyEffect(effect, index);
        }
    });

    //Keep all effects active across video loops
    effectObjects.forEach(effect => {
        if (effect) effect.update();
    });
}

    
//Applying chosen effects
function applyEffect(effect, index) {
    let { effectType, location, color } = effect;

    //Prevent duplicate effects
    if (effectObjects[index]) return;

    console.log("Applying effect:", effectType);

    let effectObj;
    switch (effectType) {
        case "particle_explosion":
            effectObj = new ParticleExplosion(location, color);
            break;
        case "color_shift":
            effectObj = new ColorShift(color);
            break;
        case "ripple_effect":
            effectObj = new RippleEffect(location, color);
            break;
        case "spiral_vortex":
            effectObj = new SpiralVortex(location, color);
            break;
    }

    effectObjects[index] = effectObj; //Store effect so it's not duplicated
}

function restartEffects() {
    console.log("Restarting effects.");
    
    effects.forEach((effect, index) => {
        if (!effectObjects[index]) {
            applyEffect(effect, index);
        }
    });
}
