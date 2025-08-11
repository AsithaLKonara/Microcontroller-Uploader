Write-Host "Committing all changes to git..." -ForegroundColor Green

# Add all changes
git add .

# Commit with detailed message
git commit -m "Add pattern-based hardware testing and UI layout improvements

- Added LED pattern testing functionality for ESP8266/ESP32
- Implemented custom serial protocol for hardware verification
- Added pattern detection and sample pattern creation
- Moved upload log to right side of UI for better layout
- Added auto-reset and visual verification features
- Fixed on_device_change method signature for event binding
- Enhanced device control with smart reset capabilities
- Added comprehensive pattern testing UI with test cycle automation"

Write-Host "Done!" -ForegroundColor Green
Read-Host "Press Enter to continue"
