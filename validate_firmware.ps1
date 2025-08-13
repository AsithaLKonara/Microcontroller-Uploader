#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ESP8266 Firmware Pre-Upload Validator
    
.DESCRIPTION
    Validates firmware files before uploading to ESP8266 to prevent wasted time
    and failed uploads. Checks format, size, integrity, and hardware compatibility.
    
.PARAMETER FirmwareFile
    Path to the firmware file to validate
    
.PARAMETER ComPort
    COM port where ESP8266 is connected (optional)
    
.PARAMETER LedTest
    Run LED hardware test after validation (requires COM port)
    
.EXAMPLE
    .\validate_firmware.ps1 my_firmware.bin
    
.EXAMPLE
    .\validate_firmware.ps1 my_firmware.bin COM4
    
.EXAMPLE
    .\validate_firmware.ps1 my_firmware.bin COM4 -LedTest
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$FirmwareFile,
    
    [Parameter(Mandatory=$false, Position=1)]
    [string]$ComPort,
    
    [Parameter(Mandatory=$false)]
    [switch]$LedTest
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ESP8266 Firmware Validator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if firmware file exists
if (-not (Test-Path $FirmwareFile)) {
    Write-Host "ERROR: Firmware file not found: $FirmwareFile" -ForegroundColor Red
    exit 1
}

Write-Host "Validating firmware: $FirmwareFile" -ForegroundColor Yellow

# Build command arguments
$validatorArgs = @($FirmwareFile)

if ($ComPort) {
    Write-Host "Using COM port: $ComPort" -ForegroundColor Yellow
    $validatorArgs += "--port", $ComPort
} else {
    Write-Host "No COM port specified - running basic validation only" -ForegroundColor Yellow
}

if ($LedTest -and $ComPort) {
    Write-Host "LED test enabled" -ForegroundColor Yellow
    $validatorArgs += "--led-test"
}

Write-Host ""

# Run the validator
try {
    python firmware_validator.py @validatorArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Firmware validation successful!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Firmware validation failed!" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Failed to run firmware validator: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Validation complete!" -ForegroundColor Cyan
