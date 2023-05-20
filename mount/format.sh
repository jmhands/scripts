#!/bin/bash

boot_drive_raw=$(df -h / | tail -1 | awk '{gsub("/dev/", "", $1); print $1}' | sed 's/[0-9]//g')

# List all unmounted drives excluding the boot drive and its partitions and nvme
drives=$(lsblk -rno name,mountpoint | awk -v boot_drive_raw="$boot_drive_raw" '$1 ~ "^sd" && $1 != boot_drive_raw && $1 !~ boot_drive_raw"[0-9]+$" && $2==""{print $1}')

# Prompt user for confirmation
echo "The following drives will be formatted:"
echo "$drives"
read -p "Do you want to proceed with formatting (y/n)? " confirm

if [[ $confirm =~ ^[Yy]$ ]]
then
  # Format drives asynchronously
  for drive in $drives
  do
    echo "Formatting drive $drive"
    sudo mkfs.ext4 -m 0 -T largefile4 -F /dev/$drive &
  done
else
  echo "Skipping drive formatting"
fi