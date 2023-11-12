import os
import re
import time
import random

# Threshold settings
THRESHOLD_DATE = "2023-06-01"
MAX_COMPRESSION_SIZE = 8
PLOTS_PER_DAY = 1000
PLOTS_PER_HOUR = PLOTS_PER_DAY // 24

# Directory to monitor
FARM_DIR = "/farm"

# Regular expressions
PATTERN_WITH_C = r"plot-k32-c(\d{1,2})-(\d{4}-\d{2}-\d{2})-\d{2}-\d{2}-[a-f0-9]+.plot"
PATTERN_WITHOUT_C = r"plot-k32-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-[a-f0-9]+.plot"

def delete_old_plots():
    while True:
        # List all files under FARM_DIR
        all_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(FARM_DIR) for f in filenames]

        # Filter out files that match the criteria
        candidates_with_c = []
        candidates_without_c = []
        for filepath in all_files:
            filename = os.path.basename(filepath)
            match_with_c = re.match(PATTERN_WITH_C, filename)
            match_without_c = re.match(PATTERN_WITHOUT_C, filename)
            if match_with_c:
                compression_size, date = int(match_with_c.group(1)), match_with_c.group(2)
                if date < THRESHOLD_DATE and compression_size <= MAX_COMPRESSION_SIZE:
                    candidates_with_c.append(filepath)
            elif match_without_c:
                candidates_without_c.append(filepath)

        # Shuffle the lists of candidates to ensure random deletion
        random.shuffle(candidates_with_c)
        random.shuffle(candidates_without_c)

        # Delete files without 'C' value first
        for filepath in candidates_without_c[:PLOTS_PER_HOUR]:
            os.remove(filepath)
            print(f"Deleted: {filepath}")  # For logging purposes

        # If there's still capacity, delete files with 'C' value
        remaining_capacity = PLOTS_PER_HOUR - len(candidates_without_c)
        for filepath in candidates_with_c[:remaining_capacity]:
            os.remove(filepath)
            print(f"Deleted: {filepath}")  # For logging purposes

        # Sleep for 1 hour before checking again
        time.sleep(3600)

if __name__ == "__main__":
    delete_old_plots()
