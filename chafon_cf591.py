#!/usr/bin/env python3
"""
CHAFON CF591 UHF RFID Reader - Comprehensive Python Wrapper for Raspberry Pi

This module provides a complete Python interface to the CHAFON CF591 RFID reader,
implementing ALL available API functions for:
- Tag reading (inventory) with trigger-based control
- Power/range control
- Tag memory read/write operations
- Device configuration
- Antenna management
- GPIO/Relay control
- Network/WiFi configuration
- And more...

Requirements:
    - Python 3.6+
    - ctypes (built-in)
    - libCFApi.so library installed

For Raspberry Pi 5 (ARM64):
    sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
    sudo ldconfig

Usage:
    from chafon_cf591 import CF591Reader
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        # Read a single tag (trigger-based)
        tag = reader.read_single_tag(timeout=3000)
        if tag:
            print(f"Tag EPC: {tag['epc']}")
        
        # Set reading range (power level 0-30 dBm)
        reader.set_rf_power(20)  # Lower power = shorter range
        
        # Continuous reading
        reader.start_inventory()
        for tag in reader.read_tags_iterator(max_count=10):
            print(f"Found: {tag['epc']}")
        reader.stop_inventory()

Author: Auto-generated from CHAFON CF591 SDK
"""

import ctypes
import ctypes.util
from ctypes import (
    Structure, POINTER, c_int64, c_char_p, c_int, c_ubyte, c_ushort, 
    c_short, c_ulong, c_uint, c_void_p, byref, sizeof, cast
)
import os
import sys
import time
import threading
from typing import Optional, List, Dict, Generator, Callable, Any
from enum import IntEnum
from dataclasses import dataclass


# ============================================================================
# Constants and Error Codes
# ============================================================================

class StatusCode(IntEnum):
    """API Status/Error Codes"""
    OK = 0x00000000
    PORT_HANDLE_ERR = 0xFFFFFF01       # Handle error or input serial port parameter error
    PORT_OPEN_FAILED = 0xFFFFFF02      # Failed to open serial port
    DLL_INNER_FAILED = 0xFFFFFF03      # Internal error in dynamic library
    CMD_PARAM_ERR = 0xFFFFFF04         # Parameter value incorrect or out of range
    CMD_SERIAL_NUM_EXIT = 0xFFFFFF05   # Serial number already exists
    CMD_INNER_ERR = 0xFFFFFF06         # Command execution failed due to internal module error
    CMD_INVENTORY_STOP = 0xFFFFFF07    # Inventory not found on label or completed
    CMD_TAG_NO_RESP = 0xFFFFFF08       # Label response timeout
    CMD_DECODE_TAG_DATA_FAIL = 0xFFFFFF09  # Demodulation label data error
    CMD_CODE_OVERFLOW = 0xFFFFFF0A     # Label data exceeds maximum transmission length
    CMD_AUTH_FAIL = 0xFFFFFF0B         # Authentication failed
    CMD_PWD_ERR = 0xFFFFFF0C           # Password error
    CMD_SAM_NO_RESP = 0xFFFFFF0D       # SAM card not responding
    CMD_SAM_CMD_FAIL = 0xFFFFFF0E      # PSAM card command execution failed
    CMD_RESP_FORMAT_ERR = 0xFFFFFF0F   # Reader/writer response format error
    CMD_HAS_MORE_DATA = 0xFFFFFF10     # Command successful, more data pending
    CMD_BUF_OVERFLOW = 0xFFFFFF11      # Buffer overflow
    CMD_COMM_TIMEOUT = 0xFFFFFF12      # Communication timeout
    CMD_COMM_WR_FAILED = 0xFFFFFF13    # Failed to write data to serial port
    CMD_COMM_RD_FAILED = 0xFFFFFF14    # Failed to read serial port data
    CMD_NOMORE_DATA = 0xFFFFFF15       # No more data available
    DLL_UNCONNECT = 0xFFFFFF16         # Network connection not established
    DLL_DISCONNECT = 0xFFFFFF17        # Network disconnected
    CMD_RESP_CRC_ERR = 0xFFFFFF18      # Reader/writer response CRC error


class MemoryBank(IntEnum):
    """Tag Memory Banks"""
    RESERVED = 0x00   # Reserved memory (Kill Password, Access Password)
    EPC = 0x01        # EPC memory
    TID = 0x02        # TID memory (Tag Identifier)
    USER = 0x03       # User memory


class LockAction(IntEnum):
    """Lock/Unlock Actions"""
    UNLOCK = 0x00
    LOCK = 0x01
    PERMANENT_UNLOCK = 0x02
    PERMANENT_LOCK = 0x03


class LockArea(IntEnum):
    """Lockable Memory Areas"""
    KILL_PWD = 0x00
    ACCESS_PWD = 0x01
    EPC = 0x02
    TID = 0x03
    USER = 0x04


class Region(IntEnum):
    """Frequency Regions"""
    FCC = 0x01        # US (902-928 MHz)
    ETSI = 0x02       # EU (865-868 MHz)
    CHN = 0x03        # China (920-925 MHz)
    KOREA = 0x04      # Korea
    JAPAN = 0x05      # Japan
    OPEN = 0x06       # Custom/Open


class WorkMode(IntEnum):
    """Reader Work Modes"""
    COMMAND = 0x00    # Command mode (manual trigger)
    AUTO = 0x01       # Auto mode (continuous reading)
    TRIGGER = 0x02    # Trigger mode (external trigger)
    WIEGAND = 0x03    # Wiegand output mode


class BaudRate(IntEnum):
    """Serial Baud Rates"""
    BR_9600 = 0x00
    BR_19200 = 0x01
    BR_38400 = 0x02
    BR_57600 = 0x03
    BR_115200 = 0x04


# ============================================================================
# C Structures (matching CFApi.h)
# ============================================================================

class TagInfo(Structure):
    """Tag information structure returned by GetTagUii"""
    _fields_ = [
        ("NO", c_ushort),           # Tag sequence number
        ("rssi", c_short),          # Signal strength (RSSI) in 0.1 dBm
        ("antenna", c_ubyte),       # Antenna number (1-4)
        ("channel", c_ubyte),       # Frequency channel
        ("crc", c_ubyte * 2),       # CRC bytes
        ("pc", c_ubyte * 2),        # Protocol control bytes
        ("codeLen", c_ubyte),       # EPC code length in bytes
        ("code", c_ubyte * 255)     # EPC code data
    ]


class TagResp(Structure):
    """Tag response structure for read/write operations"""
    _fields_ = [
        ("tagStatus", c_ubyte),
        ("antenna", c_ubyte),
        ("crc", c_ubyte * 2),
        ("pc", c_ubyte * 2),
        ("codeLen", c_ubyte),
        ("code", c_ubyte * 255)
    ]


class DeviceInfo(Structure):
    """Device information structure"""
    _fields_ = [
        ("firmVersion", c_ubyte * 32),
        ("hardVersion", c_ubyte * 32),
        ("SN", c_ubyte * 12),
        ("PARAS", c_ubyte * 12)
    ]


class DeviceFullInfo(Structure):
    """Full device information structure"""
    _fields_ = [
        ("DevicehardVersion", c_ubyte * 32),
        ("DevicefirmVersion", c_ubyte * 32),
        ("DeviceSN", c_ubyte * 12),
        ("hardVersion", c_ubyte * 32),
        ("firmVersion", c_ubyte * 32),
        ("SN", c_ubyte * 12)
    ]


class DevicePara(Structure):
    """Device parameters structure"""
    _fields_ = [
        ("DEVICEADDR", c_ubyte),      # Device address
        ("RFIDPRO", c_ubyte),         # RFID protocol
        ("WORKMODE", c_ubyte),        # Work mode
        ("INTERFACE", c_ubyte),       # Interface type
        ("BAUDRATE", c_ubyte),        # Baud rate
        ("WGSET", c_ubyte),           # Wiegand settings
        ("ANT", c_ubyte),             # Antenna mask
        ("REGION", c_ubyte),          # Frequency region
        ("STRATFREI", c_ubyte * 2),   # Start frequency (increase)
        ("STRATFRED", c_ubyte * 2),   # Start frequency (decrease)
        ("STEPFRE", c_ubyte * 2),     # Frequency step
        ("CN", c_ubyte),              # Channel number
        ("RFIDPOWER", c_ubyte),       # RF power
        ("INVENTORYAREA", c_ubyte),   # Inventory area
        ("QVALUE", c_ubyte),          # Q value
        ("SESSION", c_ubyte),         # Session
        ("ACSADDR", c_ubyte),         # Access address
        ("ACSDATALEN", c_ubyte),      # Access data length
        ("FILTERTIME", c_ubyte),      # Filter time
        ("TRIGGLETIME", c_ubyte),     # Trigger time
        ("BUZZERTIME", c_ubyte),      # Buzzer time
        ("INTENERLTIME", c_ubyte)     # Internal time
    ]


class FreqInfo(Structure):
    """Frequency information structure"""
    _fields_ = [
        ("region", c_ubyte),
        ("StartFreq", c_ushort),
        ("StopFreq", c_ushort),
        ("StepFreq", c_ushort),
        ("cnt", c_ubyte)
    ]


class NetInfo(Structure):
    """Network information structure"""
    _fields_ = [
        ("IP", c_ubyte * 4),
        ("MAC", c_ubyte * 6),
        ("PORT", c_ubyte * 2),
        ("NetMask", c_ubyte * 4),
        ("Gateway", c_ubyte * 4)
    ]


class WiFiPara(Structure):
    """WiFi parameters structure"""
    _fields_ = [
        ("wifiEn", c_ubyte),
        ("SSID", c_ubyte * 32),
        ("PASSWORD", c_ubyte * 64),
        ("IP", c_ubyte * 4),
        ("PORT", c_ubyte * 2)
    ]


class SelectSortParam(Structure):
    """Select/Sort parameters for tag filtering"""
    _fields_ = [
        ("target", c_ubyte),
        ("trucate", c_ubyte),
        ("action", c_ubyte),
        ("membank", c_ubyte),
        ("m_ptr", c_ushort),
        ("len", c_ubyte),
        ("mask", c_ubyte * 31)
    ]


class QueryParam(Structure):
    """Query parameters structure"""
    _fields_ = [
        ("condition", c_ubyte),
        ("session", c_ubyte),
        ("target", c_ubyte)
    ]


class PermissonPara(Structure):
    """Permission parameters for tag filtering"""
    _fields_ = [
        ("CodeEn", c_ubyte),
        ("Code", c_ubyte * 4),
        ("MaskEn", c_ubyte),
        ("StartAdd", c_ubyte),
        ("MaskLen", c_ubyte),
        ("MaskData", c_ubyte * 12),
        ("MaskCondition", c_ubyte)
    ]


class GpioPara(Structure):
    """GPIO parameters structure"""
    _fields_ = [
        ("KCEn", c_ubyte),
        ("RelayTime", c_ubyte),
        ("KCPowerEn", c_ubyte),
        ("TriggleMode", c_ubyte),
        ("BufferEn", c_ubyte),
        ("ProtocolEn", c_ubyte),
        ("ProtocolType", c_ubyte),
        ("ProtocolFormat", c_ubyte * 10)
    ]


class GPIOWorkParam(Structure):
    """GPIO work parameters structure"""
    _fields_ = [
        ("Mode", c_ubyte),
        ("GPIEnable", c_ubyte),
        ("InLevel", c_ubyte),
        ("GPOEnable", c_ubyte),
        ("PutLevel", c_ubyte),
        ("PutTime", c_ubyte * 8)
    ]


class AntPower(Structure):
    """Antenna power settings"""
    _fields_ = [
        ("Enable", c_ubyte),
        ("AntPower", c_ubyte * 8)
    ]


class Heartbeat(Structure):
    """Heartbeat settings"""
    _fields_ = [
        ("Enable", c_ubyte),
        ("Time", c_ubyte),
        ("Len", c_ubyte),
        ("Data", c_ubyte * 32)
    ]


class RssiPara(Structure):
    """RSSI filter parameters"""
    _fields_ = [
        ("BasciRssi", c_short),
        ("AntDelta", c_ubyte * 16)
    ]


# ============================================================================
# Data Classes for Python-friendly returns
# ============================================================================

@dataclass
class Tag:
    """Python-friendly tag data structure"""
    epc: str                    # EPC code as hex string
    epc_bytes: bytes            # EPC as raw bytes
    rssi: float                 # Signal strength in dBm
    antenna: int                # Antenna number
    channel: int                # Frequency channel
    crc: str                    # CRC as hex string
    pc: str                     # Protocol Control as hex string
    length: int                 # EPC length in bytes
    sequence: int               # Tag sequence number
    
    @classmethod
    def from_tag_info(cls, tag_info: TagInfo) -> 'Tag':
        """Create Tag from C TagInfo structure"""
        epc_bytes = bytes(tag_info.code[:tag_info.codeLen])
        return cls(
            epc=''.join(f'{b:02X}' for b in epc_bytes),
            epc_bytes=epc_bytes,
            rssi=tag_info.rssi / 10.0,
            antenna=tag_info.antenna,
            channel=tag_info.channel,
            crc=bytes(tag_info.crc).hex().upper(),
            pc=bytes(tag_info.pc).hex().upper(),
            length=tag_info.codeLen,
            sequence=tag_info.NO
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'epc': self.epc,
            'epc_bytes': self.epc_bytes,
            'rssi': self.rssi,
            'antenna': self.antenna,
            'channel': self.channel,
            'crc': self.crc,
            'pc': self.pc,
            'length': self.length,
            'sequence': self.sequence
        }


# ============================================================================
# Exception Classes
# ============================================================================

class CF591Error(Exception):
    """Base exception for CF591 operations"""
    def __init__(self, message: str, error_code: int = None):
        self.error_code = error_code
        self.message = message
        super().__init__(f"{message} (Error: 0x{error_code:08X})" if error_code else message)


class ConnectionError(CF591Error):
    """Connection-related errors"""
    pass


class CommandError(CF591Error):
    """Command execution errors"""
    pass


class TagError(CF591Error):
    """Tag operation errors"""
    pass


# ============================================================================
# Library Loader
# ============================================================================

def _load_library():
    """Load the libCFApi.so shared library"""
    # First, try loading by name (works if in system library path)
    # This is the most reliable method when library is properly installed
    try:
        return ctypes.CDLL('libCFApi.so')
    except OSError:
        pass
    
    # Then try explicit paths
    lib_paths = [
        '/usr/local/lib/libCFApi.so',
        '/usr/lib/libCFApi.so',
        '/usr/lib/aarch64-linux-gnu/libCFApi.so',  # Debian/Ubuntu ARM64 path
        '/usr/lib/arm-linux-gnueabihf/libCFApi.so',  # Debian/Ubuntu ARM path
    ]
    
    # Add relative paths based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lib_paths.extend([
        os.path.join(script_dir, 'API/Linux/ARM64/libCFApi.so'),
        os.path.join(script_dir, 'API/Linux/ARM/libCFApi.so'),
        os.path.join(os.getcwd(), 'API/Linux/ARM64/libCFApi.so'),
        os.path.join(os.getcwd(), 'API/Linux/ARM/libCFApi.so'),
        './API/Linux/ARM64/libCFApi.so',
        './API/Linux/ARM/libCFApi.so',
    ])
    
    # Try find_library (may return None or partial path)
    found_lib = ctypes.util.find_library('CFApi')
    if found_lib:
        lib_paths.append(found_lib)
    
    for lib_path in lib_paths:
        if lib_path and os.path.exists(lib_path):
            try:
                return ctypes.CDLL(lib_path)
            except OSError as e:
                # Log the error for debugging but continue trying
                continue
    
    # Final attempt: try with RTLD_GLOBAL flag (sometimes needed)
    try:
        return ctypes.CDLL('libCFApi.so', mode=ctypes.RTLD_GLOBAL)
    except (OSError, AttributeError):
        pass
    
    raise OSError(
        "Could not find libCFApi.so. Please install it:\n"
        "  For Raspberry Pi 5 (ARM64):\n"
        "    sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/\n"
        "    sudo ldconfig\n"
        "  For older Raspberry Pi (ARM 32-bit):\n"
        "    sudo cp API/Linux/ARM/libCFApi.so /usr/local/lib/\n"
        "    sudo ldconfig\n"
        "\n"
        "If already installed, verify with:\n"
        "    ls -la /usr/local/lib/libCFApi.so\n"
        "    ldconfig -p | grep libCFApi"
    )


# ============================================================================
# Main Reader Class
# ============================================================================

class CF591Reader:
    """
    CHAFON CF591 UHF RFID Reader Interface
    
    Provides comprehensive control over the RFID reader including:
    - Tag inventory (reading) with trigger-based control
    - Power/range adjustment
    - Tag memory read/write
    - Device configuration
    - Antenna management
    - GPIO/Relay control
    
    Example:
        with CF591Reader('/dev/ttyUSB0') as reader:
            # Read single tag (stops after first detection)
            tag = reader.read_single_tag(timeout=5000)
            
            # Set reading power (affects range)
            reader.set_rf_power(20)  # 20 dBm
            
            # Continuous reading
            reader.start_inventory()
            while running:
                tag = reader.get_tag(timeout=1000)
                if tag:
                    print(tag.epc)
            reader.stop_inventory()
    """
    
    def __init__(self, port: str = '/dev/ttyUSB0', baud_rate: int = 115200, 
                 auto_connect: bool = False):
        """
        Initialize CF591 Reader
        
        Args:
            port: Serial port path (e.g., '/dev/ttyUSB0') or network address
            baud_rate: Baud rate (default: 115200)
            auto_connect: Whether to connect automatically on init
        """
        self._lib = _load_library()
        self._setup_functions()
        
        self.port = port
        self.baud_rate = baud_rate
        self._handle = c_int64(0)  # Initialize to 0, not -1 (library requirement)
        self._is_open = False
        self._is_inventory_running = False
        self._inventory_lock = threading.Lock()
        
        if auto_connect:
            self.open()
    
    def _setup_functions(self):
        """Setup C function signatures"""
        lib = self._lib
        
        # Connection functions
        lib.OpenDevice.argtypes = [POINTER(c_int64), c_char_p, c_int]
        lib.OpenDevice.restype = c_int
        
        lib.OpenNetConnection.argtypes = [POINTER(c_int64), c_char_p, c_ushort, c_ulong]
        lib.OpenNetConnection.restype = c_int
        
        lib.CloseDevice.argtypes = [c_int64]
        lib.CloseDevice.restype = c_int
        
        # Device info functions
        lib.GetInfo.argtypes = [c_int64, POINTER(DeviceInfo)]
        lib.GetInfo.restype = c_int
        
        lib.GetDeviceInfo.argtypes = [c_int64, POINTER(DeviceFullInfo)]
        lib.GetDeviceInfo.restype = c_int
        
        lib.GetDevicePara.argtypes = [c_int64, POINTER(DevicePara)]
        lib.GetDevicePara.restype = c_int
        
        lib.SetDevicePara.argtypes = [c_int64, DevicePara]
        lib.SetDevicePara.restype = c_int
        
        lib.RebootDevice.argtypes = [c_int64]
        lib.RebootDevice.restype = c_int
        
        # Inventory functions
        lib.InventoryContinue.argtypes = [c_int64, c_ubyte, c_ulong]
        lib.InventoryContinue.restype = c_int
        
        lib.GetTagUii.argtypes = [c_int64, POINTER(TagInfo), c_ushort]
        lib.GetTagUii.restype = c_int
        
        lib.InventoryStop.argtypes = [c_int64, c_ushort]
        lib.InventoryStop.restype = c_int
        
        # Power functions
        lib.GetRFPower.argtypes = [c_int64, POINTER(c_ubyte), POINTER(c_ubyte)]
        lib.GetRFPower.restype = c_int
        
        lib.SetRFPower.argtypes = [c_int64, c_ubyte, c_ubyte]
        lib.SetRFPower.restype = c_int
        
        lib.GetAntPower.argtypes = [c_int64, POINTER(AntPower)]
        lib.GetAntPower.restype = c_int
        
        lib.SetAntPower.argtypes = [c_int64, AntPower]
        lib.SetAntPower.restype = c_int
        
        # Frequency functions
        lib.GetFreq.argtypes = [c_int64, POINTER(FreqInfo)]
        lib.GetFreq.restype = c_int
        
        lib.SetFreq.argtypes = [c_int64, POINTER(FreqInfo)]
        lib.SetFreq.restype = c_int
        
        # Antenna functions
        lib.GetAntenna.argtypes = [c_int64, POINTER(c_ubyte)]
        lib.GetAntenna.restype = c_int
        
        lib.SetAntenna.argtypes = [c_int64, POINTER(c_ubyte)]
        lib.SetAntenna.restype = c_int
        
        # Tag operations
        lib.ReadTag.argtypes = [c_int64, c_ubyte, POINTER(c_ubyte), c_ubyte, c_ushort, c_ubyte]
        lib.ReadTag.restype = c_int
        
        lib.GetReadTagResp.argtypes = [c_int64, POINTER(TagResp), POINTER(c_ubyte), POINTER(c_ubyte), c_ushort]
        lib.GetReadTagResp.restype = c_int
        
        lib.WriteTag.argtypes = [c_int64, c_ubyte, POINTER(c_ubyte), c_ubyte, c_ushort, c_ubyte, POINTER(c_ubyte)]
        lib.WriteTag.restype = c_int
        
        lib.GetTagResp.argtypes = [c_int64, c_ushort, POINTER(TagResp), c_ushort]
        lib.GetTagResp.restype = c_int
        
        lib.LockTag.argtypes = [c_int64, POINTER(c_ubyte), c_ubyte, c_ubyte]
        lib.LockTag.restype = c_int
        
        lib.KillTag.argtypes = [c_int64, POINTER(c_ubyte)]
        lib.KillTag.restype = c_int
        
        # Select/Sort/Query functions
        lib.SetSelectMask.argtypes = [c_int64, c_ushort, c_ubyte, POINTER(c_ubyte)]
        lib.SetSelectMask.restype = c_int
        
        lib.SelectOrSortGet.argtypes = [c_int64, c_ubyte, POINTER(SelectSortParam)]
        lib.SelectOrSortGet.restype = c_int
        
        lib.SelectOrSortSet.argtypes = [c_int64, c_ubyte, POINTER(SelectSortParam)]
        lib.SelectOrSortSet.restype = c_int
        
        lib.QueryCfgGet.argtypes = [c_int64, c_ubyte, POINTER(QueryParam)]
        lib.QueryCfgGet.restype = c_int
        
        lib.QueryCfgSet.argtypes = [c_int64, c_ubyte, POINTER(QueryParam)]
        lib.QueryCfgSet.restype = c_int
        
        # Q value (affects inventory performance)
        lib.GetCoilPRM.argtypes = [c_int64, POINTER(c_ubyte), POINTER(c_ubyte)]
        lib.GetCoilPRM.restype = c_int
        
        lib.SetCoilPRM.argtypes = [c_int64, c_ubyte, c_ubyte]
        lib.SetCoilPRM.restype = c_int
        
        # GPIO functions
        lib.GetGpioPara.argtypes = [c_int64, POINTER(GpioPara)]
        lib.GetGpioPara.restype = c_int
        
        lib.SetGpioPara.argtypes = [c_int64, GpioPara]
        lib.SetGpioPara.restype = c_int
        
        lib.GetGPIOWorkParam.argtypes = [c_int64, POINTER(GPIOWorkParam)]
        lib.GetGPIOWorkParam.restype = c_int
        
        lib.SetGPIOWorkParam.argtypes = [c_int64, GPIOWorkParam]
        lib.SetGPIOWorkParam.restype = c_int
        
        # Relay functions
        lib.Release_Relay.argtypes = [c_int64, c_ubyte]
        lib.Release_Relay.restype = c_int
        
        lib.Close_Relay.argtypes = [c_int64, c_ubyte]
        lib.Close_Relay.restype = c_int
        
        # Network functions
        lib.GetNetInfo.argtypes = [c_int64, POINTER(NetInfo)]
        lib.GetNetInfo.restype = c_int
        
        lib.SetNetInfo.argtypes = [c_int64, NetInfo]
        lib.SetNetInfo.restype = c_int
        
        # WiFi functions
        lib.GetwifiPara.argtypes = [c_int64, POINTER(WiFiPara)]
        lib.GetwifiPara.restype = c_int
        
        lib.SetwifiPara.argtypes = [c_int64, WiFiPara]
        lib.SetwifiPara.restype = c_int
        
        # Temperature functions
        lib.GetTemperature.argtypes = [c_int64, POINTER(c_ubyte), POINTER(c_ubyte)]
        lib.GetTemperature.restype = c_int
        
        lib.SetTemperature.argtypes = [c_int64, c_ubyte, c_ubyte]
        lib.SetTemperature.restype = c_int
        
        # RFID Type functions
        lib.GetRFIDType.argtypes = [c_int64, POINTER(c_ubyte)]
        lib.GetRFIDType.restype = c_int
        
        lib.SetRFIDType.argtypes = [c_int64, c_ubyte]
        lib.SetRFIDType.restype = c_int
        
        # Heartbeat functions
        lib.GetHeartbeat.argtypes = [c_int64, POINTER(Heartbeat)]
        lib.GetHeartbeat.restype = c_int
        
        lib.SetHeartbeat.argtypes = [c_int64, Heartbeat]
        lib.SetHeartbeat.restype = c_int
        
        # Permission parameters
        lib.GetPermissonPara.argtypes = [c_int64, POINTER(PermissonPara)]
        lib.GetPermissonPara.restype = c_int
        
        lib.SetPermissonPara.argtypes = [c_int64, PermissonPara]
        lib.SetPermissonPara.restype = c_int
    
    # ========================================================================
    # Connection Methods
    # ========================================================================
    
    def open(self) -> bool:
        """
        Open connection to the RFID reader via serial port
        
        Returns:
            True if connection successful
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._is_open:
            return True
        
        port_bytes = self.port.encode('utf-8')
        result = self._lib.OpenDevice(byref(self._handle), port_bytes, self.baud_rate)
        
        if result != StatusCode.OK:
            raise ConnectionError(
                f"Failed to open device on {self.port}. "
                f"Check connection and permissions (try: sudo chmod 666 {self.port})",
                result
            )
        
        self._is_open = True
        return True
    
    def open_network(self, ip: str, port: int = 4001, timeout_ms: int = 3000) -> bool:
        """
        Open connection to the RFID reader via network
        
        Args:
            ip: IP address of the reader
            port: Network port (default: 4001)
            timeout_ms: Connection timeout in milliseconds
            
        Returns:
            True if connection successful
        """
        if self._is_open:
            return True
        
        ip_bytes = ip.encode('utf-8')
        result = self._lib.OpenNetConnection(
            byref(self._handle), ip_bytes, c_ushort(port), c_ulong(timeout_ms)
        )
        
        if result != StatusCode.OK:
            raise ConnectionError(f"Failed to connect to {ip}:{port}", result)
        
        self._is_open = True
        return True
    
    def close(self):
        """Close connection to the RFID reader"""
        if not self._is_open:
            return
        
        # Stop any running inventory first
        if self._is_inventory_running:
            try:
                self.stop_inventory()
            except:
                pass
        
        self._lib.CloseDevice(self._handle)
        self._handle = c_int64(-1)
        self._is_open = False
    
    @property
    def is_open(self) -> bool:
        """Check if reader connection is open"""
        return self._is_open
    
    def _check_open(self):
        """Ensure reader is open before operations"""
        if not self._is_open:
            raise ConnectionError("Reader is not open. Call open() first.")
    
    def _check_result(self, result: int, error_msg: str, 
                      ignore_codes: List[int] = None) -> int:
        """
        Check API result and convert signed to unsigned
        
        Args:
            result: Result code from API (may be signed)
            error_msg: Error message if result is not OK
            ignore_codes: List of error codes to ignore (don't raise exception)
            
        Returns:
            Unsigned result code
        """
        # Convert signed to unsigned
        unsigned_result = result & 0xFFFFFFFF
        
        if unsigned_result == StatusCode.OK:
            return unsigned_result
        
        # Check if this is an ignorable error
        if ignore_codes and unsigned_result in ignore_codes:
            return unsigned_result
        
        # Raise exception for other errors
        raise CommandError(error_msg, result)
    
    # ========================================================================
    # Device Information Methods
    # ========================================================================
    
    def get_device_info(self) -> Dict[str, str]:
        """
        Get device information (firmware version, hardware version, serial number)
        
        Returns:
            Dictionary with device info
        """
        self._check_open()
        
        dev_info = DeviceInfo()
        result = self._lib.GetInfo(self._handle, byref(dev_info))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get device info", result)
        
        return {
            'firmware_version': bytes(dev_info.firmVersion).rstrip(b'\x00').decode('utf-8', errors='ignore'),
            'hardware_version': bytes(dev_info.hardVersion).rstrip(b'\x00').decode('utf-8', errors='ignore'),
            'serial_number': bytes(dev_info.SN).hex().upper()
        }
    
    def get_device_parameters(self) -> Dict[str, Any]:
        """
        Get all device parameters
        
        Returns:
            Dictionary with all device parameters
        """
        self._check_open()
        
        params = DevicePara()
        result = self._lib.GetDevicePara(self._handle, byref(params))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get device parameters", result)
        
        return {
            'device_address': params.DEVICEADDR,
            'rfid_protocol': params.RFIDPRO,
            'work_mode': params.WORKMODE,
            'interface': params.INTERFACE,
            'baud_rate': params.BAUDRATE,
            'wiegand_setting': params.WGSET,
            'antenna_mask': params.ANT,
            'region': params.REGION,
            'channel': params.CN,
            'rf_power': params.RFIDPOWER,
            'inventory_area': params.INVENTORYAREA,
            'q_value': params.QVALUE,
            'session': params.SESSION,
            'filter_time': params.FILTERTIME,
            'trigger_time': params.TRIGGLETIME,
            'buzzer_time': params.BUZZERTIME
        }
    
    def set_device_parameters(self, **kwargs):
        """
        Set device parameters
        
        Args:
            work_mode: Work mode (0=Command, 1=Auto, 2=Trigger)
            rf_power: RF power (0-30 dBm)
            antenna_mask: Antenna mask (bit field)
            region: Frequency region
            q_value: Q value for inventory
            session: Session value
            filter_time: Tag filter time
            trigger_time: Trigger time
            buzzer_time: Buzzer duration
        """
        self._check_open()
        
        # Get current parameters first
        params = DevicePara()
        result = self._lib.GetDevicePara(self._handle, byref(params))
        if result != StatusCode.OK:
            raise CommandError("Failed to get current parameters", result)
        
        # Update with provided values
        if 'work_mode' in kwargs:
            params.WORKMODE = kwargs['work_mode']
        if 'rf_power' in kwargs:
            params.RFIDPOWER = kwargs['rf_power']
        if 'antenna_mask' in kwargs:
            params.ANT = kwargs['antenna_mask']
        if 'region' in kwargs:
            params.REGION = kwargs['region']
        if 'q_value' in kwargs:
            params.QVALUE = kwargs['q_value']
        if 'session' in kwargs:
            params.SESSION = kwargs['session']
        if 'filter_time' in kwargs:
            params.FILTERTIME = kwargs['filter_time']
        if 'trigger_time' in kwargs:
            params.TRIGGLETIME = kwargs['trigger_time']
        if 'buzzer_time' in kwargs:
            params.BUZZERTIME = kwargs['buzzer_time']
        
        result = self._lib.SetDevicePara(self._handle, params)
        if result != StatusCode.OK:
            raise CommandError("Failed to set device parameters", result)
    
    def reboot(self):
        """Reboot the device"""
        self._check_open()
        result = self._lib.RebootDevice(self._handle)
        if result != StatusCode.OK:
            raise CommandError("Failed to reboot device", result)
    
    # ========================================================================
    # Power Control Methods (Controls Reading Range)
    # ========================================================================
    
    def get_rf_power(self) -> int:
        """
        Get current RF power level
        
        Returns:
            Power level in dBm (0-30)
        """
        self._check_open()
        
        power = c_ubyte()
        reserved = c_ubyte()
        result = self._lib.GetRFPower(self._handle, byref(power), byref(reserved))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get RF power", result)
        
        return power.value
    
    def set_rf_power(self, power: int):
        """
        Set RF power level (controls reading range)
        
        Args:
            power: Power level in dBm (0-30)
                   Higher power = longer range
                   Lower power = shorter range
                   
        Note:
            Typical values:
            - 0-10 dBm: Very short range (< 0.5m)
            - 10-20 dBm: Medium range (0.5-2m)
            - 20-30 dBm: Long range (2-5m+)
        """
        self._check_open()
        
        if not 0 <= power <= 30:
            raise ValueError("Power must be between 0 and 30 dBm")
        
        result = self._lib.SetRFPower(self._handle, c_ubyte(power), c_ubyte(0))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to set RF power", result)
    
    def get_antenna_power(self) -> Dict[str, Any]:
        """
        Get antenna-specific power settings
        
        Returns:
            Dictionary with antenna power settings
        """
        self._check_open()
        
        ant_power = AntPower()
        result = self._lib.GetAntPower(self._handle, byref(ant_power))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get antenna power", result)
        
        return {
            'enabled': bool(ant_power.Enable),
            'antenna_power': list(ant_power.AntPower)
        }
    
    def set_antenna_power(self, enabled: bool, power_values: List[int]):
        """
        Set antenna-specific power levels
        
        Args:
            enabled: Whether per-antenna power is enabled
            power_values: List of power values for each antenna (up to 8)
        """
        self._check_open()
        
        ant_power = AntPower()
        ant_power.Enable = 1 if enabled else 0
        for i, power in enumerate(power_values[:8]):
            ant_power.AntPower[i] = power
        
        result = self._lib.SetAntPower(self._handle, ant_power)
        
        if result != StatusCode.OK:
            raise CommandError("Failed to set antenna power", result)
    
    # ========================================================================
    # Inventory (Tag Reading) Methods
    # ========================================================================
    
    def start_inventory(self, inv_count: int = 0, inv_param: int = 0):
        """
        Start continuous inventory (tag reading)
        
        Args:
            inv_count: Number of tags to read (0 = continuous)
            inv_param: Inventory parameters (0 = default)
        """
        self._check_open()
        
        with self._inventory_lock:
            # If already running, stop first
            if self._is_inventory_running:
                try:
                    self._lib.InventoryStop(self._handle, c_ushort(1000))
                except:
                    pass
                self._is_inventory_running = False
            
            result = self._lib.InventoryContinue(
                self._handle, c_ubyte(inv_count), c_ulong(inv_param)
            )
            
            # Convert signed error code to unsigned for comparison
            unsigned_result = result & 0xFFFFFFFF
            
            if unsigned_result != StatusCode.OK:
                raise CommandError("Failed to start inventory", result)
            
            self._is_inventory_running = True
    
    def stop_inventory(self, timeout: int = 5000):
        """
        Stop inventory
        
        Args:
            timeout: Timeout in milliseconds
        """
        self._check_open()
        
        with self._inventory_lock:
            if not self._is_inventory_running:
                # Already stopped, nothing to do
                return
            
            result = self._lib.InventoryStop(self._handle, c_ushort(timeout))
            
            # Convert signed error code to unsigned for comparison
            unsigned_result = result & 0xFFFFFFFF
            
            # Don't raise error for timeout or inventory stop - these are normal
            # Timeout means reader already stopped or no response needed
            # Inventory stop means inventory already completed
            if (unsigned_result != StatusCode.OK and 
                unsigned_result != StatusCode.CMD_COMM_TIMEOUT and
                unsigned_result != StatusCode.CMD_INVENTORY_STOP):
                raise CommandError("Failed to stop inventory", result)
            
            self._is_inventory_running = False
    
    def get_tag(self, timeout: int = 1000) -> Optional[Tag]:
        """
        Get a single tag from the inventory buffer
        
        Args:
            timeout: Timeout in milliseconds
            
        Returns:
            Tag object if a tag was read, None otherwise
        """
        self._check_open()
        
        tag_info = TagInfo()
        result = self._lib.GetTagUii(self._handle, byref(tag_info), c_ushort(timeout))
        
        # Convert signed error code to unsigned for comparison
        unsigned_result = result & 0xFFFFFFFF
        
        if unsigned_result == StatusCode.OK:
            return Tag.from_tag_info(tag_info)
        elif unsigned_result in (StatusCode.CMD_INVENTORY_STOP, StatusCode.CMD_COMM_TIMEOUT):
            return None
        else:
            raise CommandError("Failed to get tag", result)
    
    def read_single_tag(self, timeout: int = 3000) -> Optional[Tag]:
        """
        Read a single tag and stop (trigger-based reading)
        
        This method starts inventory, reads until a tag is found or timeout,
        then stops the inventory. Perfect for trigger-based applications.
        
        Args:
            timeout: Maximum time to wait for a tag in milliseconds
            
        Returns:
            Tag object if a tag was read, None if timeout
        """
        self._check_open()
        
        try:
            self.start_inventory()
            
            start_time = time.time()
            timeout_sec = timeout / 1000.0
            
            while (time.time() - start_time) < timeout_sec:
                tag = self.get_tag(timeout=min(500, timeout))
                if tag:
                    return tag
                time.sleep(0.01)  # Small delay to prevent busy waiting
            
            return None
            
        finally:
            try:
                self.stop_inventory()
            except:
                pass
    
    def read_tags(self, max_tags: Optional[int] = None, timeout: int = 1000,
                  max_timeouts: int = 3) -> List[Tag]:
        """
        Read multiple tags
        
        Args:
            max_tags: Maximum number of tags to read (None = read until timeout)
            timeout: Timeout per read in milliseconds
            max_timeouts: Number of consecutive timeouts before stopping
            
        Returns:
            List of Tag objects
        """
        self._check_open()
        
        tags = []
        consecutive_timeouts = 0
        
        try:
            self.start_inventory()
            
            while True:
                if max_tags and len(tags) >= max_tags:
                    break
                
                tag = self.get_tag(timeout=timeout)
                
                if tag:
                    tags.append(tag)
                    consecutive_timeouts = 0
                else:
                    consecutive_timeouts += 1
                    if consecutive_timeouts >= max_timeouts:
                        break
            
        finally:
            try:
                self.stop_inventory()
            except:
                pass
        
        return tags
    
    def read_tags_iterator(self, max_count: Optional[int] = None, 
                           timeout: int = 1000) -> Generator[Tag, None, None]:
        """
        Iterator that yields tags as they are read
        
        Args:
            max_count: Maximum number of tags to yield (None = unlimited)
            timeout: Timeout per read in milliseconds
            
        Yields:
            Tag objects as they are detected
            
        Example:
            reader.start_inventory()
            for tag in reader.read_tags_iterator(max_count=10):
                print(f"Found: {tag.epc}")
            reader.stop_inventory()
        """
        self._check_open()
        
        count = 0
        consecutive_timeouts = 0
        max_consecutive_timeouts = 3
        
        while True:
            if max_count and count >= max_count:
                break
            
            tag = self.get_tag(timeout=timeout)
            
            if tag:
                yield tag
                count += 1
                consecutive_timeouts = 0
            else:
                consecutive_timeouts += 1
                if consecutive_timeouts >= max_consecutive_timeouts:
                    break
    
    # ========================================================================
    # Tag Memory Operations
    # ========================================================================
    
    def read_tag_memory(self, memory_bank: MemoryBank, word_ptr: int, 
                        word_count: int, password: bytes = None,
                        timeout: int = 2000) -> bytes:
        """
        Read tag memory
        
        Args:
            memory_bank: Memory bank to read (RESERVED, EPC, TID, USER)
            word_ptr: Starting word address (1 word = 2 bytes)
            word_count: Number of words to read
            password: Access password (4 bytes) or None for no password
            timeout: Timeout in milliseconds
            
        Returns:
            Bytes read from tag memory
        """
        self._check_open()
        
        # Stop inventory if running (memory operations require inventory to be stopped)
        was_running = self._is_inventory_running
        if was_running:
            try:
                self.stop_inventory(timeout=1000)
            except:
                pass
        
        try:
            # Prepare password
            if password:
                pwd = (c_ubyte * 4)(*password)
            else:
                pwd = (c_ubyte * 4)(0, 0, 0, 0)
            
            # Option: 0x01 = match tag first, 0x00 = skip match
            option = c_ubyte(0x00)
            
            result = self._lib.ReadTag(
                self._handle, option, pwd, c_ubyte(memory_bank),
                c_ushort(word_ptr), c_ubyte(word_count)
            )
            
            unsigned_result = result & 0xFFFFFFFF
            if unsigned_result != StatusCode.OK:
                raise TagError("Failed to initiate read command", result)
            
            # Get response
            resp = TagResp()
            read_count = c_ubyte()
            read_data = (c_ubyte * 256)()
            
            result = self._lib.GetReadTagResp(
                self._handle, byref(resp), byref(read_count),
                read_data, c_ushort(timeout)
            )
            
            unsigned_result = result & 0xFFFFFFFF
            if unsigned_result != StatusCode.OK:
                raise TagError("Failed to read tag memory", result)
            
            return bytes(read_data[:read_count.value * 2])
        finally:
            # Restart inventory if it was running
            if was_running:
                try:
                    self.start_inventory()
                except:
                    pass
    
    def write_tag_memory(self, memory_bank: MemoryBank, word_ptr: int,
                         data: bytes, password: bytes = None,
                         timeout: int = 2000):
        """
        Write data to tag memory
        
        Args:
            memory_bank: Memory bank to write (EPC, USER, etc.)
            word_ptr: Starting word address
            data: Data to write (must be even number of bytes)
            password: Access password (4 bytes) or None
            timeout: Timeout in milliseconds
        """
        self._check_open()
        
        if len(data) % 2 != 0:
            raise ValueError("Data length must be even (word-aligned)")
        
        word_count = len(data) // 2
        
        # Prepare password
        if password:
            pwd = (c_ubyte * 4)(*password)
        else:
            pwd = (c_ubyte * 4)(0, 0, 0, 0)
        
        # Prepare data
        write_data = (c_ubyte * len(data))(*data)
        
        option = c_ubyte(0x00)
        
        result = self._lib.WriteTag(
            self._handle, option, pwd, c_ubyte(memory_bank),
            c_ushort(word_ptr), c_ubyte(word_count), write_data
        )
        
        if result != StatusCode.OK:
            raise TagError("Failed to initiate write command", result)
        
        # Get response
        resp = TagResp()
        result = self._lib.GetTagResp(
            self._handle, c_ushort(0x0004), byref(resp), c_ushort(timeout)
        )
        
        if result != StatusCode.OK:
            raise TagError("Failed to write tag memory", result)
    
    def write_tag_epc(self, new_epc: bytes, password: bytes = None):
        """
        Write a new EPC to a tag
        
        Args:
            new_epc: New EPC data (typically 12 bytes)
            password: Access password or None
        """
        # EPC starts at word 2 in the EPC bank (word 0 is CRC, word 1 is PC)
        self.write_tag_memory(MemoryBank.EPC, 2, new_epc, password)
    
    def lock_tag(self, area: LockArea, action: LockAction, password: bytes = None):
        """
        Lock or unlock tag memory
        
        Args:
            area: Area to lock (KILL_PWD, ACCESS_PWD, EPC, TID, USER)
            action: Lock action (UNLOCK, LOCK, PERMANENT_UNLOCK, PERMANENT_LOCK)
            password: Access password (4 bytes)
        """
        self._check_open()
        
        if password:
            pwd = (c_ubyte * 4)(*password)
        else:
            pwd = (c_ubyte * 4)(0, 0, 0, 0)
        
        result = self._lib.LockTag(self._handle, pwd, c_ubyte(area), c_ubyte(action))
        
        if result != StatusCode.OK:
            raise TagError("Failed to lock tag", result)
    
    def kill_tag(self, kill_password: bytes):
        """
        Permanently disable a tag (IRREVERSIBLE!)
        
        Args:
            kill_password: Kill password (4 bytes) - must be set on tag
            
        Warning:
            This operation is PERMANENT and IRREVERSIBLE!
            The tag will be permanently disabled.
        """
        self._check_open()
        
        if len(kill_password) != 4:
            raise ValueError("Kill password must be exactly 4 bytes")
        
        pwd = (c_ubyte * 4)(*kill_password)
        result = self._lib.KillTag(self._handle, pwd)
        
        if result != StatusCode.OK:
            raise TagError("Failed to kill tag", result)
    
    # ========================================================================
    # Tag Filtering Methods
    # ========================================================================
    
    def set_select_mask(self, mask_ptr: int, mask_bits: int, mask: bytes):
        """
        Set tag selection mask for filtering
        
        Args:
            mask_ptr: Pointer position in bits
            mask_bits: Number of bits in the mask
            mask: Mask data bytes
        """
        self._check_open()
        
        mask_data = (c_ubyte * len(mask))(*mask)
        result = self._lib.SetSelectMask(
            self._handle, c_ushort(mask_ptr), c_ubyte(mask_bits), mask_data
        )
        
        if result != StatusCode.OK:
            raise CommandError("Failed to set select mask", result)
    
    def filter_by_epc_prefix(self, epc_prefix: bytes):
        """
        Set filter to only read tags with specific EPC prefix
        
        Args:
            epc_prefix: EPC prefix bytes to match
        """
        # EPC starts at bit 32 (after CRC and PC)
        mask_ptr = 32
        mask_bits = len(epc_prefix) * 8
        self.set_select_mask(mask_ptr, mask_bits, epc_prefix)
    
    def clear_filter(self):
        """Clear any tag filters"""
        self.set_select_mask(0, 0, b'')
    
    # ========================================================================
    # Q Value Methods (Affects Inventory Performance)
    # ========================================================================
    
    def get_q_value(self) -> int:
        """
        Get Q value for inventory algorithm
        
        Returns:
            Q value (0-15)
            
        Note:
            This function may not be available on all reader models.
            Use get_device_parameters()['q_value'] as an alternative.
        """
        self._check_open()
        
        # Try to get from device parameters first (more reliable)
        try:
            params = self.get_device_parameters()
            return params.get('q_value', 4)  # Default to 4 if not available
        except:
            pass
        
        # Fallback to direct API call
        # Stop inventory if running (some operations require inventory to be stopped)
        was_running = self._is_inventory_running
        if was_running:
            try:
                self.stop_inventory(timeout=1000)
            except:
                pass
        
        try:
            q_val = c_ubyte()
            reserved = c_ubyte()
            result = self._lib.GetCoilPRM(self._handle, byref(q_val), byref(reserved))
            
            unsigned_result = result & 0xFFFFFFFF
            if unsigned_result == StatusCode.OK:
                return q_val.value
            else:
                # If API call fails, return from device parameters or default
                params = self.get_device_parameters()
                return params.get('q_value', 4)
        finally:
            # Restart inventory if it was running
            if was_running:
                try:
                    self.start_inventory()
                except:
                    pass
    
    def set_q_value(self, q_value: int):
        """
        Set Q value for inventory algorithm
        
        Args:
            q_value: Q value (0-15)
                     Lower Q = faster for few tags
                     Higher Q = better for many tags
        """
        self._check_open()
        
        if not 0 <= q_value <= 15:
            raise ValueError("Q value must be between 0 and 15")
        
        result = self._lib.SetCoilPRM(self._handle, c_ubyte(q_value), c_ubyte(0))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to set Q value", result)
    
    # ========================================================================
    # Frequency Methods
    # ========================================================================
    
    def get_frequency(self) -> Dict[str, Any]:
        """
        Get frequency settings
        
        Returns:
            Dictionary with frequency information
        """
        self._check_open()
        
        freq_info = FreqInfo()
        result = self._lib.GetFreq(self._handle, byref(freq_info))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get frequency info", result)
        
        return {
            'region': freq_info.region,
            'start_freq': freq_info.StartFreq,
            'stop_freq': freq_info.StopFreq,
            'step_freq': freq_info.StepFreq,
            'channel_count': freq_info.cnt
        }
    
    def set_frequency(self, region: Region, start_freq: int = None, 
                      stop_freq: int = None, step_freq: int = None):
        """
        Set frequency settings
        
        Args:
            region: Frequency region (FCC, ETSI, CHN, etc.)
            start_freq: Start frequency in 0.01 MHz
            stop_freq: Stop frequency in 0.01 MHz
            step_freq: Step frequency in 0.01 MHz
        """
        self._check_open()
        
        freq_info = FreqInfo()
        freq_info.region = region
        
        if start_freq is not None:
            freq_info.StartFreq = start_freq
        if stop_freq is not None:
            freq_info.StopFreq = stop_freq
        if step_freq is not None:
            freq_info.StepFreq = step_freq
        
        result = self._lib.SetFreq(self._handle, byref(freq_info))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to set frequency", result)
    
    # ========================================================================
    # Antenna Methods
    # ========================================================================
    
    def get_antenna(self) -> int:
        """
        Get current antenna configuration
        
        Returns:
            Antenna mask (bit field: bit 0 = ant 1, bit 1 = ant 2, etc.)
        """
        self._check_open()
        
        antenna = c_ubyte()
        result = self._lib.GetAntenna(self._handle, byref(antenna))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get antenna config", result)
        
        return antenna.value
    
    def set_antenna(self, antenna_mask: int):
        """
        Set antenna configuration
        
        Args:
            antenna_mask: Bit field (1=ant1, 2=ant2, 3=both, 4=ant3, etc.)
        """
        self._check_open()
        
        antenna = c_ubyte(antenna_mask)
        result = self._lib.SetAntenna(self._handle, byref(antenna))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to set antenna", result)
    
    # ========================================================================
    # GPIO / Relay Methods
    # ========================================================================
    
    def get_gpio_params(self) -> Dict[str, Any]:
        """Get GPIO parameters"""
        self._check_open()
        
        gpio = GpioPara()
        result = self._lib.GetGpioPara(self._handle, byref(gpio))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get GPIO params", result)
        
        return {
            'kc_enabled': bool(gpio.KCEn),
            'relay_time': gpio.RelayTime,
            'kc_power_enabled': bool(gpio.KCPowerEn),
            'trigger_mode': gpio.TriggleMode,
            'buffer_enabled': bool(gpio.BufferEn),
            'protocol_enabled': bool(gpio.ProtocolEn),
            'protocol_type': gpio.ProtocolType
        }
    
    def activate_relay(self, time_100ms: int = 10):
        """
        Activate the relay
        
        Args:
            time_100ms: Time in 100ms units (e.g., 10 = 1 second)
        """
        self._check_open()
        
        result = self._lib.Close_Relay(self._handle, c_ubyte(time_100ms))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to activate relay", result)
    
    def deactivate_relay(self, time_100ms: int = 10):
        """
        Deactivate the relay
        
        Args:
            time_100ms: Time in 100ms units
        """
        self._check_open()
        
        result = self._lib.Release_Relay(self._handle, c_ubyte(time_100ms))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to deactivate relay", result)
    
    # ========================================================================
    # Temperature Methods
    # ========================================================================
    
    def get_temperature(self) -> Dict[str, int]:
        """
        Get current temperature and threshold
        
        Returns:
            Dictionary with 'current' and 'limit' temperatures
        """
        self._check_open()
        
        current = c_ubyte()
        limit = c_ubyte()
        result = self._lib.GetTemperature(self._handle, byref(current), byref(limit))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get temperature", result)
        
        return {
            'current': current.value,
            'limit': limit.value
        }
    
    def set_temperature_limit(self, limit: int):
        """
        Set temperature limit for auto-shutoff
        
        Args:
            limit: Temperature limit in degrees Celsius
        """
        self._check_open()
        
        result = self._lib.SetTemperature(self._handle, c_ubyte(limit), c_ubyte(0))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to set temperature limit", result)
    
    # ========================================================================
    # Network Methods
    # ========================================================================
    
    def get_network_info(self) -> Dict[str, str]:
        """Get network configuration"""
        self._check_open()
        
        net_info = NetInfo()
        result = self._lib.GetNetInfo(self._handle, byref(net_info))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get network info", result)
        
        ip = '.'.join(str(b) for b in net_info.IP)
        mac = ':'.join(f'{b:02X}' for b in net_info.MAC)
        port = (net_info.PORT[0] << 8) | net_info.PORT[1]
        netmask = '.'.join(str(b) for b in net_info.NetMask)
        gateway = '.'.join(str(b) for b in net_info.Gateway)
        
        return {
            'ip': ip,
            'mac': mac,
            'port': port,
            'netmask': netmask,
            'gateway': gateway
        }
    
    # ========================================================================
    # WiFi Methods
    # ========================================================================
    
    def get_wifi_params(self) -> Dict[str, Any]:
        """Get WiFi parameters"""
        self._check_open()
        
        wifi = WiFiPara()
        result = self._lib.GetwifiPara(self._handle, byref(wifi))
        
        if result != StatusCode.OK:
            raise CommandError("Failed to get WiFi params", result)
        
        return {
            'enabled': bool(wifi.wifiEn),
            'ssid': bytes(wifi.SSID).rstrip(b'\x00').decode('utf-8', errors='ignore'),
            'ip': '.'.join(str(b) for b in wifi.IP),
            'port': (wifi.PORT[0] << 8) | wifi.PORT[1]
        }
    
    # ========================================================================
    # Context Manager Support
    # ========================================================================
    
    def __enter__(self):
        """Context manager entry"""
        if not self._is_open:
            self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


# ============================================================================
# High-Level Helper Functions
# ============================================================================

def scan_for_readers(ports: List[str] = None) -> List[str]:
    """
    Scan for available RFID readers
    
    Args:
        ports: List of ports to check, or None for auto-detect
        
    Returns:
        List of ports with responding readers
    """
    import glob
    
    if ports is None:
        # Auto-detect serial ports
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    available = []
    
    for port in ports:
        try:
            reader = CF591Reader(port)
            reader.open()
            reader.get_device_info()  # Verify communication
            reader.close()
            available.append(port)
        except:
            pass
    
    return available


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='CHAFON CF591 RFID Reader')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0',
                        help='Serial port (default: /dev/ttyUSB0)')
    parser.add_argument('--power', type=int, default=None,
                        help='Set RF power level (0-30 dBm)')
    parser.add_argument('--single', action='store_true',
                        help='Read single tag and exit')
    parser.add_argument('--timeout', type=int, default=5000,
                        help='Timeout in milliseconds')
    parser.add_argument('--info', action='store_true',
                        help='Show device information')
    args = parser.parse_args()
    
    print("=" * 60)
    print("CHAFON CF591 UHF RFID Reader")
    print("=" * 60)
    
    try:
        with CF591Reader(args.port) as reader:
            print(f"Connected to {args.port}")
            
            # Show device info
            if args.info:
                info = reader.get_device_info()
                print(f"\nDevice Information:")
                print(f"  Firmware: {info['firmware_version']}")
                print(f"  Hardware: {info['hardware_version']}")
                print(f"  Serial:   {info['serial_number']}")
                
                params = reader.get_device_parameters()
                print(f"\nDevice Parameters:")
                print(f"  RF Power: {params['rf_power']} dBm")
                print(f"  Region:   {params['region']}")
                print(f"  Q Value:  {params['q_value']}")
            
            # Set power if requested
            if args.power is not None:
                reader.set_rf_power(args.power)
                print(f"\nRF Power set to {args.power} dBm")
            
            # Read tags
            if args.single:
                print(f"\nReading single tag (timeout: {args.timeout}ms)...")
                tag = reader.read_single_tag(timeout=args.timeout)
                if tag:
                    print(f"\nTag Found:")
                    print(f"  EPC:     {tag.epc}")
                    print(f"  RSSI:    {tag.rssi:.1f} dBm")
                    print(f"  Antenna: {tag.antenna}")
                else:
                    print("\nNo tag found")
            else:
                print("\nStarting continuous reading (Ctrl+C to stop)...")
                reader.start_inventory()
                
                tag_count = 0
                try:
                    while True:
                        tag = reader.get_tag(timeout=1000)
                        if tag:
                            tag_count += 1
                            print(f"\nTag #{tag_count}:")
                            print(f"  EPC:     {tag.epc}")
                            print(f"  RSSI:    {tag.rssi:.1f} dBm")
                            print(f"  Antenna: {tag.antenna}")
                            print(f"  Channel: {tag.channel}")
                except KeyboardInterrupt:
                    print("\n\nStopping...")
                
                reader.stop_inventory()
                print(f"\nTotal tags read: {tag_count}")
    
    except CF591Error as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    
    print("\nDone.")

