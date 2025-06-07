#!/bin/bash
# NVMe SMART Dashboard Runner
# Activates virtual environment and starts Streamlit dashboard

echo "🚀 Starting NVMe SMART Dashboard..."
echo "Dashboard will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop the dashboard"
echo ""
echo "📋 Features:"
echo "  - Critical warnings monitoring"
echo "  - Power on hours tracking"
echo "  - Percent used monitoring"
echo "  - TBW (Total Bytes Written) analytics"
echo "  - Temperature monitoring"
echo "  - Filter by model, capacity, and host"
echo "  - Advanced mode with detailed analytics"
echo ""

# Activate virtual environment and run Streamlit
source nvme_dashboard_env/bin/activate
streamlit run nvme_dashboard.py