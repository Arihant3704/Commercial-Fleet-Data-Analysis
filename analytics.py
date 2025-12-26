import pandas as pd
import numpy as np

def calculate_time_diff(df):
    if 'time' not in df.columns:
        return None
    return df['time'].diff().dt.total_seconds().fillna(0)

def score_normalization(raw_score, min_val, max_val, reverse=False):
    """Normalizes a raw metric to a 1-10 scale."""
    if max_val == min_val:
        return 1
    
    norm = ((raw_score - min_val) / (max_val - min_val)) * 9 + 1
    norm = max(1, min(10, norm))
    
    if reverse:
        return 11 - norm
    return norm # 1 is Low/Good, 10 is High/Bad generally in this context

def analyze_tire_wear(df):
    """
    Algorithm to determine tire wear type/score.
    Input: DataFrame with speed, braking events.
    Output: Score 1 (Least Wear) to 10 (Most Wear).
    """
    # Features associated with tire wear: Harsh Braking, Harsh Acceleration, High Speed
    
    # 1. Calculate Acceleration (m/s^2)
    # Speed is usually in km/h. Convert to m/s: / 3.6
    
    # Check if '84_vehicle_speed' (CAN) or 'speed' (GPS) exists
    speed_col = '84_vehicle_speed' if '84_vehicle_speed' in df.columns else 'speed'
    
    if speed_col not in df.columns:
        return "N/A (No Speed Data)"

    df['velocity_ms'] = df[speed_col] / 3.6
    dt = calculate_time_diff(df)
    # Avoid div by zero
    dt[dt == 0] = 1 # fallback
    
    df['acceleration'] = df['velocity_ms'].diff().fillna(0) / dt
    
    # Thresholds (Example values, would need tuning)
    harsh_accel_threshold = 2.0 # m/s^2
    harsh_brake_threshold = -2.0 # m/s^2
    high_speed_threshold = 80 # km/h
    
    harsh_accel_count = len(df[df['acceleration'] > harsh_accel_threshold])
    harsh_brake_count = len(df[df['acceleration'] < harsh_brake_threshold])
    high_speed_time = len(df[df[speed_col] > high_speed_threshold]) # Assuming 1Hz roughly
    
    total_samples = len(df)
    if total_samples == 0:
        return 1
    
    # Raw 'Wear Index' proportional to these events per hour of driving
    # Simplifying to ratio of events
    
    wear_index = (harsh_accel_count * 2 + harsh_brake_count * 3 + high_speed_time * 0.5) / total_samples
    
    # Heuristic mapping. Let's assume 0.05 is "Bad" (5% of time spent doing crazy stuff)
    score = score_normalization(wear_index, 0, 0.05)
    return int(score)

def analyze_driver_aggressiveness(df):
    """
    Score 1-10. 1 = Least Aggressive, 10 = Most Aggressive.
    Features: Speeding, Harsh Braking/Accel, Pedal usage (if avail).
    """
    speed_col = '84_vehicle_speed' if '84_vehicle_speed' in df.columns else 'speed'
    
    if speed_col not in df.columns:
        return "N/A"
        
    df['velocity_ms'] = df[speed_col] / 3.6
    dt = calculate_time_diff(df)
    dt[dt == 0] = 1
    df['acceleration'] = df['velocity_ms'].diff().fillna(0) / dt
    
    speeding_threshold = 90 # km/h, aggressive driving
    aggr_accel = 2.5 # m/s^2
    aggr_brake = -2.5
    
    speeding_events = len(df[df[speed_col] > speeding_threshold])
    hard_maneuvers = len(df[(df['acceleration'] > aggr_accel) | (df['acceleration'] < aggr_brake)])
    
    total_samples = len(df)
    if total_samples == 0:
        return 1
        
    aggr_index = (speeding_events * 1 + hard_maneuvers * 5) / total_samples
    
    score = score_normalization(aggr_index, 0, 0.02) # stricter threshold for aggressiveness
    return int(score)

def analyze_brake_shoe_health(df):
    """
    Determine wear and tear of brake shoe.
    Features: 597_brake_switch, 521_brake_pedal_position, momentum delta.
    """
    if '597_brake_switch' not in df.columns and '521_brake_pedal_position' not in df.columns:
        return "N/A (Missing Brake Data)"
    
    speed_col = '84_vehicle_speed' if '84_vehicle_speed' in df.columns else 'speed'
    
    # We want to measure "Energy Dissipated" by brakes roughly.
    # Proportional to Sum(v^2 * dt) while braking is active.
    
    is_braking = pd.Series([False] * len(df))
    if '597_brake_switch' in df.columns:
        is_braking = is_braking | (df['597_brake_switch'] == 1)
    if '521_brake_pedal_position' in df.columns:
        is_braking = is_braking | (df['521_brake_pedal_position'] > 0)
        
    braking_df = df[is_braking]
    
    if braking_df.empty:
        return "Excellent (No Braking Recorded)"
    
    # Calculate kinetic energy factor (v^2)
    # Actually, wear is related to Force * Distance. F = ma. 
    # Let's use a simpler heuristic: Total High-Speed Braking Duration.
    
    high_load_braking = braking_df[braking_df[speed_col] > 40]
    
    wear_metric = len(high_load_braking) / len(df) if len(df) > 0 else 0
    
    # 0 = Good, 1 = Worn out
    # Health Score: 100% - normalized wear
    
    health_inv = score_normalization(wear_metric, 0, 0.2) # 1 to 10 scale of wear
    
    # Convert to category
    if health_inv <= 2: return "Good"
    if health_inv <= 6: return "Moderate Wear"
    return "High Wear (Check Brakes)"

def predict_breakdown(df):
    """
    Predict likelihood of breakdown.
    Features: Battery voltage, Coolant Temp, Engine Lamps.
    """
    risk_factors = []
    
    # 1. Battery Health
    if 'carbattery' in df.columns:
        # Assuming 24V system for trucks. < 23V is warning.
        low_batt = df[df['carbattery'] < 23.0]
        if len(low_batt) > 10: # Persistent low voltage
            risk_factors.append("Low Battery Voltage detected")
            
    # 2. Engine Coolant
    col_temp = '110_engine_coolant_temperature'
    if col_temp in df.columns:
        overheat = df[df[col_temp] > 105]
        if len(overheat) > 5:
            risk_factors.append("Engine Overheating events")
            
    # 3. Warning Lamps
    red_lamp = '5079_engine_red_stop_lamp_cmd'
    if red_lamp in df.columns:
        if df[red_lamp].max() > 0:
            risk_factors.append("Critical Engine Stop Lamp Triggered")
            
    amber_lamp = '5078_engine_amber_warning_lamp_cmd'
    if amber_lamp in df.columns:
        if df[amber_lamp].max() > 0:
            risk_factors.append("Engine Warning Lamp Triggered")
            
    if not risk_factors:
        return "Healthy", "Low Risk"
    
    if "Critical Engine Stop Lamp Triggered" in risk_factors:
        return "CRITICAL: Breakdown Imminent", "; ".join(risk_factors)
        
    return "Warning: Potential Issues", "; ".join(risk_factors)
