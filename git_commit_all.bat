@echo off
echo ========================================
echo Committing all changes to git...
echo ========================================

echo.
echo 1. Adding all files to git...
git add .

echo.
echo 2. Checking git status...
git status

echo.
echo 3. Committing with detailed message...
git commit -m "Add pattern-based hardware testing and UI layout improvements

- Added LED pattern testing functionality for ESP8266/ESP32
- Implemented custom serial protocol for hardware verification
- Added pattern detection and sample pattern creation
- Moved upload log to right side of UI for better layout
- Added auto-reset and visual verification features
- Fixed on_device_change method signature for event binding
- Enhanced device control with smart reset capabilities
- Added comprehensive pattern testing UI with test cycle automation
- Updated config.py with pattern testing and LED matrix configs
- Enhanced utils.py with sample pattern creation functions
- Added test_pattern_testing.py for functionality verification
- Created SampleFirmware directory with sample patterns
- Updated requirements.txt with necessary dependencies
- Enhanced README.md with comprehensive documentation
- Added project structure and demo files"

echo.
echo 4. Final git status...
git status

echo.
echo ========================================
echo All changes committed successfully!
echo ========================================
pause
