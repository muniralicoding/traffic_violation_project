import csv
import random
from datetime import datetime, timedelta

def generate_dataset(filename="traffic_violations.csv", num_records=100):
    locations = ["Sector 17, Chandigarh", "Tribune Chowk", "Housing Board Chowk", "Aroma Light Point", "Sector 43 Bus Stand", "PGI Roundabout", "Elante Mall Road"]
    vehicle_types = ["Two-Wheeler", "Four-Wheeler", "Commercial", "Three-Wheeler"]
    violation_types = ["Overspeeding", "Red-light violation", "No helmet", "No seat belt", "Illegal parking", "Wrong-side driving", "Using mobile phone", "No valid document"]
    payment_statuses = ["Paid", "Unpaid"]
    
    start_date = datetime(2023, 1, 1)
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Violation_ID", "Date", "Time", "Location", "Vehicle_Type", "Vehicle_Number", "Violation_Type", "Fine_Amount", "Payment_Status", "Repeat_Offender", "Officer_ID"])
        
        for i in range(1, num_records + 1):
            vid = f"V{i:04d}"
            v_date = start_date + timedelta(days=random.randint(0, 365))
            v_time = f"{random.randint(8, 22):02d}:{random.randint(0, 59):02d}"
            loc = random.choice(locations)
            v_type = random.choice(vehicle_types)
            v_num = f"CH01{random.choice(['A','B','C','D'])}{random.randint(1000, 9999)}"
            violation = random.choice(violation_types)
            fine = random.choice([500, 1000, 2000, 5000])
            p_status = random.choice(payment_statuses)
            repeat = random.choice(["Yes", "No"])
            officer = f"OFC{random.randint(101, 150)}"
            
            writer.writerow([vid, v_date.strftime("%Y-%m-%d"), v_time, loc, v_type, v_num, violation, fine, p_status, repeat, officer])

if __name__ == "__main__":
    generate_dataset()
    print("Dataset generated successfully as traffic_violations.csv")
