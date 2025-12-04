# Makefile for CHAFON CF591 RFID Reader on Raspberry Pi
# 
# Usage:
#   make          - Build for ARM (32-bit)
#   make ARM64=1  - Build for ARM64 (64-bit)
#   make clean    - Remove build files

# Default to ARM (32-bit) for older Raspberry Pi models
ARCH ?= ARM

# Detect architecture if ARM64 is specified
ifeq ($(ARM64),1)
    ARCH = ARM64
endif

# Library paths
LIB_DIR = API/Linux/$(ARCH)
INCLUDE_DIR = API/Linux
TARGET = rfid_reader
SOURCE = rfid_reader_example.c

# Compiler flags
CC = gcc
CFLAGS = -Wall -Wextra -O2
LDFLAGS = -lCFApi -L$(LIB_DIR) -I$(INCLUDE_DIR)

# Check if library exists
ifeq ($(wildcard $(LIB_DIR)/libCFApi.so),)
    $(error Library not found at $(LIB_DIR)/libCFApi.so. Please check your SDK installation.)
endif

.PHONY: all clean install

all: $(TARGET)

$(TARGET): $(SOURCE)
	@echo "Building for $(ARCH) architecture..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)
	@echo "Build complete! Run with: ./$(TARGET) /dev/ttyUSB0"

clean:
	rm -f $(TARGET)

install: $(TARGET)
	@echo "Installing library to /usr/local/lib..."
	sudo cp $(LIB_DIR)/libCFApi.so /usr/local/lib/
	sudo ldconfig
	@echo "Library installed successfully!"

help:
	@echo "CHAFON CF591 RFID Reader Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make          - Build for ARM (32-bit)"
	@echo "  make ARM64=1  - Build for ARM64 (64-bit)"
	@echo "  make clean    - Remove build files"
	@echo "  make install  - Install library to system"
	@echo ""
	@echo "Current architecture: $(ARCH)"
	@echo "Library path: $(LIB_DIR)"

