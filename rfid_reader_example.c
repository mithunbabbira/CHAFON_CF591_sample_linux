/**
 * CHAFON CF591 RFID Reader Example for Raspberry Pi
 * 
 * This example demonstrates how to:
 * 1. Connect to the CF591 reader via serial port
 * 2. Start inventory (tag reading)
 * 3. Read RFID tags continuously
 * 4. Display tag information
 * 5. Stop and close the connection
 * 
 * Compilation:
 *   gcc -o rfid_reader rfid_reader_example.c -lCFApi -L./API/Linux/ARM -I./API/Linux
 * 
 * For ARM64:
 *   gcc -o rfid_reader rfid_reader_example.c -lCFApi -L./API/Linux/ARM64 -I./API/Linux
 * 
 * Usage:
 *   ./rfid_reader /dev/ttyUSB0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include "CFApi.h"

// Global variables for cleanup
static int64_t g_hComm = -1;
static volatile int g_running = 1;

// Signal handler for graceful shutdown
void signal_handler(int sig) {
    printf("\nStopping RFID reader...\n");
    g_running = 0;
}

// Convert byte array to hex string
void bytes_to_hex(unsigned char* data, int len, char* output) {
    int i;
    for (i = 0; i < len; i++) {
        sprintf(output + (i * 2), "%02X", data[i]);
    }
    output[len * 2] = '\0';
}

// Print tag information
void print_tag_info(TagInfo* tag) {
    char epc_hex[512];
    
    // Convert EPC code to hex string
    bytes_to_hex(tag->code, tag->codeLen, epc_hex);
    
    printf("Tag #%d:\n", tag->NO);
    printf("  EPC: %s\n", epc_hex);
    printf("  Length: %d bytes\n", tag->codeLen);
    printf("  RSSI: %d dBm\n", tag->rssi / 10);
    printf("  Antenna: %d\n", tag->antenna);
    printf("  Channel: %d\n", tag->channel);
    printf("  CRC: %02X %02X\n", tag->crc[0], tag->crc[1]);
    printf("  PC: %02X %02X\n", tag->pc[0], tag->pc[1]);
    printf("---\n");
}

int main(int argc, char* argv[]) {
    int result;
    char* port_name;
    int baud_rate = 115200;
    TagInfo tag_info;
    int tag_count = 0;
    
    // Setup signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Check command line arguments
    if (argc < 2) {
        printf("Usage: %s <serial_port> [baud_rate]\n", argv[0]);
        printf("Example: %s /dev/ttyUSB0 115200\n", argv[0]);
        return 1;
    }
    
    port_name = argv[1];
    if (argc >= 3) {
        baud_rate = atoi(argv[2]);
    }
    
    printf("CHAFON CF591 RFID Reader Example\n");
    printf("================================\n");
    printf("Port: %s\n", port_name);
    printf("Baud Rate: %d\n", baud_rate);
    printf("\n");
    
    // Step 1: Open device connection
    printf("Opening device...\n");
    result = OpenDevice(&g_hComm, port_name, baud_rate);
    if (result != STAT_OK) {
        printf("ERROR: Failed to open device. Error code: 0x%08X\n", result);
        if (result == STAT_PORT_OPEN_FAILED) {
            printf("Hint: Check if the device is connected and permissions are correct.\n");
            printf("      Try: sudo chmod 666 %s\n", port_name);
        }
        return 1;
    }
    printf("Device opened successfully!\n\n");
    
    // Step 2: Get device information (optional)
    DeviceInfo dev_info;
    memset(&dev_info, 0, sizeof(DeviceInfo));
    result = GetInfo(g_hComm, &dev_info);
    if (result == STAT_OK) {
        printf("Device Information:\n");
        printf("  Firmware Version: %s\n", dev_info.firmVersion);
        printf("  Hardware Version: %s\n", dev_info.hardVersion);
        printf("  Serial Number: ");
        for (int i = 0; i < 12; i++) {
            printf("%02X", dev_info.SN[i]);
        }
        printf("\n\n");
    }
    
    // Step 3: Start inventory
    printf("Starting inventory (tag reading)...\n");
    printf("Press Ctrl+C to stop\n\n");
    
    result = InventoryContinue(g_hComm, 0, 0);  // 0 = continuous mode
    if (result != STAT_OK) {
        printf("ERROR: Failed to start inventory. Error code: 0x%08X\n", result);
        CloseDevice(g_hComm);
        return 1;
    }
    
    // Step 4: Read tags in a loop
    printf("Reading tags...\n");
    printf("================================\n");
    
    while (g_running) {
        // Get tag information (timeout: 1000ms)
        result = GetTagUii(g_hComm, &tag_info, 1000);
        
        if (result == STAT_OK) {
            // Successfully read a tag
            tag_count++;
            print_tag_info(&tag_info);
        }
        else if (result == STAT_CMD_INVENTORY_STOP) {
            // No more tags or inventory stopped
            // This is normal - continue waiting for more tags
            continue;
        }
        else if (result == STAT_CMD_COMM_TIMEOUT) {
            // Timeout - no tags detected in this cycle
            // Continue waiting
            continue;
        }
        else {
            // Other error
            printf("ERROR: Failed to read tag. Error code: 0x%08X\n", result);
            if (result == STAT_CMD_COMM_RD_FAILED) {
                printf("Communication error. Check connection.\n");
                break;
            }
        }
        
        // Small delay to prevent CPU spinning
        usleep(10000);  // 10ms
    }
    
    // Step 5: Stop inventory
    printf("\nStopping inventory...\n");
    result = InventoryStop(g_hComm, 5000);  // 5 second timeout
    if (result != STAT_OK) {
        printf("Warning: Failed to stop inventory gracefully. Error code: 0x%08X\n", result);
    }
    
    // Step 6: Close device
    printf("Closing device...\n");
    result = CloseDevice(g_hComm);
    if (result != STAT_OK) {
        printf("Warning: Error closing device. Error code: 0x%08X\n", result);
    }
    
    printf("\nTotal tags read: %d\n", tag_count);
    printf("Done.\n");
    
    return 0;
}


