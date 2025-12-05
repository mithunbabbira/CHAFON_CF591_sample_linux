# CHAFON CF591 RFID Reader - Raspberry Pi Integration

## Overview

This SDK provides everything you need to integrate the CHAFON CF591 UHF RFID reader with your Raspberry Pi to read RFID tags.

## What's Included

### Documentation
- **QUICK_START.md** - Step-by-step guide to get started quickly
- **RASPBERRY_PI_README.md** - Comprehensive API documentation and reference
- **README_RASPBERRY_PI.md** - This file (overview and index)

### Example Code
- **rfid_reader_example.c** - Complete C example program
- **rfid_reader_python.py** - Python wrapper and example
- **Makefile** - Easy compilation for both ARM and ARM64

### SDK Files
- **API/Linux/CFApi.h** - Main header file with all API definitions
- **API/Linux/ARM/** - Libraries for 32-bit Raspberry Pi (Pi 1, 2, Zero)
- **API/Linux/ARM64/** - Libraries for 64-bit Raspberry Pi (Pi 3, 4, 5)

## Quick Start

1. **Connect your device** to Raspberry Pi via USB
2. **Find the serial port**: `ls /dev/ttyUSB*`
3. **Install library**: `sudo cp API/Linux/ARM/libCFApi.so /usr/local/lib/ && sudo ldconfig`
4. **Compile**: `make` (or `make ARM64=1` for 64-bit)
5. **Run**: `./rfid_reader /dev/ttyUSB0`

See **QUICK_START.md** for detailed instructions.

## Architecture Support

| Raspberry Pi Model | Architecture | Library Path |
|-------------------|--------------|--------------|
| Pi 1, 2, Zero | ARM (32-bit) | `API/Linux/ARM/` |
| Pi 3, 4, 5 (32-bit OS) | ARM (32-bit) | `API/Linux/ARM/` |
| Pi 3, 4, 5 (64-bit OS) | ARM64 | `API/Linux/ARM64/` |

Check your architecture: `uname -m`

## Key API Functions

### Connection
- `OpenDevice()` - Open serial port connection
- `CloseDevice()` - Close connection

### Tag Reading
- `InventoryContinue()` - Start reading tags
- `GetTagUii()` - Get tag information
- `InventoryStop()` - Stop reading

### Device Info
- `GetInfo()` - Get device information
- `GetDevicePara()` - Get device parameters
- `SetDevicePara()` - Configure device

## Example Usage

### C Example
```c
int64_t hComm;
TagInfo tag;

// Open device
OpenDevice(&hComm, "/dev/ttyUSB0", 115200);

// Start inventory
InventoryContinue(hComm, 0, 0);

// Read tags
while (GetTagUii(hComm, &tag, 1000) == STAT_OK) {
    // Process tag
    printf("EPC: %s\n", tag.code);
}

// Cleanup
InventoryStop(hComm, 5000);
CloseDevice(hComm);
```

### Python Example
```python
from rfid_reader_python import RFIDReader

reader = RFIDReader('/dev/ttyUSB0', 115200)
reader.open()
reader.start_inventory()

while True:
    tag = reader.read_tag(timeout=1000)
    if tag:
        print(f"EPC: {tag['epc']}, RSSI: {tag['rssi']} dBm")

reader.close()
```

## File Structure

```
CF561.591.5C1.500 SDK/
├── API/
│   └── Linux/
│       ├── CFApi.h              # Main header file
│       ├── ARM/                 # 32-bit libraries
│       │   ├── libCFApi.so
│       │   └── libCFApi.a
│       └── ARM64/              # 64-bit libraries
│           ├── libCFApi.so
│           └── libCFApi.a
├── rfid_reader_example.c       # C example
├── rfid_reader_python.py        # Python wrapper
├── Makefile                     # Build script
├── QUICK_START.md              # Quick start guide
├── RASPBERRY_PI_README.md       # Full documentation
└── README_RASPBERRY_PI.md       # This file
```

## Common Issues and Solutions

### Library Not Found
```bash
sudo cp API/Linux/ARM/libCFApi.so /usr/local/lib/
sudo ldconfig
```

### Permission Denied
```bash
sudo chmod 666 /dev/ttyUSB0
# Or add user to dialout group:
sudo usermod -a -G dialout $USER
```

### No Tags Detected
- Check antenna connection
- Verify tags are within range
- Check RF power settings
- Verify frequency region settings

## Connection Methods

The CF591 supports multiple connection methods:

1. **Serial Port (USB/RS232)**
   - Default: `/dev/ttyUSB0` or `/dev/ttyACM0`
   - Baud rate: 115200

2. **Network (Ethernet)**
   - Use `OpenNetConnection()` instead of `OpenDevice()`
   - Default port: 4001

3. **USB HID**
   - Use `OpenHidConnection()` for HID interface

## Tag Information Structure

Each tag provides:
- **EPC Code** - Electronic Product Code (unique identifier)
- **RSSI** - Signal strength in dBm
- **Antenna** - Which antenna detected the tag (1-4)
- **Channel** - Frequency channel
- **CRC/PC** - Protocol control information

## Next Steps

1. **Read QUICK_START.md** - Get up and running quickly
2. **Review RASPBERRY_PI_README.md** - Understand the full API
3. **Try the examples** - Run `rfid_reader_example.c` or `rfid_reader_python.py`
4. **Customize** - Modify examples for your specific needs

## Additional Resources

- **API Header**: `API/Linux/CFApi.h` - Complete function reference
- **Sample Code**: `Sample/C#/` - C# examples (reference implementation)
- **User Manuals**: `User Guide/` - Device documentation
- **Drivers**: `Drive/` - USB drivers if needed

## Support

For issues:
1. Check the troubleshooting sections in the guides
2. Review error codes in `CFApi.h`
3. Check device connection and permissions
4. Consult CHAFON documentation in `User Guide/`

## License

This SDK is provided by CHAFON for use with their RFID readers. Please refer to your purchase agreement for licensing terms.

---

**Happy RFID Reading!** 🏷️


