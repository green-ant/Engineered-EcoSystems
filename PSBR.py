import time
from time import sleep
import datetime
from datetime import timedelta,datetime
import pymongo
import json
import sys
import glob
import serial
import re
import os

global ReactorCOM
ReactorCOM=[]

FMT='%Y-%m-%d %H:%M:%S'
class PSBR:
    def __init__(self,ID,st,et):
        self.ID=ID
        self.PID=0
        self.PID_dur_min=5
        self.PID_tm=datetime.fromtimestamp(time.time()).strftime(FMT)
        tmp=datetime.strptime(st,FMT)
        self._id=ID+"_"+datetime.strftime(tmp,'%Y-%m-%d')
        self.start_tm=st
        self.end_tm=et  
        self.tdelta=0
        self.current_stage="Initial"
        self.operational_stages=[]
        self.ph_meter=[]
        self.controller=[]
        self.sensor_data=[]
        self.Controller_log=[]
        self.get_data()

    def get_data(self):
        file_nm=self._id+".json"
        if os.path.isfile(file_nm):
            data = json.load(open(file_nm))
            self.PID=int(data["PID"])+1
            self.start_tm=data["start_tm"]
            self.end_tm=data["end_tm"]
            self.tdelta=data["tdelta"]
            self.current_stage=data["current_stage"]
            self.operational_stages=data["operational_stages"]
            self.ph_meter=data["ph_meter"]
            self.sensor_data=data["sensor_data"]
            self.Controller_log=data["Controller_log"]
            self.controller=data["controller"]
            msg="Start of Process:"+str(self.PID)
            self.add_Controller_log(self.PID_tm,msg)
            i=0
            for op_st in self.operational_stages:
                self.operational_stages[i]["status"]="Off"
                i=i+1
            self.save_data()
        else:
            self.get_port_data()

    def get_port_data(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        COM_port = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                COM_port.append(port)
            except (OSError, serial.SerialException):
                pass
        i=0
        Controller_COM={}
        for COM in COM_port:
            if COM!='AMA0':
                Controller_COM['port']=i
                ReactorCOM.append(serial.Serial(COM, 9600, timeout=.1))
                ReactorCOM[i].write("lo\r\n")
                time.sleep(5)
                data = ReactorCOM[i].readline()
                self.read_cntllr_data(ReactorCOM[i],Controller_COM)
                i=i+1
        print self.controller

    def read_cntllr_data(self,Reactor,Controller_COM):
        Reactor.write("Reactor Setup\r\n")
        time.sleep(5)
        data = Reactor.readline()
        data=data.rstrip()
        Controller_COM["cmd"]=""
        dt_cntrllr=data.split('~')
        Controller_COM["ID"]=dt_cntrllr[0]
        if len(dt_cntrllr)==2:
            elm=dt_cntrllr[1].split(',')
            for el in elm:
                Controller_COM["cmd"]=el+" "+Controller_COM["cmd"]
            Controller_COM["sent_cmd"]=""
            self.controller.append(Controller_COM.copy())


    def light_switch(self,tm,status,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Light in op_st["element"]:
                    if Light["ID"].find(ID)!=-1:
                        print "Light <"+ID+"> Switch:"+status+" at Time="+tm
                        cmd=ID+":"+str(status)
                        Light["previous"].append(dict(Light["current"]))
                        Light["current"]["status"]=status
                        Light["current"]["timestamp"]=tm
                        return cmd

    def valve_switch(self,tm,status,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Valve in op_st["element"]:
                    if Valve["ID"].find(ID)!=-1:
                        print "Valve <"+ID+"> Switch:"+status+" at Time="+tm
                        cmd=ID+":"+str(status)
                        if Valve["dur_on"]>0:
                            cmd=cmd+" for "+str(Valve["dur_on"])+" sec."
                        Valve["previous"].append(dict(Valve["current"]))
                        Valve["current"]["status"]=status
                        Valve["current"]["timestamp"]=tm


    def mixer_switch(self,tm,status,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Mixer in op_st["element"]:
                    if Mixer["ID"].find(ID)!=-1:
                        print "Mixer <"+ID+"> Switch:"+status+" at Time="+tm
                        cmd=ID+":"+str(status)
                        Mixer["previous"].append(dict(Mixer["current"]))
                        Mixer["current"]["status"]=status
                        Mixer["current"]["timestamp"]=tm 
                        return cmd

    def sensor_switch(self,tm,status,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for SensorSwitch in op_st["element"]:
                    if SensorSwitch["ID"].find(ID)!=-1:
                        print "<"+ID+"> Switch :"+status+" at Time="+tm
                        cmd=ID+":"+str(status)
                        SensorSwitch["previous"].append(dict(SensorSwitch["current"]))
                        SensorSwitch["current"]["status"]=status
                        SensorSwitch["current"]["timestamp"]=tm 
                        return cmd


    def pHController_switch(self,tm,status,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for pHCtrllr in op_st["element"]:
                    if pHCtrllr["ID"].find(ID)!=-1:
                        print "pHController <"+ID+"> Switch:"+status+" at Time="+tm
                        cmd=str(ID)+":"+status                    
                        pHCtrllr["previous"].append(dict(pHCtrllr["current"]))
                        pHCtrllr["current"]["status"]=status
                        pHCtrllr["current"]["timestamp"]=tm 
                        return cmd 

    def mlvss_switch(self,tm,dis,ID,stage):
        cmd="Effluent@"+str(dis)
        

    def add_phMeter(self,phMeter):
        self.ph_meter.append(phMeter)

    def add_operational_stages(self,op_stg):
        self.operational_stages.append(op_stg)

    def operation(self):
        tm=datetime.fromtimestamp(time.time()).strftime(FMT)
        duration=(datetime.strptime(self.end_tm, FMT) - datetime.strptime(self.start_tm, FMT)).total_seconds()
        self.tdelta=(datetime.strptime(tm, FMT) - datetime.strptime(self.start_tm, FMT)).total_seconds()
        
        print "Operational Stage Started at Time="+str(datetime.strptime(self.start_tm, FMT))

        for op_st in self.operational_stages:
            print "     "+op_st["stage"]+" Stage Starts at Time="+str(datetime.strptime(op_st["start_time"], FMT))
            print "     "+op_st["stage"]+" Stage Ends at Time="+str(datetime.strptime(op_st["end_time"], FMT))


        print "Operational Stage Ends at Time="+str(datetime.strptime(self.end_tm, FMT))

        while self.tdelta<=duration:
            self.read_sensor_data()
            time.sleep(5)
            self.read_sensor_data()
            time.sleep(5)
            self.read_sensor_data()
            tm=datetime.fromtimestamp(time.time()).strftime(FMT)

            for op_st in self.operational_stages:
                tdelta1=(datetime.strptime(tm, FMT) - datetime.strptime(op_st["start_time"], FMT)).total_seconds()
                duration1=(datetime.strptime(op_st["end_time"], FMT) - datetime.strptime(op_st["start_time"], FMT)).total_seconds()

                if tdelta1<=duration1 and tdelta1>0:
                    if op_st["status"]=="Off":
                        print "##"+op_st["stage"]+" Stage Started at Time="+tm
                        op_st["status"]="On"
                        msg=str(self.ID)+":"+str(op_st["stage"])+" "+op_st["status"]                    
                        self.add_Controller_log(tm,msg)
                        self.current_stage=op_st["stage"]                        
                        cmd=";"

                        for elm in op_st["element"]:                    
                            if elm["item"]=="Mixer":
                                cmd=cmd+self.mixer_switch(tm,"On",elm["ID"],op_st["stage"])+";"
                            if elm["item"]=="Valve":
                                if elm["dur_on"]>0:
                                    cmd=cmd+str(elm["ID"])+"@"+str(elm["dur_on"])+";"
                                else:
                                    cmd=cmd+elm["ID"]+":On"+";"
                            if elm["item"]=="Light":
                                cmd=cmd+self.light_switch(tm,"On",elm["ID"],op_st["stage"])+";"
                            if elm["item"]=="Sensor":
                                cmd=cmd+self.sensor_switch(tm,"On",elm["ID"],op_st["stage"])+";"
                            if elm["item"]=="pHController":
                                cmd=cmd+self.pHController_switch(tm,"On",elm["ID"],op_st["stage"])+";"
                            

                        self.add_ControllerCOM_log(tm,cmd)
                        break 

                    for elm in op_st["element"]:
                        if elm["item"]=="Mixer":
                            self.mixer_on_off(tm,op_st["start_time"],elm["intrvl_on"],elm["intrvl_off"],elm["ID"],op_st["stage"])
                        if elm["item"]=="pHController":
                            self.pH_Controller(tm,elm["ID"],op_st["stage"])
                            time.sleep(30)
                    break
                                        
                if tdelta1>=duration1 and op_st["status"]=="On":
                    print "##"+op_st["stage"]+" Stage Ended at Time="+tm
                    op_st["status"]="Off"
                    msg=str(self.ID)+":"+str(op_st["stage"])+" "+op_st["status"]                    
                    self.add_Controller_log(tm,msg)
                    self.current_stage="None"
                    cmd=""
                    for elm in op_st["element"]:                    
                        if elm["item"]=="Mixer":
                            cmd=cmd+self.mixer_switch(tm,"Off",elm["ID"],op_st["stage"])+";"
                        if elm["item"]=="Light":
                            cmd=cmd+self.light_switch(tm,"Off",elm["ID"],op_st["stage"])+";"
                        if elm["item"]=="Valve":
                            self.valve_switch(tm,"Off",elm["ID"],op_st["stage"])
                            cmd=cmd+elm["ID"]+":Off"+";"
                        if elm["item"]=="Sensor":
                            cmd=cmd+self.sensor_switch(tm,"Off",elm["ID"],op_st["stage"])+";"
                        if elm["item"]=="pHController":
                            cmd=cmd+self.pHController_switch(tm,"Off",elm["ID"],op_st["stage"])+";"
                    self.add_ControllerCOM_log(tm,cmd)
                    break 
        
            self.save_data()
            self.tdelta=(datetime.strptime(tm, FMT) - datetime.strptime(self.start_tm, FMT)).total_seconds()
            self.PID_tdelta=((datetime.strptime(tm, FMT) - datetime.strptime(self.PID_tm, FMT)).total_seconds())/60
            if self.PID_tdelta>=self.PID_dur_min:
                msg="End of Process:"+str(self.PID)
                self.add_Controller_log(tm,msg)
                self.save_data()
                return 0
        
        print "End of Operational Stage"
        self.save_data()

    def add_Controller_log(self,tm,msg):        
        log={}
        log["msg"]=msg
        log["timestamp"]=tm  
        self.Controller_log.append(log)

    def add_ControllerCOM_log(self,tm,cmd):
        tmp_dtStrng=cmd.split(';')
        for Cntrllr in self.controller:
            j=0
            Cntrllr['sent_cmd']=""
            keyWords=Cntrllr['cmd'].split(' ')

            for keyWord in keyWords:
                i=0
                if len(keyWord)>=2:
                    for dtStrng in tmp_dtStrng:
                        if keyWord in dtStrng:
                            tmp_dtStrng[i]=" "
                            Cntrllr['sent_cmd']=dtStrng+";"+Cntrllr['sent_cmd']
                            j=j+1
                        i=i+1
                        
            if j>0:
                Cntrllr['sent_cmd']=str(Cntrllr['ID'])+"~"+Cntrllr['sent_cmd']+"\r\n"
                print "Command sent to Controller:"+Cntrllr['sent_cmd']
                ReactorCOM[Cntrllr['port']].write(str(Cntrllr['sent_cmd']))
                time.sleep(5)
                data = ReactorCOM[Cntrllr['port']].readline()
                data=data.rstrip()
                cntrllr=data.split('~')
                if len(cntrllr) >= 2:
                    log={}
                    print cntrllr
                    log["msg"]=data
                    log["timestamp"]=tm
                    self.Controller_log.append(log)

    def light_on_off(self,tm,st_tm,intrvl_on,intrvl_off,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Light in op_st["element"]:
                    if Light["ID"].find(ID)!=-1:
                        intrvl=(datetime.strptime(tm, FMT) -datetime.strptime(Light["current"]["timestamp"], FMT)).total_seconds()
                        if intrvl>(intrvl_on*60) and Light["current"]["status"]=="On": 
                            cmd=self.light_switch(tm,"Off",ID,stage)
                            self.add_ControllerCOM_log(tm,cmd)
                            break
                        if intrvl>(intrvl_off*60) and Light["current"]["status"]=="Off": 
                            cmd=self.light_switch(tm,"On",ID,stage)
                            self.add_ControllerCOM_log(tm,cmd)
                            break
            
    def mixer_on_off(self,tm,st_tm,intrvl_on,intrvl_off,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for Mixer in op_st["element"]:
                    if Mixer["ID"].find(ID)!=-1:
                        intrvl=(datetime.strptime(tm, FMT) -datetime.strptime(Mixer["current"]["timestamp"], FMT)).total_seconds()
                        if intrvl>(intrvl_on*60) and Mixer["current"]["status"]=="On": 
                            cmd=self.mixer_switch(tm,"Off",ID,stage)
                            self.add_ControllerCOM_log(tm,cmd)
                            break
                        if intrvl>(intrvl_off*60) and Mixer["current"]["status"]=="Off": 
                            cmd=self.mixer_switch(tm,"On",ID,stage)
                            self.add_ControllerCOM_log(tm,cmd)
                            break

    def pH_Controller(self,tm,ID,stage):
        for op_st in self.operational_stages:
            if op_st["stage"]==stage:
                for pHCtrllr in op_st["element"]:
                    if pHCtrllr["ID"].find(ID)!=-1:
                        if float(self.sensor_data[-1][str(pHCtrllr["ph_meter"])])>pHCtrllr["setpoint_ph"]:
                            cmd=str(pHCtrllr["ID"])+":Dose_"+pHCtrllr["dosage"]+"@2"
                            self.add_ControllerCOM_log(tm,cmd)

    def add_sensor_data(self,sensor_dt):
        self.sensor_data.append(sensor_dt)

    def read_sensor_data(self):
        snsr=[]
        sensor_dt={}
        cmd="Sensor_Data"
        for Cntrllr in self.controller:
            keyWords=Cntrllr['cmd'].split(' ')
            for keyWord in keyWords:
                if len(keyWord)>=2:
                    if len(re.findall(keyWord, cmd))>=1:
                        Cntrllr['sent_cmd']=str(Cntrllr['ID'])+"~Sensor_Data\r\n"
                        ReactorCOM[Cntrllr['port']].write(str(Cntrllr['sent_cmd']))
                        time.sleep(5)
                        Cntrllr['sent_cmd']=""
                        data = ReactorCOM[Cntrllr['port']].readline()
                        data=data.rstrip()
                        snsr=data.split(';')
                        if len(snsr)>1:
                            for i in range(1,len(snsr)):
                                tmp=snsr[i].split(':')
                                if len(tmp)>1:
                                    sensor_dt[tmp[0]]=tmp[1]
        if len(sensor_dt)>0:
            sensor_dt["timestamp"]=datetime.fromtimestamp(time.time()).strftime(FMT)
            print sensor_dt
            self.add_sensor_data(sensor_dt) 
            self.save_data()

    def save_data(self):
        file_nm=self._id+".json"
        with open(file_nm, 'w') as f:
            json.dump(self.__dict__, f,indent=4, sort_keys=True, separators=(',',':'))

    def save_mongodb(self,db_nm,url):
        client = pymongo.MongoClient(url)
        db = client.get_default_database()
        PSBR_db = db[db_nm]
        tm=datetime.fromtimestamp(time.time()).strftime('%m-%d')
        PSBR_db.update({'_id':self._id},{'$set':self.__dict__},True,False)
        print "MongoDB Data Saved"
