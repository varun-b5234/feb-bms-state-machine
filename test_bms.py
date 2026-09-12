import unittest
from bms_state_machine import BMSState, SensorData, get_next_state

class TestBMSTransitions(unittest.TestCase):

    def test_idle_to_running_when_car_on(self):
        data = SensorData(car_on=True)
        result = get_next_state(BMSState.IDLE, data)
        self.assertEqual(result, BMSState.RUNNING)

    def test_idle_to_charging_when_plugged_in(self):
        data = SensorData(plugged_in=True)
        result = get_next_state(BMSState.IDLE, data)
        self.assertEqual(result, BMSState.CHARGING)

    def test_idle_stays_idle_when_nothing_happens(self):
        data = SensorData()
        result = get_next_state(BMSState.IDLE, data)
        self.assertEqual(result, BMSState.IDLE)

    def test_running_to_fault_on_overtemp(self):
        data = SensorData(car_on=True, cell_temps=[50.0]*6)
        result = get_next_state(BMSState.RUNNING, data)
        self.assertEqual(result, BMSState.FAULT)

    def test_running_to_fault_on_overvoltage(self):
        data = SensorData(car_on=True, cell_voltages=[4.5]*6)
        result = get_next_state(BMSState.RUNNING, data)
        self.assertEqual(result, BMSState.FAULT)

    def test_running_to_idle_when_car_turned_off(self):
        data = SensorData(car_on=False)
        result = get_next_state(BMSState.RUNNING, data)
        self.assertEqual(result, BMSState.IDLE)

    def test_charging_to_balancing_when_imbalanced(self):
        data = SensorData(plugged_in=True, cell_voltages=[3.7, 3.7, 3.7, 3.7, 3.7, 3.8])
        result = get_next_state(BMSState.CHARGING, data)
        self.assertEqual(result, BMSState.BALANCING)

    def test_charging_to_idle_when_unplugged(self):
        data = SensorData(plugged_in=False)
        result = get_next_state(BMSState.CHARGING, data)
        self.assertEqual(result, BMSState.IDLE)

    def test_charging_to_fault_on_overvoltage(self):
        data = SensorData(plugged_in=True, cell_voltages=[4.5]*6)
        result = get_next_state(BMSState.CHARGING, data)
        self.assertEqual(result, BMSState.FAULT)

    def test_balancing_to_idle_when_balanced(self):
        data = SensorData(cell_voltages=[3.7]*6)
        result = get_next_state(BMSState.BALANCING, data)
        self.assertEqual(result, BMSState.IDLE)

    def test_balancing_stays_when_still_imbalanced(self):
        data = SensorData(cell_voltages=[3.7, 3.7, 3.7, 3.7, 3.7, 3.8])
        result = get_next_state(BMSState.BALANCING, data)
        self.assertEqual(result, BMSState.BALANCING)

    def test_fault_to_shutdown(self):
        data = SensorData()
        result = get_next_state(BMSState.FAULT, data)
        self.assertEqual(result, BMSState.SHUTDOWN)

    def test_shutdown_stays_shutdown(self):
        data = SensorData()
        result = get_next_state(BMSState.SHUTDOWN, data)
        self.assertEqual(result, BMSState.SHUTDOWN)


#unittest.main()