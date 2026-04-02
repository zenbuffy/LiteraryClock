#!/bin/bash

# Enable WiFi, wait for NTP sync, then disable WiFi
# Run this via cron just before the clock wakes (e.g. 05:55)
lipc-set-prop com.lab126.cmd wirelessEnable 1

# Wait for connection and NTP sync to complete
sleep 60

lipc-set-prop com.lab126.cmd wirelessEnable 0
