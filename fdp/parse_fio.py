import os
import csv

def calculate_averages(log_dir):
    results = {}
    for filename in os.listdir(log_dir):
        if filename.endswith("_bw_log.log") or filename.endswith("_iops_log.log"):
            filepath = os.path.join(log_dir, filename)
            is_bw = "_bw_" in filename
            key = filename.split('_')[0]
            if key not in results:
                results[key] = {"read_bw": 0, "write_bw": 0, "read_iops": 0, "write_iops": 0}

            read_total, write_total, read_count, write_count = 0, 0, 0, 0
            with open(filepath, 'r') as file:
                for line in file:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        value = float(parts[1].strip())
                        rw_type = int(parts[2].strip())  # 0 for read, 1 for write
                        if rw_type == 0:  # Read
                            read_total += value
                            read_count += 1
                        elif rw_type == 1:  # Write
                            write_total += value
                            write_count += 1

            if is_bw:
                if read_count > 0:
                    results[key]["read_bw"] = read_total / read_count
                if write_count > 0:
                    results[key]["write_bw"] = write_total / write_count
            else:  # iops log
                if read_count > 0:
                    results[key]["read_iops"] = read_total / read_count
                if write_count > 0:
                    results[key]["write_iops"] = write_total / write_count

    return results

def write_to_csv(results, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Host', 'Avg Read Bandwidth', 'Avg Write Bandwidth', 'Avg Read IOPS', 'Avg Write IOPS']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for host, data in results.items():
            writer.writerow({'Host': host, 'Avg Read Bandwidth': data["read_bw"],
                             'Avg Write Bandwidth': data["write_bw"], 'Avg Read IOPS': data["read_iops"],
                             'Avg Write IOPS': data["write_iops"]})

if __name__ == "__main__":
    log_directory = "/root/logs"  # Change this to your logs directory
    output_csv_path = "/root/output.csv"  # Change this to your desired output CSV file path
    results = calculate_averages(log_directory)
    write_to_csv(results, output_csv_path)
    print("Processing complete. Results saved to", output_csv_path)