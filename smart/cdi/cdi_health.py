import streamlit as st
import json
import gzip
import io
import tarfile
from datetime import datetime
import pandas as pd
import altair as alt

def extract_json_from_gzip(uploaded_file):
    """Extract and parse multiple JSON files from a gzipped tar archive."""
    drives_data = []

    # Create a BytesIO object from the uploaded file
    bytes_io = io.BytesIO(uploaded_file.read())

    # Open as tar archive
    try:
        with tarfile.open(fileobj=bytes_io, mode='r:gz') as tar:
            # Iterate through all files in the archive
            for member in tar.getmembers():
                if member.name.endswith('.json'):
                    # Extract the JSON file
                    f = tar.extractfile(member)
                    if f is not None:
                        try:
                            # Parse JSON content
                            content = json.loads(f.read().decode('utf-8'))
                            drives_data.append(content)
                        except Exception as e:
                            st.warning(f"Failed to parse {member.name}: {str(e)}")
    except Exception as e:
        st.error(f"Error processing archive: {str(e)}")

    return drives_data

def calculate_tbw(data):
    """Calculate Terabytes Written from SMART data."""
    try:
        if 'ata_smart_attributes' in data:
            for attr in data['ata_smart_attributes']['table']:
                if attr['id'] == 241:  # Total_LBAs_Written
                    return (attr['raw']['value'] * 512) / (1024**4)  # Convert to TBW
    except Exception as e:
        st.warning(f"Error calculating TBW: {str(e)}")
    return 0

def analyze_drive_health(data):
    """Analyze drive health based on specified criteria."""
    issues = []
    is_failed = False

    try:
        # Basic SMART status check
        if not data.get('smart_status', {}).get('passed', True):
            issues.append("Failed SMART status")
            is_failed = True

        # Temperature checks
        temp_data = data.get('temperature', {})
        current_temp = temp_data.get('current')
        max_temp = temp_data.get('lifetime_max')

        if current_temp and max_temp:
            if max_temp > 70:  # General threshold for most drives
                issues.append(f"Maximum temperature exceeded: {max_temp}°C")
                is_failed = True

        # Check SMART attributes
        if 'ata_smart_attributes' in data:
            for attr in data['ata_smart_attributes']['table']:
                # Reallocated Sectors check
                if attr['id'] == 5 and attr['raw']['value'] > 10:
                    issues.append(f"Reallocated sectors: {attr['raw']['value']}")
                    is_failed = True

                # Pending Sectors check
                elif attr['id'] == 197 and attr['raw']['value'] > 10:
                    issues.append(f"Pending sectors: {attr['raw']['value']}")
                    is_failed = True

                # Uncorrectable Errors
                elif attr['id'] == 187 and attr['raw']['value'] > 0:
                    issues.append(f"Uncorrectable errors: {attr['raw']['value']}")
                    is_failed = True

        # Calculate workload
        tbw = calculate_tbw(data)
        poh = data.get('power_on_time', {}).get('hours', 0)

        if poh > 0:
            tb_per_year = (tbw * 8760) / poh  # Convert to TB/year
            if tb_per_year > 550:
                issues.append(f"Heavy workload: {tb_per_year:.1f} TB/year")

        return is_failed, issues, tbw

    except Exception as e:
        st.warning(f"Error analyzing drive health: {str(e)}")
        return True, ["Error analyzing drive health"], 0

def main():
    st.title("Drive Health Analysis Dashboard")

    uploaded_files = st.file_uploader("Upload SMART log files (TAR.GZ)",
                                    type=['gz'],
                                    accept_multiple_files=True)

    if uploaded_files:
        drives_data = []

        # Process each uploaded file
        with st.spinner('Processing files...'):
            for uploaded_file in uploaded_files:
                data = extract_json_from_gzip(uploaded_file)
                if data:
                    drives_data.extend(data)
                    st.success(f"Successfully processed: {uploaded_file.name}")
                else:
                    st.error(f"Failed to process: {uploaded_file.name}")

        if not drives_data:
            st.error("No valid SMART data found in uploaded files")
            return

        # Summary statistics
        st.header("Fleet Summary")
        total_drives = len(drives_data)
        failed_drives = 0
        total_tbw = 0
        drive_summaries = []

        for data in drives_data:
            try:
                model = data.get('model_name', 'Unknown')
                serial = data.get('serial_number', 'Unknown')
                firmware = data.get('firmware_version', 'Unknown')
                is_failed, issues, tbw = analyze_drive_health(data)

                if is_failed:
                    failed_drives += 1

                total_tbw += tbw

                drive_summaries.append({
                    'Model': model,
                    'Serial': serial,
                    'Firmware': firmware,
                    'Status': 'Failed' if is_failed else 'Healthy',
                    'POH': data.get('power_on_time', {}).get('hours', 0),
                    'TBW': round(tbw, 2),
                    'Temperature': data.get('temperature', {}).get('current', 'N/A'),
                    'Issues': ', '.join(issues) if issues else 'None'
                })
            except Exception as e:
                st.warning(f"Error processing drive {serial}: {str(e)}")

        # Calculate MTBF and AFR
        total_poh = sum(data.get('power_on_time', {}).get('hours', 0) for data in drives_data)
        mtbf_hours = total_poh / (failed_drives if failed_drives > 0 else 1)
        afr = (failed_drives / total_drives) * (8760 / (total_poh / total_drives)) * 100 if total_drives > 0 and total_poh > 0 else 0

        # Display summary metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Total Drives", total_drives)
        with col2:
            st.metric("Failed Drives", failed_drives)
        with col3:
            st.metric("Total TB Written", f"{total_tbw:.2f}")
        with col4:
            health_ratio = ((total_drives - failed_drives) / total_drives * 100) if total_drives > 0 else 0
            st.metric("Fleet Health", f"{health_ratio:.1f}%")
        with col5:
            st.metric("MTBF (hours)", f"{mtbf_hours:,.0f}")
        with col6:
            st.metric("AFR", f"{afr:.2f}%")

        # Convert to DataFrame for better display
        df_summary = pd.DataFrame(drive_summaries)

        # Show failed drives first
        st.header("Failed Drives")
        failed_df = df_summary[df_summary['Status'] == 'Failed']
        if not failed_df.empty:
            st.dataframe(failed_df)
        else:
            st.success("No failed drives detected")

        # Show all drives
        st.header("All Drives")
        st.dataframe(df_summary)

        # Drive Health Distribution
        st.header("Health Distribution")
        health_chart = alt.Chart(df_summary).mark_bar().encode(
            x='Status',
            y='count()',
            color=alt.Color('Status', scale=alt.Scale(
                domain=['Healthy', 'Failed'],
                range=['#2ecc71', '#e74c3c']
            ))
        ).properties(height=300)
        st.altair_chart(health_chart, use_container_width=True)

        # TBW Distribution
        st.header("TBW Distribution")
        tbw_chart = alt.Chart(df_summary).mark_boxplot().encode(
            y='TBW'
        ).properties(height=300)
        st.altair_chart(tbw_chart, use_container_width=True)

if __name__ == "__main__":
    main()