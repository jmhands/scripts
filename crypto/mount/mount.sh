#!/bin/bash

# Prompt user for their username
read -p "Enter your username: " username

# Prompt user for their boot drive
read -p "Enter your boot drive (e.g. /dev/sda): " boot_drive

# Extract just the name of the boot drive without '/dev/'
boot_drive_name=$(echo "$boot_drive" | sed 's/\/dev\///')

# List all unmounted drives with no partitions and exclude the boot drive and its partitions
drives=$(lsblk -nlo NAME,MOUNTPOINT | awk '! /\// {print $1}' | grep -Ev "^$boot_drive_name$|^$boot_drive_name[0-9]+$" | grep -E '^sd[a-z]$|^sd[a-z][a-z]$|^sd[a-z][a-z][0-9]$|^sda[a-z]$|^sda[a-z][0-9]$')

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

  # Get drive serial number
  serial_number=$(sudo smartctl -a "/dev/$drive" | grep "Serial Number" | awk '{print $3}')

  # Create mount point directory and set permissions
  mount_point="/farm/hdd$count-$serial_number"
  mkdir -p "$mount_point"

  # Generate fstab entry
  entry="/dev/disk/by-uuid/$uuid $mount_point ext4 nofail,rw,noatime 0 0"

  # Append entry to fstab
  echo "$entry" >> /etc/fstab

  mount "$mount_point"
  chown -R "$username":"$username" "$mount_point"

  # Increment counter for next mount point directory
  count=$((count+1))
done

echo "Script complete."
