# Fix: libCFApi.so Missing Dependency

## Problem
When trying to use the CHAFON CF591 library, you get:
```
OSError: libhid.so: cannot open shared object file: No such file or directory
```

## Root Cause
The `libCFApi.so` library depends on `libhid.so`, but Raspberry Pi OS uses `libhidapi` libraries instead.

## Solution

Run these commands:

```bash
# 1. Install the libusb HID backend
sudo apt-get install -y libhidapi-libusb0

# 2. Create a symlink from libhid.so to libhidapi-libusb.so.0
sudo ln -sf /usr/lib/aarch64-linux-gnu/libhidapi-libusb.so.0 /usr/lib/aarch64-linux-gnu/libhid.so

# 3. Update library cache
sudo ldconfig

# 4. Verify it works
python3 -c "import ctypes; lib = ctypes.CDLL('libCFApi.so'); print('Success!')"
```

## Verification

After running the fix, verify:

```bash
# Check library loads
python3 -c "from chafon_cf591 import CF591Reader; print('Module imported!')"

# Check dependencies
ldd /usr/local/lib/libCFApi.so | grep hid
```

You should see that `libhid.so` is now found.

## Note

This symlink is safe because:
- `libhidapi-libusb.so.0` provides the same HID functionality
- The CHAFON library was compiled against an older HID library name
- The symlink makes the library compatible with modern systems

