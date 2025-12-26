import pandas as pd
import glob
import os

def load_data(vehicle_id, can_dir, gps_dir):
    """
    Loads and merges CAN and GPS data for a specific vehicle.
    Returns a unified DataFrame sorted by time.
    """
    vehicle_can_files = glob.glob(os.path.join(can_dir, "**", f"{vehicle_id}.csv"), recursive=True)
    vehicle_gps_files = glob.glob(os.path.join(gps_dir, "**", f"{vehicle_id}.csv"), recursive=True)

    can_df = pd.DataFrame()
    gps_df = pd.DataFrame()

    if vehicle_can_files:
        print(f"Loading CAN data from {vehicle_can_files[0]}...")
        can_df = pd.read_csv(vehicle_can_files[0])
        can_df['time'] = pd.to_datetime(can_df['time'])
        # Rename columns to be more friendly if needed, or stick to raw 104_... format
        # For now, we keep raw names but ensure numeric conversion where possible
        for col in can_df.columns:
            if col != 'time':
                can_df[col] = pd.to_numeric(can_df[col], errors='coerce')

    if vehicle_gps_files:
        print(f"Loading GPS data from {vehicle_gps_files[0]}...")
        gps_df = pd.read_csv(vehicle_gps_files[0])
        gps_df['time'] = pd.to_datetime(gps_df['time'])
        for col in gps_df.columns:
            if col != 'time':
                gps_df[col] = pd.to_numeric(gps_df[col], errors='coerce')

    if can_df.empty and gps_df.empty:
        return pd.DataFrame()

    if can_df.empty:
        return gps_df.sort_values('time')
    
    if gps_df.empty:
        return can_df.sort_values('time')

    # Merge on time using nearest tolerance if timestamps don't align perfectly (likely)
    # CAN data might be higher frequency or different clock.
    # We'll use a merge_asof
    can_df = can_df.sort_values('time')
    gps_df = gps_df.sort_values('time')

    # We treat CAN as the base because it has the engine data, but GPS has speed too.
    # Let's try to merge keeping all data. ASOF merge direction 'nearest'
    merged_df = pd.merge_asof(can_df, gps_df, on='time', direction='nearest', tolerance=pd.Timedelta('1min'), suffixes=('_can', '_gps'))
    
    return merged_df

def get_list_of_vehicles(can_dir):
    files = glob.glob(os.path.join(can_dir, "**", "*.csv"), recursive=True)
    return [os.path.splitext(os.path.basename(f))[0] for f in files]
