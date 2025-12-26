# Commercial Fleet Data Analysis

## Project Overview
This repository contains the source code and documentation for a "Next Generation Fleet Management Solution". The project analyzes telemetry data (CAN bus and GPS) from commercial trucks to derive actionable insights regarding vehicle health and driver behavior.

**Key Analytics Developed:**
*   **Tire Wear Score**: Algorithms to estimate tire degradation based on harsh acceleration, braking, and high-speed cornering.
*   **Driver Aggressiveness**: Scoring system (1-10) to rate driving safety based on speeding and kinetic events.
*   **Brake Shoe Health**: Predictive maintenance indicators for brake wear using pedal actuation data at speed.
*   **Breakdown Prediction**: Logic to flag critical faults (Engine Overheating, Low Battery, Stop Lamps) before catastrophic failure occurs.

## Repository Structure
*   `main.py`: The entry point script. Runs the analysis and generates reports.
*   `analytics.py`: Library containing the core algorithms for vehicle scoring and health checks.
*   `data_loader.py`: Utility module for ingesting, cleaning, and merging asynchronous CAN/GPS data streams.
*   `Internship_Report.md`: Comprehensive technical report detailing methodology, algorithms, and key findings.
*   `fleet_analytics_report.csv`: Sample output report generated from the dataset.

## Setup & Usage

### 1. Requirements
*   Python 3.8+
*   Pandas
*   Numpy

### 2. Installation
```bash
git clone https://github.com/Arihant3704/Commercial-Fleet-Data-Analysis.git
cd Commercial-Fleet-Data-Analysis
pip install pandas numpy
```

### 3. Running the Analysis
The project is pre-configured to run on the included dataset.
```bash
python main.py
```
This will process the vehicle data in the internal folders and output `fleet_analytics_report.csv`.

## Methodology
The system handles sparse sensor data (missing brake sensors on some units) vs. rich telemetry (full engine braking and torque data) by using adaptive feature selection. Time-series data from GPS (1Hz or lower) is merged with CAN event data to form a unified timeline for analysis.

---
*Internship Project Submission - 2025*
