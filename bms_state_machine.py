from enum import Enum

class BMSState(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    CHARGING = "CHARGING"
    BALANCING = "BALANCING"
    FAULT = "FAULT"
    SHUTDOWN = "SHUTDOWN"


from dataclasses import dataclass, field
from typing import List

@dataclass
class SensorData:
    cell_voltages: List[float] = field(default_factory=lambda:[3.7]*6)
    cell_temps: List[float] = field(default_factory=lambda:[25.0]*6)
    car_on: bool = False
    plugged_in: bool = False

test_data = SensorData()
print(test_data)

MAX_VOLTAGE = 4.2      
MIN_VOLTAGE = 2.5      
MAX_TEMP = 45.0        
VOLTAGE_IMBALANCE_THRESH = 0.05  

def has_fault_condition(data: SensorData):
    for v in data.cell_voltages:
        if v>MAX_VOLTAGE or v<MIN_VOLTAGE:
            return True
    for t in data.cell_temps:
        if t >MAX_TEMP:
            return True
    return False

def needs_balancing(data: SensorData):
    return (max(data.cell_voltages) - min(data.cell_voltages)) 

def get_next_state(current_state: BMSState, data: SensorData):
    if current_state == BMSState.IDLE:
        if data.car_on:
            return BMSState.RUNNING
        if data.plugged_in:
            return BMSState.CHARGING
        return BMSState.IDLE

    elif current_state == BMSState.RUNNING:
        if has_fault_condition(data):
            return BMSState.FAULT
        if not data.car_on:
            return BMSState.IDLE
        return BMSState.RUNNING

    elif current_state == BMSState.CHARGING:
        if has_fault_condition(data):
            return BMSState.FAULT
        if not data.plugged_in:
            return BMSState.IDLE
        if needs_balancing(data):
            return BMSState.BALANCING
        return BMSState.CHARGING

    elif current_state == BMSState.BALANCING:
        if has_fault_condition(data):
            return BMSState.FAULT
        if not needs_balancing(data):
            return BMSState.IDLE
        return BMSState.BALANCING

    elif current_state == BMSState.FAULT:
        return BMSState.SHUTDOWN

    elif current_state == BMSState.SHUTDOWN:
        return BMSState.SHUTDOWN  

    return current_state

def run_simulation(initial_state: BMSState, sensor_readings_over_time: List[SensorData]):
    current_state = initial_state
    print(f"Starting state: {current_state}")

    for tick, data in enumerate(sensor_readings_over_time):
        next_state = get_next_state(current_state, data)
        if next_state != current_state:
            print(f"Tick {tick}: {current_state} -> {next_state} (data: {data})")
            send_can_message(next_state)
        current_state = next_state

    print(f"Final state: {current_state}")
    return current_state

def simulate_normal_drive(num_ticks: int = 5):
    return [SensorData(car_on=True) for _ in range(num_ticks)]

def simulate_overheat_while_driving():
    return [
        SensorData(car_on=True),
        SensorData(car_on=True, cell_temps=[30.0]*6),
        SensorData(car_on=True, cell_temps=[40.0]*6),
        SensorData(car_on=True, cell_temps=[50.0]*6),  
    ]

def simulate_charge_and_balance():
    return [
        SensorData(plugged_in=True, cell_voltages=[3.7]*6),
        SensorData(plugged_in=True, cell_voltages=[3.7, 3.7, 3.7, 3.7, 3.7, 3.8]),  
        SensorData(plugged_in=True, cell_voltages=[3.7]*6),  
        SensorData(plugged_in=False),
    ]
def send_can_message(state: BMSState):
    print(f"[CAN] Broadcasting bms_state = {state.value}")

#print(" Normal Drive:")
#run_simulation(BMSState.IDLE, simulate_normal_drive())

#print("Oerheat While Driving:")
#run_simulation(BMSState.IDLE, simulate_overheat_while_driving())

print("Charge + Balance:")
run_simulation(BMSState.IDLE, simulate_charge_and_balance())


