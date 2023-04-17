# scripts
This is JM's collection of random scripts

## fio_sweep.sh

currently setup for raw device testing for a full sweep of queue depths, workloads, and blocksizes

### Config

edit the device configuration, block sizes, workloads (RW_PATTERNS), and queue depth (IO_DEPTHS)
```
DEVICE="/dev/nvme1n1"
BLOCK_SIZES=("4k" "16k" "128k")
RW_PATTERNS=("write" "read" "readwrite" "randread" "randwrite")
IO_DEPTHS=("1" "4" "16" "64" "128" "256")
```