import datetime
from datetime import timedelta,datetime
FMT='%Y-%m-%d %H:%M:%S'
class Operational_Stage:
    def __init__(self,stage,st,et):
        self.stage=stage
        self.start_time=st
        self.end_time=et
        self.element=[]
        self.status="Off"
        self.dur_min=round((datetime.strptime(et, FMT) - datetime.strptime(st, FMT)).total_seconds()/60,3)

    def add_element(self,element):
        self.element.append(element)