"""
Sensor Simulator - Simulates 50+ factory sensors broadcasting MQTT data.

This simulates:
- 3 production lines
- 4 sensors per line (temperature, vibration, throughput, pressure)
- Line 2 gradually develops a bearing failure pattern over 3 hours
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_PREFIX = "factory/line"

# Simulation state
start_time = time.time()

def generate_sensor_reading(line_number, sensor_type, elapsed_minutes):
    """Generate realistic sensor reading with failure pattern on Line 2."""
    
    # Line 2 develops bearing failure after 180 minutes (3 hours)
    is_line_2_failing = (line_number == 2 and elapsed_minutes > 180)
    
    if sensor_type == "temperature":
        # Normal: 70-75°C
        if is_line_2_failing:
            # Temperature rises gradually: 75°C → 85°C over 1 hour
            failure_progress = min((elapsed_minutes - 180) / 60, 1.0)
            base_temp = 75 + (failure_progress * 10)
            temp = base_temp + random.uniform(-1, 1)
            status = "critical" if temp > 80 else "warning"
        else:
            temp = 72 + random.uniform(-3, 3)
            status = "warning" if temp > 75 else "normal"
        
        return {
            "value": round(temp, 2),
            "unit": "celsius",
            "status": status
        }
    
    elif sensor_type == "vibration":
        # Normal: 3-4 mm/s
        if is_line_2_failing:
            # Vibration increases: 4 mm/s → 10 mm/s
            failure_progress = min((elapsed_minutes - 180) / 60, 1.0)
            base_vib = 4 + (failure_progress * 6)
            vib = base_vib + random.uniform(-0.3, 0.3)
            status = "critical" if vib > 8.5 else "warning"
        else:
            vib = 3.5 + random.uniform(-0.5, 0.5)
            status = "warning" if vib > 4.5 else "normal"
        
        return {
            "value": round(vib, 2),
            "unit": "mm/s",
            "status": status
        }
    
    elif sensor_type == "throughput":
        # Normal: 165-175 units/hr
        if is_line_2_failing:
            # Throughput drops: 170 → 130 units/hr
            failure_progress = min((elapsed_minutes - 180) / 60, 1.0)
            base_throughput = 170 - (failure_progress * 40)
            throughput = base_throughput + random.uniform(-5, 5)
            status = "warning" if throughput < 150 else "normal"
        else:
            throughput = 170 + random.uniform(-5, 5)
            status = "normal"
        
        return {
            "value": round(throughput, 1),
            "unit": "units/hr",
            "status": status
        }
    
    elif sensor_type == "pressure":
        # Normal: 100-110 PSI
        pressure = 105 + random.uniform(-5, 5)
        status = "warning" if pressure < 95 or pressure > 115 else "normal"
        
        return {
            "value": round(pressure, 1),
            "unit": "psi",
            "status": status
        }

def main():
    """Main simulation loop."""
    
    # Connect to MQTT broker
    print("Connecting to MQTT broker...")
    client = mqtt.Client()
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        print("Make sure Mosquitto is running!")
        return
    
    print("\nStarting sensor simulation...")
    print("Broadcasting data every 5 seconds")
    print("Line 2 will develop bearing failure after 3 hours (180 minutes)")
    print("Press Ctrl+C to stop\n")
    
    lines = [1, 2, 3]
    sensor_types = ["temperature", "vibration", "throughput", "pressure"]
    
    try:
        while True:
            elapsed_minutes = (time.time() - start_time) / 60
            
            # For each production line
            for line_number in lines:
                # For each sensor type
                for sensor_type in sensor_types:
                    # Generate reading
                    reading = generate_sensor_reading(line_number, sensor_type, elapsed_minutes)
                    
                    # Create sensor name
                    sensor_name = f"motor_{line_number}{'abc'[line_number-1]}_{sensor_type}"
                    
                    # Create payload
                    payload = {
                        "id": f"reading_{int(time.time())}_{line_number}_{sensor_type}",
                        "line_number": line_number,
                        "sensor_name": sensor_name,
                        "sensor_type": sensor_type,
                        "value": reading["value"],
                        "unit": reading["unit"],
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "status": reading["status"]
                    }
                    
                    # Publish to MQTT
                    topic = f"{TOPIC_PREFIX}/{line_number}/{sensor_type}"
                    client.publish(topic, json.dumps(payload))
                    
                    # Print status (only show warnings/critical)
                    if reading["status"] != "normal":
                        print(f"[{reading['status'].upper()}] Line {line_number} {sensor_type}: {reading['value']} {reading['unit']}")
            
            # Print progress every minute
            if int(elapsed_minutes) % 1 == 0 and time.time() - start_time < 3:
                print(f"Elapsed: {int(elapsed_minutes)} minutes")
                if elapsed_minutes < 180:
                    print(f"   Line 2 bearing failure in: {int(180 - elapsed_minutes)} minutes")
            
            # Wait 5 seconds before next batch
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nStopping sensor simulation...")
        client.disconnect()
        print("Disconnected from MQTT broker")

if __name__ == "__main__":
    main()