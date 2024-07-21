#!/bin/bash

# Function to extract data units written from smart log
extract_data_units_written() {
    # $1 is the log file path
    grep "Data Units Written" $1 | awk '{print $5}'  # This extracts the raw value of data units written
}

# Function to extract physical media units written from ocp log
extract_physical_media_written() {
    # $1 is the log file path
    grep "Physical media units written" $1 | awk '{print $NF}'  # This extracts the last number in the line, which is the bytes count
}

# Calculate Delta WAF
calculate_delta_waf() {
    # $1 is initial data units written, $2 is final data units written
    # $3 is initial physical media units written, $4 is final physical media units written
    delta_host_writes=$(echo "($2 - $1) * 512 * 1000" | bc)
    if [ "$delta_host_writes" -eq 0 ]; then
        echo "Error: Delta host writes is zero, cannot divide by zero."
        exit 1
    fi
    delta_nand_writes=$(echo "$4 - $3" | bc)
    echo "scale=4; $delta_nand_writes / $delta_host_writes" | bc  # Using bc to perform floating point division
}

# Paths to the log files
SMART_BEFORE_LOG="/tmp/smart_before.log"
SMART_AFTER_LOG="/tmp/smart_after.log"
OCP_BEFORE_LOG="/tmp/ocp_before.log"
OCP_AFTER_LOG="/tmp/ocp_after.log"

# Extracting data units written and physical media units written
data_units_written_before=$(extract_data_units_written $SMART_BEFORE_LOG)
data_units_written_after=$(extract_data_units_written $SMART_AFTER_LOG)
physical_media_written_before=$(extract_physical_media_written $OCP_BEFORE_LOG)
physical_media_written_after=$(extract_physical_media_written $OCP_AFTER_LOG)

# Check if extraction is successful
if [ -z "$data_units_written_before" ] || [ -z "$data_units_written_after" ]; then
    echo "Error: Failed to extract data units written from SMART logs."
    exit 1
fi

if [ -z "$physical_media_written_before" ] || [ -z "$physical_media_written_after" ]; then
    echo "Error: Failed to extract physical media units written from OCP logs."
    exit 1
fi

# Calculate Delta WAF
delta_waf=$(calculate_delta_waf $data_units_written_before $data_units_written_after $physical_media_written_before $physical_media_written_after)

# Output results
echo "Write Amplification Factor (WAF):"
echo "WAF = $delta_waf"