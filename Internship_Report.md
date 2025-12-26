# Fleet Vehicle Analytics Project Report

**Date:** 2025-10-27
**Subject:** Commercial Fleet Data Analysis - Internship Project

---

## 1. Project Objective
The goal of this project was to develop a "Next Generation Fleet Management Solution" by performing advanced analytics on real-world commercial truck data. The specific problems addressed were:
1.  **Tire Wear Analysis**: developing an algorithm to score tire wear based on driving patterns.
2.  **Driver Aggressiveness**: Scoring drivers based on harsh maneuvers and speeding.
3.  **Brake Shoe Health**: Determining wear and tear on brakes.
4.  **Breakdown Prediction**: Predicting potential future breakdowns based on vehicle telemetry.

## 2. Dataset Overview
The analysis was performed on real-world datasets containing two primary data streams:
*   **CAN Bus Data**: Rich telemetry including engine coolant temperature, oil pressure, warning lamps, engine usage hours, and odometer readings.
*   **GPS Data**: Location (latitude/longitude), speed, and battery voltage.

Two distinct vehicle profiles were analyzed:
*   **Rich Data (e.g., RJ47GA6350)**: Contained over 60 columns of engine parameters, enabling deep health analysis.
*   **Sparse Data (e.g., RJ47GA5867)**: Contained limited telemetry, requiring robust code that handles missing features gracefully.

## 3. Methodology & Algorithms

### A. Data Processing Pipeline
I developed a python-based pipeline (`data_loader.py`) that:
*   **Ingests** both CAN and GPS CSV files.
*   **Aligns** timestamps to merge these asynchronous data streams.
*   **Normalizes** column names to create a consistent schema for analysis.

### B. Analytical Models

#### 1. Tire Wear & Driver Aggressiveness Score (1-10)
*   **Logic**: These scores are derived from physical forces applied to the vehicle. I calculated **Acceleration** ($m/s^2$) from the speed data.
*   **Features Used**:
    *   **Harsh Acceleration**: Changes in speed > $2.0 m/s^2$.
    *   **Harsh Braking**: Deceleration < $-2.0 m/s^2$.
    *   **High Speed Events**: Duration spent above $80 km/h$.
*   **Scoring**: A normalized score where 1 represents minimal wear/calm driving and 10 represents high wear/aggressive driving.

#### 2. Brake Shoe Health
*   **Logic**: Brake wear is proportional to the energy dissipated during braking.
*   **Algorithm**: The model detects "High Load Braking" events—instances where the brake pedal is depressed (or brake switch active) while the vehicle is moving at significant speed (> $40 km/h$).
*   **Output**: Categorized as "Good", "Moderate Wear", or "High Wear".

#### 3. Breakdown Prediction
*   **Logic**: This model looks for critical warning signs that precede mechanical failure.
*   **Indicators Monitored**:
    *   **Engine Overheating**: Coolant temperature consistently > $105^\circ C$.
    *   **Battery Health**: GPS battery voltage dropping below 23.0V (indicating alternator or battery failure).
    *   **Critical Fault Codes**: Activation of the `Engine Red Stop Lamp` or `OBD Malfunction` lamps.
*   **Output**: A risk assessment of "Healthy", "Warning", or "CRITICAL".

## 4. Key Findings

The analysis of the provided fleet revealed significant insights:

| Vehicle ID | Analysis Result | Key Observations |
| :--- | :--- | :--- |
| **RJ47GA6350** | **CRITICAL RISK** | **Breakdown Imminent**. The algorithms detected active "Engine Stop" lamps and identified engine overcrowding issues. Immediate maintenance is recommended. |
| **RJ47GA6215** | **High Brake Wear** | The vehicle is often braked at high speeds, indicating a driving habit that accelerates brake shoe wear. |
| **Others** | Healthy | Other vehicles in the fleet showed nominal parameters. |

## 5. Challenges & Solutions

**Challenge: Data Sampling Resolution**
*   **Issue**: The provided dataset had a sampling rate of approximately 1 minute. Transient events like harsh braking typically last only 2-3 seconds.
*   **Impact**: Averaging speed changes over 60 seconds smoothed out the "spikes" needed to detect aggressive driving, resulting in artificially low aggressiveness scores.
*   **Solution**: I documented this limitation and focused the analysis on **sustained** indicators (like engine temperature and warning lamps) which are reliable even at lower sampling rates. I recommended increasing the telemetry frequency to 1Hz for future tire wear precision.

## 6. Conclusion
This project successfully demonstrated that automated analytics can identify at-risk vehicles before they fail. By flagging Vehicle **RJ47GA6350**, the system proved its value in potentially preventing a costly roadside breakdown. The code modules (`analytics.py`, `main.py`) are modular and ready to scale to a larger fleet.
