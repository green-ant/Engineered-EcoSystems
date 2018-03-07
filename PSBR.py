import time
from time import sleep
import datetime
from datetime import timedelta,datetime
import pymongo
import json

FMT='%Y-%m-%d %H:%M:%S'
class PSBR:
    def __init__(self,ID,st,et):
        self.ID=ID
        self._id=ID+":"+datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y')

        self.start_tm=st
        self.end_tm=et  
        self.tdelta=0
        self.current_stage="Initial"
        self.operational_stages=[]
        self.ph_meter=[]
        self.sensor_data=[]
        self.pHController_log=[]

        
    def light_switch(self,tm,status,Reactor,ID,stage,cmd):
        tm=datetime.fromtimestamp(time.time()).strftime(FMT)
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Light in op_st["element"]:
                    if Light["ID"].find(ID)!=-1:
                        if Light["current"]["status"]!=status:
                            print "Light Switch :"+status+" at Time="+tm
                            self.add_pHController_log(tm,cmd,Reactor)
                            Light["previous"].append(dict(Light["current"]))
                            Light["current"]["status"]=status
                            Light["current"]["timestamp"]=tm

    def mixer_switch(self,tm,status,Reactor,ID,stage):
        tm=datetime.fromtimestamp(time.time()).strftime(FMT)
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Mixer in op_st["element"]:
                    if Mixer["ID"].find(ID)!=-1:
                        if Mixer["current"]["status"]!=status:
                            print "Mixer Switch :"+status+" at Time="+tm
                            cmd=str(self.ID)+":"+ID+" "+str(status)+"\r\n"
                            self.add_pHController_log(tm,cmd,Reactor)
                            Mixer["previous"].append(dict(Mixer["current"]))
                            Mixer["current"]["status"]=status
                            Mixer["current"]["timestamp"]=tm
    

    def get_float_status(self,tm,Reactor,ID,stage):
        tm=datetime.fromtimestamp(time.time()).strftime(FMT)
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for FloatSwitch in op_st["element"]:
                    if FloatSwitch["ID"].find(ID)!=-1:
                        cmd=str(ID)+":Status\r\n"
                        Reactor.write(cmd)
                        time.sleep(5)
                        data = Reactor.readline()
                        data=data.rstrip()
                        cntrllr=data.split(':')
                        if len(cntrllr) == 2:
                            status=cntrllr[1]
                            if FloatSwitch["current"]["status"]!=status:
                                FloatSwitch["previous"].append(dict(FloatSwitch["current"]))
                                FloatSwitch["current"]["status"]=status
                                FloatSwitch["current"]["timestamp"]=tm

    def pHController_switch(self,tm,status,Reactor,ID,stage):
        tm=datetime.fromtimestamp(time.time()).strftime(FMT)
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for pHCtrllr in op_st["element"]:
                    if pHCtrllr["ID"].find(ID)!=-1:
                        if pHCtrllr["current"]["status"]!=status:
                            cmd=str(self.ID)+":"+str(ID)+" "+status+"\r\n"                    
                            self.add_pHController_log(tm,cmd,Reactor)
                            pHCtrllr["previous"].append(dict(pHCtrllr["current"]))
                            pHCtrllr["current"]["status"]=status
                            pHCtrllr["current"]["timestamp"]=tm        


    def add_phMeter(self,phMeter):
        self.ph_meter.append(phMeter)

    def add_operational_stages(self,op_stg):
        self.operational_stages.append(op_stg)

    def operation(self,Reactor):
        tm=datetime.fromtimestamp(time.time()).strftime(FMT)
        duration=(datetime.strptime(self.end_tm, FMT) - datetime.strptime(self.start_tm, FMT)).total_seconds()
        self.tdelta=(datetime.strptime(tm, FMT) - datetime.strptime(self.start_tm, FMT)).total_seconds()
        
        print "Operational Stage Started at Time="+str(datetime.strptime(self.start_tm, FMT))

        for op_st in self.operational_stages:
            print "     "+op_st["stage"]+" Stage Starts at Time="+str(datetime.strptime(op_st["start_time"], FMT))
            print "     "+op_st["stage"]+" Stage Ends at Time="+str(datetime.strptime(op_st["end_time"], FMT))


        print "Operational Stage Ends at Time="+str(datetime.strptime(self.end_tm, FMT))

        while self.tdelta<=duration:
            self.read_sensor_data(Reactor)
            time.sleep(5)
            self.read_sensor_data(Reactor)
            time.sleep(5)
            self.read_sensor_data(Reactor)
            

            tm=datetime.fromtimestamp(time.time()).strftime(FMT)

            for op_st in self.operational_stages:
                tdelta1=(datetime.strptime(tm, FMT) - datetime.strptime(op_st["start_time"], FMT)).total_seconds()
                duration1=(datetime.strptime(op_st["end_time"], FMT) - datetime.strptime(op_st["start_time"], FMT)).total_seconds()

                if tdelta1<=duration1 and tdelta1>0:

                    if op_st["status"]=="Off":
                        print "##"+op_st["stage"]+" Stage Started at Time="+tm
                        op_st["status"]="On"
                        cmd=str(self.ID)+":"+str(op_st["stage"])+" On\r\n"                    
                        self.add_pHController_log(tm,cmd,Reactor)
                        self.current_stage=op_st["stage"]                        
                        cmd= op_st["stage"]+" Switched On at "+tm 
                        
                        for elm in op_st["element"]:                    
                            
                            if elm["item"]=="Mixer":
                                self.mixer_switch(tm,"On",Reactor,elm["ID"],op_st["stage"])

                            if elm["item"]=="Light":
                                self.light_switch(tm,"On",Reactor,elm["ID"],op_st["stage"],elm["cmdOn"])

                            if elm["item"]=="FloatSwitch":
                                self.get_float_status(tm,Reactor,elm["ID"],op_st["stage"])

                            if elm["item"]=="pHController":
                                self.pHController_switch(tm,"On",Reactor,elm["ID"],op_st["stage"])
                        
                        break 

                    for elm in op_st["element"]:
                        if elm["item"]=="Mixer":
                            self.mixer_on_off(tm,op_st["start_time"],elm["intrvl_on"],elm["intrvl_off"],Reactor,elm["ID"],op_st["stage"])

                        if elm["item"]=="FloatSwitch":
                            self.get_float_status(tm,Reactor,elm["ID"],op_st["stage"])
                        
                        if elm["item"]=="pHController":
                            self.pH_Controller(tm,Reactor,elm["ID"],op_st["stage"])
                    break
                                        
                if tdelta1>=duration1 and op_st["status"]=="On":
                    op_st["status"]="Off"
                    cmd=str(self.ID)+":"+str(op_st["stage"])+" Off\r\n"                    
                    self.add_pHController_log(tm,cmd,Reactor)    
                    print "##"+op_st["stage"]+" Stage Ended at Time="+tm
                    self.current_stage="None"

                    for elm in op_st["element"]:                    
                            
                        if elm["item"]=="Mixer":
                            self.mixer_switch(tm,"Off",Reactor,elm["ID"],op_st["stage"])

                        if elm["item"]=="Light":
                            self.light_switch(tm,"Off",Reactor,elm["ID"],op_st["stage"],elm["cmdOff"])

                        if elm["item"]=="FloatSwitch":
                            self.get_float_status(tm,Reactor,elm["ID"],op_st["stage"])
                        
                        if elm["item"]=="pHController":
                            self.pHController_switch(tm,"Off",Reactor,elm["ID"],op_st["stage"])
                        
                    break 
        
            self.save_data()
        
            self.tdelta=(datetime.strptime(tm, FMT) - datetime.strptime(self.start_tm, FMT)).total_seconds()
        
        print "End of Operational Stage"
        self.save_data()
#        self.save_mongodb('psbr','mongodb://cdd:cdd123@ds135537.mlab.com:35537/psbr_v0')

   
    def add_pHController_log(self,tm,cmd,Reactor):
        Reactor.write(str(cmd))
        time.sleep(5)
        data = Reactor.readline()
        data=data.rstrip()
        cntrllr=data.split(':')

        if len(cntrllr) == 2:
            log={}
            log["msg"]=data
            log["timestamp"]=tm  
            print data
            self.pHController_log.append(log)

        self.save_mongodb('psbr','mongodb://cdd:cdd123@ds135537.mlab.com:35537/psbr_v0')

    def light_on_off(self,tm,st_tm,intrvl_on,intrvl_off,Reactor,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Light in op_st["element"]:
                    if Light["ID"].find(ID)!=-1:        
                        if self.tdelta<=dur_min and Light["current"]["status"]=="Off" and self.tdelta>0:
                            self.light_switch(tm,"On",ID,stage,Reactor)
                            return 0

                        if self.tdelta>dur_min and Light["current"]["status"]=="On":
                            self.light_switch(tm,"Off",ID,stage,Reactor)
                            return 0
            
    def mixer_on_off(self,tm,st_tm,intrvl_on,intrvl_off,Reactor,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Mixer in op_st["element"]:
                    if Mixer["ID"].find(ID)!=-1:
                        intrvl=(datetime.strptime(tm, FMT) -datetime.strptime(Mixer["current"]["timestamp"], FMT)).total_seconds()
                        if intrvl>(intrvl_on*60) and Mixer["current"]["status"]=="On": 
                            self.mixer_switch(tm,"Off",Reactor,ID,stage)
                            break

                        if intrvl>(intrvl_off*60) and Mixer["current"]["status"]=="Off": 
                            self.mixer_switch(tm,"On",Reactor,ID,stage)
                            break

    def pH_Controller(self,tm,Reactor,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for pHCtrllr in op_st["element"]:
                    if pHCtrllr["ID"].find(ID)!=-1:
                        if float(self.sensor_data[-1][str(pHCtrllr["ph_meter"])])>pHCtrllr["setpoint_ph"]:
                            cmd=str(pHCtrllr["ID"])+":"+"Dose "+pHCtrllr["dosage"]+"\r\n"
                            self.add_pHController_log(tm,cmd,Reactor)

    def add_sensor_data(self,sensor_dt):
        self.sensor_data.append(sensor_dt)

    def read_sensor_data(self,Reactor):
        snsr=[]
        cmd=str(self.ID)+":Sensor Data"+"\r\n"
        Reactor.write(cmd)
        time.sleep(5)
        data = Reactor.readline()
        data=data.rstrip()

        snsr=data.split(';')

        if len(snsr) > 2:
            tmp1=[]
            tmp1=snsr[1].split(':')
            tmp2=[]
            tmp3=[]     
            sensor_dt={}
            sensor_dt["temp"]=round(float(tmp1[1]),2)
            i=0

            for pHMtr in self.ph_meter:
                tmp2.append([])
                tmp2[i]=snsr[i+2].split(':')
                sensor_dt[pHMtr["ID"]]=round(float(tmp2[i][1]),2)
                i=i+1


            sensor_dt["timestamp"]=datetime.fromtimestamp(time.time()).strftime(FMT)
            self.add_sensor_data(sensor_dt)
            print sensor_dt
            self.save_data()

    def save_data(self):
        tm=datetime.fromtimestamp(time.time()).strftime('%m-%d')
        file_nm=tm+".json"
        with open(file_nm, 'w') as f:
            json.dump(self.__dict__, f,indent=4, sort_keys=True, separators=(',',':'))

    def save_mongodb(self,db_nm,url):
        client = pymongo.MongoClient(url)
        db = client.get_default_database()
        PSBR_db = db[db_nm]
        tm=datetime.fromtimestamp(time.time()).strftime('%m-%d')
        PSBR_db.update({'_id':self._id},{'$set':self.__dict__},True,False)
        print "MongoDB Data Saved"
