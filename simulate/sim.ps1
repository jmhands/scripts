$dir_path = 'D:\plots'
$csv_output_path = 'D:\plots\output.csv'

# Remove the following line from the script
# Add-Content -Path $csv_output_path -Value 'File,Average plot lookup time,Worst plot lookup lookup time,Average full proof lookup time'

# Get all .plot files in the directory
$files = Get-ChildItem -Path $dir_path -Filter '*.plot'

# Add the header to the CSV file only once
Add-Content -Path $csv_output_path -Value 'File,Average plot lookup time,Worst plot lookup lookup time,Average full proof lookup time'

foreach ($file in $files) {
    $output = & '.\bladebit_cuda.exe' 'simulate' '-n' '1000' $file.FullName
    $avg_plot_lookup_time = ($output | Select-String -Pattern 'Average plot lookup time\s+:\s+(\d+\.\d+)').Matches.Groups[1].Value
    $worst_plot_lookup_time = ($output | Select-String -Pattern 'Worst plot lookup lookup time\s+:\s+(\d+\.\d+)').Matches.Groups[1].Value
    $avg_full_proof_lookup_time = ($output | Select-String -Pattern 'Average full proof lookup time:\s+(\d+\.\d+)').Matches.Groups[1].Value

    # Write data to the CSV file
    Add-Content -Path $csv_output_path -Value "$($file.Name),$avg_plot_lookup_time,$worst_plot_lookup_time,$avg_full_proof_lookup_time"
}
