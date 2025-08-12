/*
 * ESP8266 LED Pixel Test
 * Simple test to verify LED connections and basic functionality
 * 
 * Hardware:
 * - ESP8266 (NodeMCU, Wemos D1 Mini, etc.)
 * - WS2812B LED Matrix or Strip
 * - 5V Power Supply (2-3A for 8x8, 8-10A for 16x16)
 * 
 * Connections:
 * - VCC → 5V Power Supply
 * - GND → Common Ground (shared with ESP8266)
 * - DIN → GPIO2 (D4 on NodeMCU)
 */

#include <Adafruit_NeoPixel.h>

// Configuration - CHANGE THESE IF NEEDED
#define LED_PIN     2     // GPIO2 (D4 on NodeMCU) - CHANGE IF USING DIFFERENT PIN
#define NUM_LEDS    64    // 8x8 matrix = 64 LEDs - CHANGE IF DIFFERENT
#define BRIGHTNESS  50    // Brightness 0-255 (start low to test)

// Create LED strip object
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// Test colors
uint32_t colors[] = {
  strip.Color(255, 0, 0),     // Red
  strip.Color(0, 255, 0),     // Green
  strip.Color(0, 0, 255),     // Blue
  strip.Color(255, 255, 0),   // Yellow
  strip.Color(255, 0, 255),   // Magenta
  strip.Color(0, 255, 255),   // Cyan
  strip.Color(255, 255, 255), // White
  strip.Color(0, 0, 0)        // Off
};

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  delay(1000); // Wait for serial to start
  
  Serial.println();
  Serial.println("=== ESP8266 LED PIXEL TEST ===");
  Serial.println("Starting LED test...");
  
  // Initialize LED strip
  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.clear();
  strip.show();
  
  Serial.println("LED strip initialized");
  Serial.print("Pin: GPIO");
  Serial.println(LED_PIN);
  Serial.print("LEDs: ");
  Serial.println(NUM_LEDS);
  Serial.print("Brightness: ");
  Serial.println(BRIGHTNESS);
  Serial.println("Ready to test!");
}

void loop() {
  // Test 1: Individual colors
  Serial.println("\n--- Testing Individual Colors ---");
  
  for (int i = 0; i < 7; i++) { // Skip the last color (off)
    Serial.print("Testing color ");
    Serial.println(i + 1);
    
    // Fill all LEDs with current color
    fillAll(colors[i]);
    delay(2000); // Show for 2 seconds
  }
  
  // Test 2: Turn off
  Serial.println("Turning all LEDs OFF");
  fillAll(colors[7]); // Off
  delay(2000);
  
  // Test 3: Rainbow effect
  Serial.println("\n--- Testing Rainbow Effect ---");
  rainbow(20);
  
  // Test 4: Individual LED test
  Serial.println("\n--- Testing Individual LEDs ---");
  testIndividualLEDs();
  
  // Test 5: Pattern test
  Serial.println("\n--- Testing Patterns ---");
  testPatterns();
  
  Serial.println("\n--- Test Complete - Restarting ---");
  delay(3000);
}

// Fill all LEDs with a color
void fillAll(uint32_t color) {
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, color);
  }
  strip.show();
}

// Rainbow effect
void rainbow(int wait) {
  for (long firstPixelHue = 0; firstPixelHue < 5 * 65536; firstPixelHue += 256) {
    for (int i = 0; i < NUM_LEDS; i++) {
      int pixelHue = firstPixelHue + (i * 65536L / NUM_LEDS);
      strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(pixelHue)));
    }
    strip.show();
    delay(wait);
  }
}

// Test individual LEDs
void testIndividualLEDs() {
  for (int i = 0; i < NUM_LEDS; i++) {
    Serial.print("Testing LED ");
    Serial.println(i);
    
    // Turn off all LEDs
    strip.clear();
    
    // Turn on current LED
    strip.setPixelColor(i, strip.Color(255, 255, 255)); // White
    strip.show();
    
    delay(100); // Brief flash
  }
  
  // Turn all off
  strip.clear();
  strip.show();
}

// Test some basic patterns
void testPatterns() {
  // Pattern 1: Alternating colors
  Serial.println("Pattern 1: Alternating colors");
  for (int i = 0; i < NUM_LEDS; i++) {
    if (i % 2 == 0) {
      strip.setPixelColor(i, strip.Color(255, 0, 0)); // Red
    } else {
      strip.setPixelColor(i, strip.Color(0, 0, 255)); // Blue
    }
  }
  strip.show();
  delay(2000);
  
  // Pattern 2: Border only
  Serial.println("Pattern 2: Border only");
  strip.clear();
  
  // Calculate matrix dimensions (assuming square)
  int matrixSize = sqrt(NUM_LEDS);
  
  for (int i = 0; i < NUM_LEDS; i++) {
    int row = i / matrixSize;
    int col = i % matrixSize;
    
    // If on border, make it green
    if (row == 0 || row == matrixSize - 1 || col == 0 || col == matrixSize - 1) {
      strip.setPixelColor(i, strip.Color(0, 255, 0)); // Green
    }
  }
  strip.show();
  delay(2000);
  
  // Clear all
  strip.clear();
  strip.show();
}

/*
 * TROUBLESHOOTING:
 * 
 * 1. NO LEDs LIGHT UP:
 *    - Check power supply (use 5V, not 3.3V)
 *    - Verify VCC → 5V, GND → GND, DIN → GPIO2
 *    - Check power supply current (need 2-3A for 8x8)
 *    - Try different GPIO pin (GPIO4, GPIO5, GPIO12, GPIO13, GPIO14)
 *    - Reset device after upload
 * 
 * 2. SOME LEDs WORK:
 *    - Check power supply current rating
 *    - Verify all connections are solid
 *    - Check for damaged LED segments
 * 
 * 3. WRONG COLORS:
 *    - Change NEO_GRB to NEO_RGB in strip definition
 *    - Check LED type (WS2812B vs SK6812 vs APA102)
 * 
 * 4. FLICKERING:
 *    - Reduce brightness (change BRIGHTNESS value)
 *    - Check power supply stability
 *    - Verify ground connections
 * 
 * 5. SERIAL MONITOR:
 *    - Open at 115200 baud
 *    - Look for startup messages
 *    - Check for error messages
 */
