#include <SPI.h>
#include <MD_AD9833.h>

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// -----------------------------------------------
// CONFIG OLED
// -----------------------------------------------
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// -----------------------------------------------
// CONFIG AD9833
// -----------------------------------------------
#define DATA  11  
#define CLK   13  
#define FSYNC 10  

MD_AD9833 AD(FSYNC);

// -----------------------------------------------
// PINES Y VARIABLES
// -----------------------------------------------
#define POT   A0
#define BTN   2

int mode;
int freq;
int lastbtn;

// -----------------------------------------------
// VARIABLES PARA DATOS DEL RADAR
// -----------------------------------------------
String rxLine = "";
float distance_m = 0;
float velocity_mps = 0;
String direction = "";

// -----------------------------------------------
// SETUP
// -----------------------------------------------
void setup() {
  Serial.begin(115200);

  pinMode(BTN, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);

  AD.begin();
  mode = 0;
  freq = 0;
  lastbtn = HIGH;

  // --- OLED ---
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for(;;); // No OLED = freeze
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0,0);
  display.println("Radar OLED Ready");
  display.display();

  delay(500);
}

// -----------------------------------------------
// LOOP PRINCIPAL
// -----------------------------------------------
void loop() {

  // =============================
  // 1) LÓGICA ORIGINAL DEL AD9833
  // =============================
  AD.setMode(MD_AD9833::MODE_TRIANGLE);
  delay(500);

  int potval = 30 + analogRead(POT);
  if (potval != freq) {
    freq = potval;
    AD.setFrequency(MD_AD9833::CHAN_0, freq);
  }

  // =============================
  // 2) LECTURA DE DATOS SERIAL
  // =============================
  readSerialRadarData();

  // =============================
  // 3) ACTUALIZAR OLED
  // =============================
  drawOLED();
}

// ========================================================================
// FUNCIÓN: Leer Serial y parsear mensaje de Python
// ========================================================================
void readSerialRadarData() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      parseRadarLine(rxLine);
      rxLine = "";
    } else {
      rxLine += c;
    }
  }
}

// ========================================================================
// FUNCIÓN: Parsear "D:xx.xx,V:yy.yy,DIR:W"
// ========================================================================
void parseRadarLine(String line) {
  line.trim();

  // Ejemplo recibido: D:12.34,V:1.23,DIR:F
  int dIndex = line.indexOf("D:");
  int vIndex = line.indexOf("V:");
  int dirIndex = line.indexOf("DIR:");

  if (dIndex == -1 || vIndex == -1 || dirIndex == -1) return;

  distance_m = line.substring(dIndex + 2, line.indexOf(",", dIndex)).toFloat();
  velocity_mps = line.substring(vIndex + 2, line.indexOf(",", vIndex)).toFloat();
  direction = line.substring(dirIndex + 4);
}

// ========================================================================
// FUNCIÓN: Dibujar en OLED
// ========================================================================
void drawOLED() {

  display.clearDisplay();
  display.setCursor(0,0);
  display.setTextSize(1);

  display.println("   RADAR DOPPLER");
  display.println("----------------------");

  display.print("Dist: ");
  display.print(distance_m, 2);
  display.println(" m");

  display.print("Vel:  ");
  display.print(velocity_mps, 2);
  display.println(" m/s");

  display.print("Dir:  ");
  display.println(direction);

  display.display();
}
