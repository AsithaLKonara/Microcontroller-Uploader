# Sample ESP8266 Firmware Files

This folder contains sample firmware files for testing the J Tech Pixel Uploader.

## Files:

### sample_esp8266.bin
- **Format**: Binary firmware file
- **Size**: 4KB (4096 bytes)
- **Usage**: Standard ESP8266 firmware binary
- **Header**: Contains ESP8266 magic number (0xE9)

### sample_esp8266.hex
- **Format**: Intel HEX file
- **Size**: ~1KB of data
- **Usage**: Alternative firmware format for ESP8266
- **Structure**: Extended linear addressing with sample data

### sample_esp8266.dat
- **Format**: Generic data file
- **Size**: 2KB (2048 bytes)
- **Usage**: Configuration or data file
- **Content**: Sample ESP8266 configuration data

## Testing:

These files can be used to test:
1. File selection in the uploader
2. File validation
3. Upload process simulation
4. Different file format handling

## Note:

These are **SAMPLE FILES ONLY** and should **NOT** be used for actual device flashing.
They contain random data and are intended for testing purposes only.
