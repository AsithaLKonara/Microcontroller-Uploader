@echo off
echo ========================================
echo ESP8266 Firmware Validator
echo ========================================
echo.

if "%~1"=="" (
    echo Usage: validate_firmware.bat <firmware_file> [COM_port]
    echo.
    echo Examples:
    echo   validate_firmware.bat my_firmware.bin
    echo   validate_firmware.bat my_firmware.bin COM4
    echo   validate_firmware.bat my_firmware.bin COM4 --led-test
    echo.
    pause
    exit /b 1
)

set FIRMWARE_FILE=%~1
set COM_PORT=%~2

if not exist "%FIRMWARE_FILE%" (
    echo ERROR: Firmware file not found: %FIRMWARE_FILE%
    pause
    exit /b 1
)

echo Validating firmware: %FIRMWARE_FILE%
if not "%COM_PORT%"=="" (
    echo Using COM port: %COM_PORT%
    echo.
    python firmware_validator.py "%FIRMWARE_FILE%" --port %COM_PORT%
) else (
    echo No COM port specified - running basic validation only
    echo.
    python firmware_validator.py "%FIRMWARE_FILE%"
)

echo.
echo Validation complete!
pause
