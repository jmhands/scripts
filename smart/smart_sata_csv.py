import subprocess
import json
import csv
import os

def get_smart_data(device):
    result = subprocess.run(['smartctl', '-a', device, '-j'], stdout=subprocess.PIPE)
    return json.loads(result.stdout)

def parse_json(data):
    if 'model_name' not in data or 'serial_number' not in data or 'firmware_version' not in data or 'ata_smart_attributes' not in data:
        return []

    model_name = data['model_name']
    serial_number = data['serial_number']
    firmware_version = data['firmware_version']
    smart_attributes = data['ata_smart_attributes']['table']

    rows = []
    for attr in smart_attributes:
        rows.append([
            model_name,
            serial_number,
            firmware_version,
            attr['id'],
            attr['name'],
            attr['value'],
            attr['worst'],
            attr['thresh'],
            attr.get('when_failed', ''),
            attr['raw']['value']
        ])
    return rows

def write_csv(data, file):
    with open(file, 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(data)

# Get a list of all SCSI devices (which includes SATA devices)
devices = [device for device in os.listdir('/dev') if device.startswith('sd') and not device[2:].isdigit()]

# Initialize CSV file with headers
with open('smart_attributes.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Model Name', 'Serial Number', 'Firmware Version', 'ID', 'Name', 'Value', 'Worst', 'Thresh', 'When Failed', 'Raw Value'])

# Iterate over devices and write SMART data to CSV
for device in devices:
    data = get_smart_data(f'/dev/{device}')
    parsed_data = parse_json(data)
    if parsed_data:  # Only write data if there's something to write
        write_csv(parsed_data, 'smart_attributes.csv')