class pHController:
    def __init__(self,ID,ph_meter,temp_sensor,tm):
        self.ID=ID
        self.item="pHController"
        self.current={}
        self.current["status"]="Off"
        self.current["timestamp"]=tm
        self.previous=[]
        self.ph_meter=ph_meter
        self.dosage="CO2"
        self.status="Off"
        self.setpoint_ph=7.3
        self.temp_sensor=temp_sensor
