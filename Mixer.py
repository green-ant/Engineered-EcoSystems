class Mixer:
    def __init__(self,ID,intrvl_on,intrvl_off,tm):
        self.ID=ID
        self.intrvl_on=intrvl_on
        self.intrvl_off=intrvl_off
        self.current={}
        self.current["status"]="Off"
        self.current["timestamp"]=tm
        self.previous=[]
        self.item="Mixer"
