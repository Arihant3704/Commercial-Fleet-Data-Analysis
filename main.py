import os
import pandas as pd
from data_loader import load_data, get_list_of_vehicles
from analytics import (
    analyze_tire_wear, 
    analyze_driver_aggressiveness, 
    analyze_brake_shoe_health, 
    predict_breakdown
)

# Configuration
CAN_DIR = '/home/arihant/Downloads/cim intership/candata_KM Trans (1) (3)/km'
GPS_DIR = '/home/arihant/Downloads/cim intership/gpsdata_KM Trans (1) (2)/km'
OUTPUT_FILE = 'fleet_analytics_report.csv'

def main():
    print("Starting Fleet Analytics...")
    
    vehicles = get_list_of_vehicles(CAN_DIR)
    results = []
    
    for vehicle_id in vehicles:
        print(f"\nProcessing Vehicle: {vehicle_id}")
        try:
            df = load_data(vehicle_id, CAN_DIR, GPS_DIR)
            
            if df.empty:
                print(f"No data found for {vehicle_id} (or merge failed). Skipping.")
                continue
                
            # Run Analytics
            tire_score = analyze_tire_wear(df)
            aggr_score = analyze_driver_aggressiveness(df)
            brake_health = analyze_brake_shoe_health(df)
            breakdown_status, risk_details = predict_breakdown(df)
            
            results.append({
                'VehicleID': vehicle_id,
                'TireWearScore': tire_score,
                'DriverAggressivenessScore': aggr_score,
                'BrakeShoeHealth': brake_health,
                'BreakdownRiskStatus': breakdown_status,
                'RiskDetails': risk_details
            })
            
        except Exception as e:
            print(f"Error processing {vehicle_id}: {e}")
            
    if not results:
        print("No results generated.")
        return

    # Export to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nAnalysis Complete. Report saved to {OUTPUT_FILE}")
    print(results_df)

if __name__ == "__main__":
    main()
