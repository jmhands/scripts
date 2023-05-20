# scripts
This is JM's collection of random scripts

## monitoring

docker compose file for running Prometheus, Node-Exporter, NVIDIA GPU exporter, and Chia Exporter
Just install docker from https://docs.docker.com/engine/install/ubuntu/ and run `docker compose up -d`

## smart

Collection of scripts to collect SMART data off all the drives in a system. Outputs to csv

## mount

Use `format.sh` to format all HDDs in a system to ext4 for use in Chia farming, and `mount.sh` to automatically create fstab entires and mount all the drives in your system

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

## random one liners

NFS settings for /etc/fstab

`nfs rw,hard,intr,rsize=32768,wsize=32768,nfsvers=4,async,noatime,actimeo=0,timeo=600,retry=-1`

Creating a RAID array with lvm

```
sudo pvcreate /dev/nvme0n1 /dev/nvme1n1 /dev/nvme2n1 /dev/nvme3n1
sudo vgcreate test1 /dev/nvme0n1 /dev/nvme1n1 /dev/nvme2n1 /dev/nvme3n1
sudo lvcreate --type striped -i 4 -I 512k -l 100%FREE -n test1 test1
```

Format drive with xfs

`mkfs.xfs -f -s size=4k -m crc=0 /dev/nvme1n1`

List all the /mnt for python

`python3 -c "import glob; print(glob.glob('/mnt/*'))"`

Change everything in fstab to read only

`sed -i 's/rw,/ro,/g' /etc/fstab`

Find all files below a certain size and delete them

`sudo find /mnt/hdd* -type f -size -100G -delete`

Print total amount of terabytes in /mnt

`df | grep mnt | awk 'BEGIN{sum=0} {sum+=$3*1024/(1000^5)} END{print sum}'`

Update firmware on SATA drive with hdparm

`sudo hdparm --yes-i-know-what-i-am-doing --please-destroy-my-drive --fwdownload fw.bin /dev/sda`

For loop for all drives in the system

`for i in $(ls /dev/sd*); do echo $i; done`

Format all drives (very dangerous) for use in Chia farming

`for i in $(ls /dev/sd*); do mkfs.ext4 -F -m 0 -T largefile4 $i; done`