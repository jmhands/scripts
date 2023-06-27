#!/bin/bash

# Find all drives that are not mounted
drives=$(lsblk -nlo NAME,MOUNTPOINT | awk '! /\// {print $1}' | grep -E '^sd[b-z]$|^sd[b-z][a-z]$|^sd[b-z][a-z][0-9]$')

# Prompt user for confirmation
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
