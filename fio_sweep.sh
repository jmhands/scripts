#!/bin/bash

DEVICE="/dev/nvme1n1"
BLOCK_SIZES=("4k" "16k" "128k")
RW_PATTERNS=("write" "read" "readwrite" "randread" "randwrite")
IO_DEPTHS=("1" "4" "16" "64" "128" "256")

# Create directories for logs and output
mkdir -p fio_logs

# Create and initialize the CSV summary file
CSV_FILE="fio_summary.csv"
echo "Block Size,Workload,I/O Depth,IOPS,Bandwidth (MB/s),Latency (us)" > "${CSV_FILE}"

# Colors for summary
LIGHT_MAGENTA="\033[95m"
LIGHT_BLUE="\033[94m"
LIGHT_YELLOW="\033[93m"
RESET="\033[0m"

for bs in "${BLOCK_SIZES[@]}"; do
  for rw in "${RW_PATTERNS[@]}"; do
    for io_depth in "${IO_DEPTHS[@]}"; do
      TEST_NAME="${rw}_${bs}_iodepth${io_depth}"
      echo "Running test: ${TEST_NAME}"

      # Run the fio test and capture its output
      FIO_JSON_OUTPUT=$(sudo fio --filename="${DEVICE}" \
                            --rw="${rw}" \
                            --direct=1 \
                            --bs="${bs}" \
                            --ioengine=io_uring \
                            --runtime=60 \
                            --numjobs=1 \
                            --time_based \
                            --group_reporting \
                            --name="${TEST_NAME}" \
                            --iodepth="${io_depth}" \
                            # uncomment these to write the bandwidth log
                            #--log_avg_msec=1000 \
                            #--write_bw_log="fio_logs/${TEST_NAME}_bw.log" \
                            --output-format=json 2>&1)

      echo "Completed test: ${TEST_NAME}"
      echo "--------------------------------------"

      # Extract metrics from fio's JSON output
      IOPS=$(echo "$FIO_JSON_OUTPUT" | jq '.jobs[0].read.iops + .jobs[0].write.iops')
      BANDWIDTH_MB=$(echo "$FIO_JSON_OUTPUT" | jq '(.jobs[0].read.bw + .jobs[0].write.bw) * 1024 / 1000 / 1000')
      if [ "$rw" == "read" ] || [ "$rw" == "randread" ] || [ "$rw" == "readwrite" ]; then
        LATENCY_US=$(echo "$FIO_JSON_OUTPUT" | jq '.jobs[0].read.lat_ns.mean / 1000')
      else
        LATENCY_US=$(echo "$FIO_JSON_OUTPUT" | jq '.jobs[0].write.lat_ns.mean / 1000')
      fi

      # Append the results to the CSV summary file
      echo "${bs%k},${rw},${io_depth},${IOPS},${BANDWIDTH_MB},${LATENCY_US}" >> "${CSV_FILE}"

      # Format output with 2 decimal places
      IOPS=$(printf "%.2f" "${IOPS}")
      BANDWIDTH_MB=$(printf "%.2f" "${BANDWIDTH_MB}")
      LATENCY_US=$(printf "%.2f" "${LATENCY_US}")

      # Print summary with colors
      if [ "$rw" == "randwrite" ]; then
        COLOR="${LIGHT_MAGENTA}"
      elif [ "$rw" == "write" ]; then
        COLOR="${LIGHT_MAGENTA}"
      elif [ "$rw" == "randread" ]; then
        COLOR="${LIGHT_BLUE}"
      elif [ "$rw" == "read" ]; then
        COLOR="${LIGHT_BLUE}"
      elif [ "$rw" == "readwrite" ]; then
        COLOR="${LIGHT_YELLOW}"
      fi

      SUMMARY_LINE="${COLOR}BS: ${bs}, ${rw}, I/O Depth: ${io_depth}, IOPS: ${IOPS}, BW (MB/s): ${BANDWIDTH_MB}, Latency (us): ${LATENCY_US}${RESET}"
      echo -e "${SUMMARY_LINE}"

    done
  done
done

# Print the final summary table
echo -e "\nFinal Summary:"
echo -e "${SUMMARY_TABLE}"

# Function to find the longest string in an array
function max_length() {
  local max_len=0
  for str in "${@}"; do
    if [ ${#str} -gt ${max_len} ]; then
      max_len=${#str}
    fi
  done
  echo ${max_len}
}

# Generate the aligned Markdown table with colors from the summary CSV
IFS=',' read -r bs rw io_depth iops bandwidth latency < "${CSV_FILE}"
bs_len=$(max_length "${BLOCK_SIZES[@]}" "Block Size")
rw_len=$(max_length "${RW_PATTERNS[@]}" "Workload")
io_len=$(max_length "${IO_DEPTHS[@]}" "I/O Depth")

MD_TABLE="| $(printf "%-${bs_len}s" "${bs}") | $(printf "%-${rw_len}s" "${rw}") | $(printf "%-${io_len}s" "${io_depth}") | ${iops} | ${bandwidth} | ${latency} |\n"
MD_TABLE+="|$(printf '%0.s-' {1..$((bs_len+2))})|$(printf '%0.s-' {1..$((rw_len+2))})|$(printf '%0.s-' {1..$((io_len+2))})|--------:|-----------:|-----------:|\n"

while IFS=',' read -r bs rw io_depth iops bandwidth latency; do
  if [ "$bs" != "Block Size" ]; then
    if [ "$rw" == "randwrite" ]; then
      COLOR="${LIGHT_MAGENTA}"
    elif [ "$rw" == "write" ]; then
      COLOR="${LIGHT_MAGENTA}"
    elif [ "$rw" == "randread" ]; then
      COLOR="${LIGHT_BLUE}"
    elif [ "$rw" == "read" ]; then
      COLOR="${LIGHT_BLUE}"
    elif [ "$rw" == "readwrite" ]; then
      COLOR="${LIGHT_YELLOW}"
    fi
    MD_TABLE+="| ${COLOR}$(printf "%-${bs_len}s" "${bs}")${RESET} | ${COLOR}$(printf "%-${rw_len}s" "${rw}")${RESET} | ${COLOR}$(printf "%-${io_len}s" "${io_depth}")${RESET} | ${COLOR}${iops}${RESET} | ${COLOR}${bandwidth}${RESET} | ${COLOR}${latency}${RESET} |\n"
  fi
done < "${CSV_FILE}"

# Print the final Markdown table with colors and alignment
echo -e "\nFinal Summary in Markdown with Alignment and Colors:"
echo -e "${MD_TABLE}"