#!/usr/bin/env python3
"""
LED Pixel Troubleshooting Script
This script helps diagnose why pixels aren't working after successful uploads
"""

import os
import time
from datetime import datetime

def troubleshoot_pixel_issues():
    """Comprehensive troubleshooting for LED pixel issues"""
    print("🔍 LED Pixel Troubleshooting Guide")
    print("=" * 60)
    
    print("\n📋 Common Issues After Successful Upload:")
    print("1. 🔌 Hardware Connection Problems")
    print("2. ⚡ Power Supply Issues")
    print("3. 🎯 Pin Configuration Mismatch")
    print("4. 🔄 Device Mode Issues")
    print("5. 📱 Firmware Compatibility")
    print("6. 🎨 Pattern Data Issues")
    
    print("\n🔧 Step-by-Step Troubleshooting:")
    
    # Hardware Connection Check
    print("\n1️⃣ HARDWARE CONNECTION CHECK:")
    print("   ✅ Verify all wires are properly connected:")
    print("      • VCC (Power) → 5V or 3.3V (check your LED type)")
    print("      • GND (Ground) → Common ground")
    print("      • DIN (Data In) → Correct GPIO pin")
    print("   ✅ Check for loose connections or cold solder joints")
    print("   ✅ Ensure no wires are touching each other")
    print("   ✅ Verify LED strip orientation (arrow points to data flow)")
    
    # Power Supply Check
    print("\n2️⃣ POWER SUPPLY CHECK:")
    print("   ✅ LED strips need adequate power:")
    print("      • 8x8 RGB Matrix: ~2-3A at 5V")
    print("      • 16x16 RGB Matrix: ~8-10A at 5V")
    print("      • Individual RGB LEDs: ~60mA each at 5V")
    print("   ✅ Use external power supply for LED strips")
    print("   ✅ Don't power LEDs from USB (limited current)")
    print("   ✅ Check voltage levels with multimeter")
    
    # Pin Configuration
    print("\n3️⃣ PIN CONFIGURATION CHECK:")
    print("   ✅ Verify correct GPIO pin in your code:")
    print("      • ESP8266: GPIO2, GPIO4, GPIO5, GPIO12, GPIO13, GPIO14")
    print("      • ESP32: Any GPIO pin (avoid GPIO6-11)")
    print("      • Check if pin is defined correctly in firmware")
    print("   ✅ Ensure pin is not used by other functions")
    print("   ✅ Check for pin conflicts with WiFi/Serial")
    
    # Device Mode Check
    print("\n4️⃣ DEVICE MODE CHECK:")
    print("   ✅ ESP8266/ESP32 modes:")
    print("      • Flash Mode: For uploading firmware")
    print("      • Run Mode: For normal operation")
    print("   ✅ After upload, device should auto-reset to run mode")
    print("   ✅ Check if device is actually running your code")
    print("   ✅ Monitor serial output for startup messages")
    
    # Firmware Compatibility
    print("\n5️⃣ FIRMWARE COMPATIBILITY:")
    print("   ✅ Check if firmware is designed for your LED type:")
    print("      • WS2812B (NeoPixel) - 3-wire protocol")
    print("      • SK6812 - Similar to WS2812B")
    print("      • APA102 - 4-wire SPI protocol")
    print("      • LPD8806 - 2-wire protocol")
    print("   ✅ Verify LED library compatibility")
    print("   ✅ Check for correct color order (RGB vs GRB)")
    
    # Pattern Data Issues
    print("\n6️⃣ PATTERN DATA ISSUES:")
    print("   ✅ If using .dat files:")
    print("      • Verify file format (RGB values 0-255)")
    print("      • Check file size (should be multiple of 3)")
    print("      • Ensure correct matrix dimensions")
    print("   ✅ If using .bin files:")
    print("      • Verify firmware includes LED control code")
    print("      • Check if patterns are hardcoded")
    
    print("\n🔍 DIAGNOSTIC STEPS:")
    
    # Serial Monitor Check
    print("\n📡 SERIAL MONITOR CHECK:")
    print("   1. Connect device to computer")
    print("   2. Open serial monitor at correct baud rate")
    print("   3. Reset device and watch for startup messages")
    print("   4. Look for error messages or warnings")
    print("   5. Check if your code is actually running")
    
    # LED Test Pattern
    print("\n🎨 LED TEST PATTERN:")
    print("   1. Try uploading a simple test pattern:")
    print("      • Single color (all red, all green, all blue)")
    print("      • Simple animation (blinking, scrolling)")
    print("      • Basic shapes (square, circle)")
    print("   2. Start with minimal complexity")
    print("   3. Gradually increase pattern complexity")
    
    # Hardware Test
    print("\n🔌 HARDWARE TEST:")
    print("   1. Test individual components:")
    print("      • Power supply voltage and current")
    print("      • LED strip with known working controller")
    print("      • Microcontroller with simple blink code")
    print("   2. Check for damaged components")
    print("   3. Verify LED strip isn't defective")
    
    print("\n💡 QUICK FIXES TO TRY:")
    print("   🔄 Reset device after upload")
    print("   🔌 Disconnect and reconnect power")
    print("   📱 Check WiFi connection (if applicable)")
    print("   🎯 Verify correct GPIO pin assignment")
    print("   ⚡ Use external power supply")
    print("   🎨 Try simpler test patterns first")
    
    print("\n🚨 EMERGENCY CHECKS:")
    print("   ❌ Is device getting power? (LED indicator on?)")
    print("   ❌ Are you using the right voltage? (3.3V vs 5V)")
    print("   ❌ Is the data pin connected to the right GPIO?")
    print("   ❌ Are there any error messages in serial monitor?")
    print("   ❌ Is the LED strip actually working? (test with known good controller)")
    
    print("\n📞 NEXT STEPS:")
    print("   1. Try the diagnostic steps above")
    print("   2. Check serial monitor for error messages")
    print("   3. Test with simple LED blink code")
    print("   4. Verify hardware connections")
    print("   5. Check power supply adequacy")
    
    print("\n💬 NEED MORE HELP?")
    print("   • Share serial monitor output")
    print("   • Describe your hardware setup")
    print("   • Mention what type of upload you did")
    print("   • Include any error messages")

def create_simple_test_code():
    """Create simple test code for LED troubleshooting"""
    print("\n🎯 SIMPLE LED TEST CODE:")
    print("=" * 40)
    
    print("\n📱 ESP8266/ESP32 Basic LED Test:")
    print("```cpp")
    print("#include <Adafruit_NeoPixel.h>")
    print("")
    print("#define LED_PIN     2  // Change to your GPIO pin")
    print("#define NUM_LEDS    64 // Change to your LED count")
    print("#define BRIGHTNESS  50")
    print("")
    print("Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);")
    print("")
    print("void setup() {")
    print("  Serial.begin(115200);")
    print("  Serial.println(\"LED Test Starting...\");")
    print("  ")
    print("  strip.begin();")
    print("  strip.setBrightness(BRIGHTNESS);")
    print("  strip.show(); // Initialize all pixels to 'off'")
    print("  ")
    print("  Serial.println(\"LED Strip initialized\");")
    print("}")
    print("")
    print("void loop() {")
    print("  // Test 1: All Red")
    print("  Serial.println(\"Testing RED\");")
    print("  colorWipe(strip.Color(255, 0, 0), 100);")
    print("  delay(1000);")
    print("  ")
    print("  // Test 2: All Green")
    print("  Serial.println(\"Testing GREEN\");")
    print("  colorWipe(strip.Color(0, 255, 0), 100);")
    print("  delay(1000);")
    print("  ")
    print("  // Test 3: All Blue")
    print("  Serial.println(\"Testing BLUE\");")
    print("  colorWipe(strip.Color(0, 0, 255), 100);")
    print("  delay(1000);")
    print("}")
    print("")
    print("void colorWipe(uint32_t color, int wait) {")
    print("  for(int i = 0; i < strip.numPixels(); i++) {")
    print("    strip.setPixelColor(i, color);")
    print("    strip.show();")
    print("    delay(wait);")
    print("  }")
    print("}")
    print("```")
    
    print("\n🔧 TROUBLESHOOTING CHECKLIST:")
    print("   □ Upload this simple test code")
    print("   □ Open serial monitor at 115200 baud")
    print("   □ Reset device and watch for messages")
    print("   □ Check if LEDs respond to color changes")
    print("   □ Verify GPIO pin number is correct")
    print("   □ Ensure adequate power supply")

if __name__ == "__main__":
    troubleshoot_pixel_issues()
    create_simple_test_code()
