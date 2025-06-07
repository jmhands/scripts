#!/usr/bin/env python3
"""
NVMe SMART Dashboard
Analyzes NVMe SMART logs collected from multiple hosts
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import glob
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="NVMe SMART Dashboard",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_smart_data(log_dir="/opt/nvme_smart_logs"):
    """Load all SMART log JSON files"""
    json_files = glob.glob(os.path.join(log_dir, "*.json"))

    if not json_files:
        st.error(f"No JSON files found in {log_dir}")
        return pd.DataFrame()

    data = []
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                log_data = json.load(f)
                if 'smart_log' in log_data and log_data['smart_log']:
                    smart_data = log_data['smart_log']
                    id_ctrl_data = log_data.get('id_ctrl', {})
                    id_ns_data = log_data.get('id_ns', {})

                    # Extract model and capacity info
                    model_number = id_ctrl_data.get('mn', 'Unknown').strip() if id_ctrl_data else 'Unknown'
                    # Use TNVMCAP (Total NVM Capacity) field from id_ctrl which gives capacity directly in bytes
                    capacity_bytes = id_ctrl_data.get('tnvmcap', 0) if id_ctrl_data else 0
                    capacity_tb = capacity_bytes / (1000**4) if capacity_bytes > 0 else 0  # Convert to decimal TB

                    # Extract key metrics from SMART log
                    record = {
                        'hostname': log_data.get('hostname', 'Unknown'),
                        'device': log_data.get('device', 'Unknown'),
                        'serial_number': log_data.get('serial_number', 'Unknown'),
                        'timestamp': log_data.get('timestamp', ''),
                        'file_path': file_path,

                        # Drive identification
                        'model_number': model_number,
                        'capacity_tb': capacity_tb,
                        'firmware_rev': id_ctrl_data.get('fr', 'Unknown').strip() if id_ctrl_data else 'Unknown',

                        # Critical metrics
                        'critical_warning': smart_data.get('critical_warning', 0),
                        'avail_spare': smart_data.get('avail_spare', 0),
                        'spare_thresh': smart_data.get('spare_thresh', 0),
                        'percent_used': smart_data.get('percent_used', 0),
                        'power_on_hours': smart_data.get('power_on_hours', 0),
                        'unsafe_shutdowns': smart_data.get('unsafe_shutdowns', 0),
                        'media_errors': smart_data.get('media_errors', 0),
                        'num_err_log_entries': smart_data.get('num_err_log_entries', 0),

                        # Temperature (convert from Kelvin to Celsius if needed)
                        'temperature': smart_data.get('temperature', 0) - 273.15 if smart_data.get('temperature', 0) > 200 else smart_data.get('temperature', 0),
                        'temp_sensor_1': smart_data.get('temp_sensor_1', 0) - 273.15 if smart_data.get('temp_sensor_1', 0) > 200 else smart_data.get('temp_sensor_1', 0),
                        'temp_sensor_2': smart_data.get('temp_sensor_2', 0) - 273.15 if smart_data.get('temp_sensor_2', 0) > 200 else smart_data.get('temp_sensor_2', 0),

                        # Data written/read (convert to TB)
                        # NVMe spec: data_units_written is in thousands, so multiply by 1000, then * 512 bytes, then convert to decimal TB
                        'data_units_written': (smart_data.get('data_units_written', 0) * 1000 * 512) / (1000**4),  # Convert to decimal TB
                        'data_units_read': (smart_data.get('data_units_read', 0) * 1000 * 512) / (1000**4),      # Convert to decimal TB
                        'host_writes': (smart_data.get('host_writes', 0) * 1000 * 512) / (1000**4),             # Convert to decimal TB
                        'host_reads': (smart_data.get('host_reads', 0) * 1000 * 512) / (1000**4),               # Convert to decimal TB

                        # Full SMART data for advanced mode
                        'full_smart_data': smart_data
                    }
                    data.append(record)
        except Exception as e:
            st.warning(f"Error reading {file_path}: {e}")

    return pd.DataFrame(data)

def interpret_critical_warning(warning_value):
    """Interpret critical warning bits"""
    warnings = []
    if warning_value & 0x01:
        warnings.append("Available Spare Below Threshold")
    if warning_value & 0x02:
        warnings.append("Temperature Above/Below Threshold")
    if warning_value & 0x04:
        warnings.append("NVM Subsystem Reliability Degraded")
    if warning_value & 0x08:
        warnings.append("Media in Read-Only Mode")
    if warning_value & 0x10:
        warnings.append("Volatile Memory Backup Device Failed")

    return warnings if warnings else ["OK"]

def format_time_duration(hours):
    """Format hours into human readable duration"""
    if hours < 24:
        return f"{hours:.1f} hours"
    elif hours < 24 * 365:
        days = hours / 24
        return f"{days:.1f} days ({hours:,.0f} hours)"
    else:
        years = hours / (24 * 365)
        return f"{years:.2f} years ({hours:,.0f} hours)"

def main():
    st.title("💾 NVMe SMART Dashboard")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        log_dir = st.text_input("Log Directory", value="/opt/nvme_smart_logs")
        refresh = st.button("🔄 Refresh Data")

        st.markdown("---")
        st.header("Filters")
        show_advanced = st.checkbox("Advanced Mode", help="Show detailed SMART statistics")

        # Add filters (only show if data is loaded)
        if 'df' in st.session_state and not st.session_state.df.empty:
            df_for_filters = st.session_state.df

            # Model filter
            models = ['All'] + sorted(df_for_filters['model_number'].unique().tolist())
            selected_model = st.selectbox("Filter by Model", models)

            # Capacity filter
            capacities = ['All'] + sorted([f"{cap:.1f} TB" for cap in df_for_filters['capacity_tb'].unique() if cap > 0])
            selected_capacity = st.selectbox("Filter by Capacity", capacities)

            # Host filter
            hosts = ['All'] + sorted(df_for_filters['hostname'].unique().tolist())
            selected_host = st.selectbox("Filter by Host", hosts)

    # Load data
    if 'df' not in st.session_state or refresh:
        with st.spinner("Loading SMART data..."):
            st.session_state.df = load_smart_data(log_dir)

    df = st.session_state.df

    # Apply filters if they exist
    if 'df' in st.session_state and not st.session_state.df.empty:
        if 'selected_model' in locals() and selected_model != 'All':
            df = df[df['model_number'] == selected_model]
        if 'selected_capacity' in locals() and selected_capacity != 'All':
            capacity_val = float(selected_capacity.split(' ')[0])
            df = df[abs(df['capacity_tb'] - capacity_val) < 0.1]
        if 'selected_host' in locals() and selected_host != 'All':
            df = df[df['hostname'] == selected_host]

    if df.empty:
        st.error("No data available. Check the log directory path or adjust filters.")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Drives", len(df))

    with col2:
        critical_drives = len(df[df['critical_warning'] > 0])
        st.metric("Critical Warnings", critical_drives,
                 delta=f"{critical_drives}/{len(df)}" if critical_drives > 0 else None,
                 delta_color="inverse")

    with col3:
        avg_percent_used = df['percent_used'].mean()
        st.metric("Avg. Percent Used", f"{avg_percent_used:.1f}%")

    with col4:
        total_tbw = df['data_units_written'].sum()
        st.metric("Total TBW", f"{total_tbw:.1f} TB")

    st.markdown("---")

    # Critical Warnings Section
    st.header("🚨 Critical Warnings")
    critical_df = df[df['critical_warning'] > 0]

    if not critical_df.empty:
        st.error(f"⚠️ {len(critical_df)} drives have critical warnings!")

        for _, drive in critical_df.iterrows():
            warnings = interpret_critical_warning(drive['critical_warning'])
            with st.expander(f"🔴 {drive['hostname']} - {drive['serial_number']} - {drive['device']}"):
                st.write(f"**Warnings:** {', '.join(warnings)}")
                st.write(f"**Available Spare:** {drive['avail_spare']}% (Threshold: {drive['spare_thresh']}%)")
                st.write(f"**Percent Used:** {drive['percent_used']}%")
                st.write(f"**Temperature:** {drive['temperature']:.1f}°C")
    else:
        st.success("✅ All drives are healthy - no critical warnings!")

    st.markdown("---")

    # Main Dashboard
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Power On Hours")
        fig_hours = px.bar(df, x='serial_number', y='power_on_hours',
                          hover_data=['hostname', 'device', 'model_number'],
                          title="Power On Hours by Drive")
        fig_hours.update_xaxes(tickangle=45)
        st.plotly_chart(fig_hours, use_container_width=True)

        # Add human readable durations
        if st.checkbox("Show Readable Duration"):
            duration_df = df[['hostname', 'serial_number', 'model_number', 'power_on_hours']].copy()
            duration_df['duration'] = duration_df['power_on_hours'].apply(format_time_duration)
            st.dataframe(duration_df[['hostname', 'serial_number', 'model_number', 'duration']],
                        use_container_width=True)

    with col2:
        st.subheader("Percent Used")
        fig_used = px.bar(df, x='serial_number', y='percent_used',
                         color='percent_used', color_continuous_scale='RdYlGn_r',
                         hover_data=['hostname', 'device', 'model_number'],
                         title="Wear Level (% Used) by Drive")
        fig_used.update_xaxes(tickangle=45)
        fig_used.add_hline(y=80, line_dash="dash", line_color="orange",
                          annotation_text="80% Warning Level")
        st.plotly_chart(fig_used, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Total Bytes Written (TBW)")
        fig_tbw = px.bar(df, x='serial_number', y='data_units_written',
                        hover_data=['hostname', 'device', 'model_number'],
                        title="Total Terabytes Written by Drive")
        fig_tbw.update_xaxes(tickangle=45)
        st.plotly_chart(fig_tbw, use_container_width=True)

    with col4:
        st.subheader("Temperature")
        fig_temp = px.bar(df, x='serial_number', y='temperature',
                         color='temperature', color_continuous_scale='thermal',
                         hover_data=['hostname', 'device', 'model_number'],
                         title="Current Temperature by Drive")
        fig_temp.update_xaxes(tickangle=45)
        fig_temp.add_hline(y=70, line_dash="dash", line_color="orange",
                          annotation_text="70°C Warning")
        fig_temp.add_hline(y=85, line_dash="dash", line_color="red",
                          annotation_text="85°C Critical")
        st.plotly_chart(fig_temp, use_container_width=True)

    # Data Table
    st.markdown("---")
    st.subheader("📊 Drive Summary Table")

    display_df = df[['hostname', 'serial_number', 'model_number', 'capacity_tb', 'device', 'critical_warning',
                    'percent_used', 'power_on_hours', 'data_units_written',
                    'temperature', 'avail_spare', 'firmware_rev']].copy()

    display_df['critical_warning'] = display_df['critical_warning'].apply(
        lambda x: "⚠️ YES" if x > 0 else "✅ OK"
    )
    display_df['power_on_hours'] = display_df['power_on_hours'].apply(format_time_duration)
    display_df['capacity_tb'] = display_df['capacity_tb'].apply(lambda x: f"{x:.1f} TB" if x > 0 else "Unknown")
    display_df = display_df.round(2)

    st.dataframe(display_df, use_container_width=True)

    # Advanced Mode
    if show_advanced:
        st.markdown("---")
        st.header("🔧 Advanced SMART Analytics")

        # Select drive for detailed analysis
        selected_drive = st.selectbox("Select Drive for Detailed Analysis",
                                    options=df['serial_number'].unique())

        drive_data = df[df['serial_number'] == selected_drive].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Drive Details: {selected_drive}")
            st.write(f"**Host:** {drive_data['hostname']}")
            st.write(f"**Device:** {drive_data['device']}")
            st.write(f"**Model:** {drive_data['model_number']}")
            st.write(f"**Capacity:** {drive_data['capacity_tb']:.1f} TB")
            st.write(f"**Firmware:** {drive_data['firmware_rev']}")
            st.write(f"**Power On Hours:** {format_time_duration(drive_data['power_on_hours'])}")
            st.write(f"**Unsafe Shutdowns:** {drive_data['unsafe_shutdowns']:,}")
            st.write(f"**Media Errors:** {drive_data['media_errors']:,}")
            st.write(f"**Error Log Entries:** {drive_data['num_err_log_entries']:,}")

        with col2:
            st.subheader("Read/Write Statistics")
            st.write(f"**Data Written:** {drive_data['data_units_written']:.2f} TB")
            st.write(f"**Data Read:** {drive_data['data_units_read']:.2f} TB")
            st.write(f"**Host Writes:** {drive_data['host_writes']:.2f} TB")
            st.write(f"**Host Reads:** {drive_data['host_reads']:.2f} TB")

        # Full SMART data
        st.subheader("Complete SMART Data")
        with st.expander("View Raw SMART JSON"):
            st.json(drive_data['full_smart_data'])

        # SMART fields analysis
        smart_data = drive_data['full_smart_data']
        smart_fields = []

        for key, value in smart_data.items():
            if isinstance(value, (int, float)) and key != 'critical_warning':
                smart_fields.append({'Field': key, 'Value': value})

        smart_df = pd.DataFrame(smart_fields)
        if not smart_df.empty:
            st.dataframe(smart_df, use_container_width=True)

if __name__ == "__main__":
    main()