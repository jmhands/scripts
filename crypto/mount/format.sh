#!/bin/bash

# Find all drives that are not mounted
drives=$(lsblk -nlo NAME,MOUNTPOINT | awk '! /\// {print $1}' | grep -E '^sd[a-z]$|^sd[a-z][a-z]$|^sd[a-z][a-z][0-9]$')

# Prompt user for drives to skip
read -p "Enter drives you want to skip (comma separated e.g. sda,sdb): " skip_drives
IFS=',' read -ra ADDR <<< "$skip_drives"

# Remove the drives to skip from the list
for i in "${ADDR[@]}"; do
   drives=$(echo "$drives" | sed "/^$i$/d")
done

# Show the list of drives to be formatted
echo "The following drives will be formatted:"
for drive in $drives; do
  echo "/dev/$drive"
done

read -p "Do you want to proceed with formatting (y/n)? " confirm

if [[ $confirm =~ ^[Yy]$ ]]
then
  # Format drives asynchronously
  for drive in $drives
  do
    echo "Formatting drive /dev/$drive"
    sudo mkfs.ext4 -m 0 -T largefile4 -F /dev/$drive &
  done
else
  echo "Skipping drive formatting"
fi
