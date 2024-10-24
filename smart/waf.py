import subprocess
import json
import time
import csv

# Function to execute nvme command and return JSON output
def run_nvme_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr.decode())
        return None

# Function to calculate NAND writes and host writes
def calculate_writes(nvme_smart_log, nvme_ocp_log):
    if nvme_smart_log and nvme_ocp_log:
        nand_writes = nvme_ocp_log["Physical media units written"]["lo"]
        host_writes = nvme_smart_log["data_units_written"] * 512 * 1000  # bytes
        return nand_writes, host_writes
    return None, None

# Main function to run the commands and log to CSV
def log_nvme_data(interval, csv_file):
    # Open the CSV file to write, flush=True ensures the data is written immediately
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["Timestamp", "NAND Writes (Bytes)", "Host Writes (Bytes)"])
        file.flush()

        while True:
            # Run both commands
            smart_log_command = "sudo nvme smart-log /dev/nvme0 -o=json"
            ocp_log_command = "sudo nvme ocp smart-add-log /dev/nvme0 -o=json"

            # Fetch logs
            nvme_smart_log = run_nvme_command(smart_log_command)
            nvme_ocp_log = run_nvme_command(ocp_log_command)

            # Calculate NAND writes and host writes
            nand_writes, host_writes = calculate_writes(nvme_smart_log, nvme_ocp_log)

            if nand_writes is not None and host_writes is not None:
                # Get the current timestamp
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

                # Write the data to CSV
                writer.writerow([timestamp, nand_writes, host_writes])
                print(f"{timestamp} - NAND Writes: {nand_writes}, Host Writes: {host_writes}")

                # Ensure the data is immediately written to the file
                file.flush()

            # Wait for the specified interval
            time.sleep(interval)

# Set the interval (in seconds) and CSV file path
interval = 10  # Example: log every 60 seconds
csv_file = "nvme_log.csv"

# Start logging
log_nvme_data(interval, csv_file)
