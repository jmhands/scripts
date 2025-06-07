# NVMe SMART Dashboard

A comprehensive Streamlit dashboard for analyzing NVMe SMART logs collected from multiple hosts using Ansible.

## Features

### 🔍 **Main Dashboard**
- **Critical Warnings**: Instantly identify drives with health issues
- **Power On Hours**: Track drive usage in hours, days, or years
- **Percent Used**: Monitor wear levels across all drives
- **Total Bytes Written (TBW)**: See write endurance consumption
- **Temperature Monitoring**: Current temps with warning thresholds
- **Drive Summary Table**: Comprehensive overview of all drives

### 🔧 **Advanced Mode**
- **Detailed Drive Analysis**: Per-drive deep dive
- **Complete SMART Data**: View all raw SMART attributes
- **Read/Write Statistics**: Detailed I/O metrics
- **Error Tracking**: Media errors, unsafe shutdowns, etc.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Collect NVMe SMART Data
First, run the Ansible playbook to collect SMART logs:
```bash
ansible-playbook nvme_smart_logs.yml -i inventory.ini
```

This will create JSON files in `/opt/nvme_smart_logs/` on your collection host.

### 3. Run the Dashboard
```bash
streamlit run nvme_dashboard.py
```

The dashboard will be available at `http://localhost:8501`

## Usage

### Basic Mode
- View overall fleet health at a glance
- Identify drives with critical warnings
- Monitor key metrics: power hours, wear level, TBW, temperature
- Filter and sort drive data

### Advanced Mode
- Enable "Advanced Mode" in the sidebar
- Select individual drives for detailed analysis
- View complete SMART attribute data
- Analyze read/write patterns and error history

### Configuration
- **Log Directory**: Change the path to your SMART logs (default: `/opt/nvme_smart_logs/`)
- **Refresh Data**: Click refresh to reload the latest data
- **Filters**: Use sidebar options to customize the view

## Dashboard Sections

### 📊 Summary Metrics
- Total drive count
- Drives with critical warnings
- Average percent used across fleet
- Total terabytes written (TBW)

### 🚨 Critical Warnings
Automatically flags drives with:
- Available spare below threshold
- Temperature issues
- NVM subsystem reliability degraded
- Media in read-only mode
- Volatile memory backup failures

### 📈 Visualizations
- **Power On Hours**: Bar chart showing drive age/usage
- **Percent Used**: Color-coded wear level visualization
- **Total Bytes Written**: Write endurance tracking
- **Temperature**: Current temps with warning/critical thresholds

### 📋 Data Table
Sortable table with key metrics for all drives:
- Hostname and device path
- Serial number for unique identification
- Critical warning status
- Wear level (% used)
- Power on time in human-readable format
- Total data written
- Current temperature
- Available spare capacity

## Data Sources

The dashboard reads JSON files created by the `nvme_smart_logs.yml` Ansible playbook. Each file contains:
- Host information (hostname, device path)
- Drive identification (serial number)
- Timestamp of collection
- Complete SMART log data in JSON format

## Interpretation

### Critical Warning Bits
- **Bit 0**: Available spare below threshold
- **Bit 1**: Temperature above/below threshold
- **Bit 2**: NVM subsystem reliability degraded
- **Bit 3**: Media in read-only mode
- **Bit 4**: Volatile memory backup device failed

### Key Metrics
- **Power On Hours**: Total time drive has been powered on
- **Percent Used**: Vendor estimate of drive life consumed (0-100%)
- **Data Units Written**: Total data written to drive (converted to TB)
- **Temperature**: Current drive temperature in Celsius
- **Available Spare**: Remaining spare capacity percentage

## Troubleshooting

### No Data Available
- Verify the log directory path is correct
- Ensure JSON files exist in the specified directory
- Check that the Ansible playbook ran successfully
- Verify file permissions allow reading the log files

### Missing Metrics
- Some drives may not report all SMART attributes
- Missing values are handled gracefully with defaults
- Check the raw SMART data in Advanced Mode for available fields

### Performance
- Large numbers of drives may slow initial load
- Use the refresh button to reload data
- Consider filtering or archiving old log files

## Files

- `nvme_dashboard.py`: Main Streamlit dashboard application
- `nvme_smart_logs.yml`: Ansible playbook for data collection
- `requirements.txt`: Python dependencies
- `README.md`: This documentation
- `nvme_smart.md`: NVMe SMART specification reference