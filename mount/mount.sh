#!/bin/bash

boot_drive_raw=$(df -h / | tail -1 | awk '{gsub("/dev/", "", $1); print $1}' | sed 's/[0-9]//g')

# List all unmounted drives excluding the boot drive and its partitions
drives=$(lsblk -rno name,mountpoint | awk -v boot_drive_raw="$boot_drive_raw" '$1 ~ "^sd" && $1 != boot_drive_raw && $1 !~ boot_drive_raw"[0-9]+$" && $1 !~ "^nvme" && $2==""{print $1}')


# Prompt user for confirmation
echo "The following drives will have fstab and mountpoints created for:"
echo "$drives"
read -p "Do you want to proceed (y/n)? " confirm

if [ "$confirm" == "n" ]; then
  echo "Exiting script."
  exit 1
fi

# Find the number of existing /farm/hdd mountpoints
existing_hdds=$(ls -d /farm/hdd* 2>/dev/null | wc -l)
count=$((existing_hdds+1))

# Loop through drives and generate fstab entries and mount point directories
for drive in $drives
do
  # Get UUID of drive
  uuid=$(lsblk -o name,uuid,size | awk -v drive="$drive" '$1 == drive {print $2}')

  # Create mount point directory and set permissions
  mount_point="/farm/hdd$count"
  mkdir -p $mount_point

  # Generate fstab entry
  entry="/dev/disk/by-uuid/$uuid $mount_point ext4 nofail,rw,noatime 0 0"

  # Append entry to fstab
  echo $entry >> /etc/fstab

  mount $mount_point
  chown -R jm:jm $mount_point

  # Increment counter for next mount point directory
  count=$((count+1))
done

echo "Script complete."