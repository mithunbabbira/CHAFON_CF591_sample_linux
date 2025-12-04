# CHAFON CF591 RFID Reader - Raspberry Pi Integration Guide

## Overview
This guide explains how to use the CHAFON CF591 UHF RFID reader with a Raspberry Pi to read RFID tags.

## SDK Structure

### Linux Libraries Available
The SDK provides pre-compiled libraries for different architectures:
- **ARM** (`API/Linux/ARM/`) - For Raspberry Pi 1, 2, Zero
- **ARM64** (`API/Linux/ARM64/`) - For Raspberry Pi 3, 4, 5 (64-bit OS)
- **x86/x64** - For Intel-based systems

### Key Files
- `CFApi.h` - Main header file with all function declarations and data structures
- `libCFApi.so` - Shared library (dynamic linking)
- `libCFApi.a` - Static library (static linking)

## Connection Methods

The CF591 supports multiple connection methods:

1. **Serial Port (RS232/USB)**
   - Default baud rate: 115200
   - Device appears as `/dev/ttyUSB0` or `/dev/ttyACM0` on Linux

2. **Network (Ethernet)**
   - Default port: 4001
   - Requires network configuration on the reader

3. **USB HID** (if supported)
   - Uses HID interface

## Core API Functions for Reading Tags

### 1. Open Device Connection
```c
int OpenDevice(int64_t* hComm, char* pcCom, int iBaudRate);
```
- Opens serial port connection
- Parameters:
  - `hComm`: Handle pointer (output)
  - `pcCom`: Serial port name (e.g., "/dev/ttyUSB0")
  - `iBaudRate`: Baud rate (typically 115200)
- Returns: `STAT_OK` (0x00000000) on success

### 2. Start Inventory (Tag Reading)
```c
int InventoryContinue(int64_t hComm, unsigned char btInvCount, unsigned long dwInvParam);
```
- Starts continuous inventory/reading mode
- Parameters:
  - `hComm`: Device handle
  - `btInvCount`: Number of tags to read (0 = continuous)
  - `dwInvParam`: Inventory parameters (0 = default)
- Returns: `STAT_OK` on success

### 3. Get Tag Information
```c
int GetTagUii(int64_t hComm, TagInfo* tag_info, unsigned short timeout);
```
- Retrieves tag data from the reader
- Parameters:
  - `hComm`: Device handle
  - `tag_info`: Pointer to TagInfo structure (output)
  - `timeout`: Timeout in milliseconds
- Returns: `STAT_OK` on success, `STAT_CMD_INVENTORY_STOP` when no more tags

### 4. Stop Inventory
```c
int InventoryStop(int64_t hComm, unsigned short timeout);
```
- Stops the inventory process
- Parameters:
  - `hComm`: Device handle
  - `timeout`: Timeout in milliseconds

### 5. Close Device
```c
int CloseDevice(int64_t hComm);
```
- Closes the device connection

## TagInfo Structure

```c
typedef struct {
    unsigned short NO;          // Tag sequence number
    short rssi;                 // Signal strength (RSSI)
    unsigned char antenna;      // Antenna number (1-4)
    unsigned char channel;       // Frequency channel
    unsigned char crc[2];        // CRC bytes
    unsigned char pc[2];         // Protocol control bytes
    unsigned char codeLen;      // EPC code length
    unsigned char code[255];     // EPC code data
} TagInfo;
```

## Workflow for Reading Tags

1. **Open the device** using `OpenDevice()`
2. **Start inventory** using `InventoryContinue()`
3. **Loop to read tags**:
   - Call `GetTagUii()` repeatedly
   - Process each tag's EPC code
   - Continue until no more tags or timeout
4. **Stop inventory** using `InventoryStop()`
5. **Close device** using `CloseDevice()`

## Compilation Instructions

### For Raspberry Pi (ARM/ARM64)

1. **Determine your Pi architecture:**
   ```bash
   uname -m
   ```
   - `armv7l` → Use ARM library
   - `aarch64` → Use ARM64 library

2. **Copy the appropriate library:**
   ```bash
   # For ARM (32-bit)
   cp API/Linux/ARM/libCFApi.so /usr/local/lib/
   
   # For ARM64 (64-bit)
   cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
   
   # Update library cache
   sudo ldconfig
   ```

3. **Compile your program:**
   ```bash
   gcc -o rfid_reader rfid_reader.c -lCFApi -L./API/Linux/ARM -I./API/Linux
   ```

## Example Usage

See `rfid_reader_example.c` for a complete working example.

## Error Codes

Common error codes (defined in `CFApi.h`):
- `STAT_OK` (0x00000000) - Success
- `STAT_PORT_OPEN_FAILED` (0xFFFFFF02) - Failed to open serial port
- `STAT_CMD_COMM_TIMEOUT` (0xFFFFFF12) - Communication timeout
- `STAT_CMD_INVENTORY_STOP` (0xFFFFFF07) - Inventory stopped or no tags found

## Troubleshooting

1. **Device not found:**
   - Check USB connection: `lsusb`
   - Check serial ports: `ls /dev/ttyUSB* /dev/ttyACM*`
   - Ensure proper permissions: `sudo chmod 666 /dev/ttyUSB0`

2. **Library not found:**
   - Ensure library is in `/usr/local/lib/` or set `LD_LIBRARY_PATH`
   - Run `ldconfig` after copying library

3. **No tags detected:**
   - Check antenna connection
   - Verify power settings
   - Ensure tags are within range
   - Check frequency region settings

## Additional Resources

- Header file: `API/Linux/CFApi.h` - Complete API reference
- Sample code: `Sample/C#/` - C# examples (can be used as reference)
- Documentation: `User Guide/` - User manuals

