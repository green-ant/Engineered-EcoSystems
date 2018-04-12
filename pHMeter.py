
class pHMeter:
    def __init__(self,ID):
        self.ID=ID
        self.Const={}
        self.Const["Slope"]=0
        self.Const["Constant"]=0

    def read_pHcalib_data(self,Reactor):
        snsr=[]
        j=0
        print "Calib Request Sent for "+str(pHMtr["ID"])
        cmd=str(self.ID)+":Calib_pH\r\n"
        Reactor.write(cmd)
        time.sleep(5)
        data = Reactor.readline()
        data=data.rstrip()        
        snsr=data.split(';')
            
        if len(snsr)==3:
            tmp=[]
            tmp.append([])
            tmp[0]=snsr[1].split(':')
            self.ph_meter[j]["Const"]["Slope"]=tmp[0][1]
                
            tmp.append([])
            tmp[1]=snsr[2].split(':')
            self.ph_meter[j]["Const"]["Constant"]=tmp[1][1]
            j=j+1
        self.save_data()

    def get_calibration(self,Reactor,smpl_no):
        snsr=[]
        
        print "pH Calibration"
        cmd=str(self.ID)+":pH_Calibration_Values\r\n"
        Reactor.write(cmd)
        time.sleep(5)
        data = Reactor.readline()
        data=data.rstrip()       
        snsr=data.split(';')
        tmp=[]
        i=0
        if len(snsr)==3:
            tmp.append([])
            tmp[i]=snsr[i+1].split(':')
            self.Buffer["pH"][smpl_no]=round(float(tmp[i][1]),2)
            i=i+1
            tmp.append([])
            tmp[i]=snsr[i+1].split(':')
            self.Buffer["Voltage"][smpl_no]=round(float(tmp[i][1]),2)
            
    def cal_calib_constant(self):
        xsum=0
        x2sum=0
        ysum=0
        xysum=0
        n=3
        for i in range(n):
            xsum=xsum+self.Buffer["Voltage"][i]
            ysum=ysum+self.Buffer["pH"][i]
            x2sum=x2sum+pow(self.Buffer["Voltage"][i],2)
            xysum=xysum+self.Buffer["Voltage"][i]*self.Buffer["pH"][i]

        self.Buff_Const["Slope"]=round((n*xysum-xsum*ysum)/(n*x2sum-xsum*xsum),2)        
        self.Buff_Const["Constant"]=round((x2sum*ysum-xsum*xysum)/(x2sum*n-xsum*xsum),2)

    def calib_page(self,Reactor,no,pHCtrllr,ph_val):
        self.Buffer["pH"][no]=ph_val        
        self.get_calibration(Reactor,no)
        FMT='%Y-%m-%d'
        ph_id=self.get_ph_mtr_id(pHCtrllr)
        lcd_txt=["####################","####################","####################","####################"]
        lcd_txt[0]="PSBR "+str(self.ID)
        lcd_txt[1]="Prev Calib "+str(pHCtrllr["ph_meter"])+"="+str(self.Buffer["pH"][no])
        lcd_txt[3]="Sample No:"+str(no+1)+" Val="+str(self.Buffer["Voltage"][no])
        lcd_txt[2]="m:"+str(self.ph_meter[ph_id]["Const"]["Slope"])+" c:"+str(self.ph_meter[ph_id]["Const"]["Slope"])+" Buf.Sol"
        self.display_txt(lcd_txt)
        
    def calib_output(self,Reactor,pHCtrllr):
        self.cal_calib_constant()
        lcd_txt=["####################","####################","####################","####################"]
        lcd_txt[0]="#"+str(self.ID)+"# -1-  -2-  -3-   "
        lcd_txt[1]="pH    "+str(self.Buffer["pH"][0])+" "+str(self.Buffer["pH"][1])+" "+str(self.Buffer["pH"][2])
        lcd_txt[2]="Val   "+str(self.Buffer["Voltage"][0])+" "+str(self.Buffer["Voltage"][1])+" "+str(self.Buffer["Voltage"][2])
        lcd_txt[3]="m="+str(self.Buff_Const["Slope"])+" c="+str(self.Buff_Const["Constant"])
        self.display_txt(lcd_txt)
        
    def save_ph_calib_data(self,Reactor,pHCtrllr):
        tm=datetime.fromtimestamp(time.time()).strftime(FMT)
        print "Saving pH Calibration Constant"
        cmd=str(pHCtrllr["ph_meter"])+":Constant"+"\r\n"
        self.add_pHController_log(tm,cmd,Reactor)

        cmd=str(self.Buff_Const["Constant"])+"\r\n"
        self.add_pHController_log(tm,cmd,Reactor)
        
        print "Saving pH Calibration Slope"
        cmd=str(pHCtrllr["ph_meter"])+":Slope"+"\r\n"
        self.add_pHController_log(tm,cmd,Reactor)

        cmd=str(self.Buff_Const["Slope"])+"\r\n"
        self.add_pHController_log(tm,cmd,Reactor)

    def ph_calib_interface1(self,Reactor):
        
        self.Buffer={}
        self.Buffer["Voltage"]=[0,0,0]
        self.Buffer["pH"]=[0,0,0]
        self.Buff_Const={}

        lcd_txt=["####################","####################","####################","####################"]
        lcd_txt[0]="#PSBR# pHCalibration "
        i=0
        for pHCtrllr in self.ph_controller:
            lcd_txt[i+1]="pHController "+str(pHCtrllr["ID"])+"  Opt:"+str(i+1)
            i=i+1
        self.display_txt(lcd_txt)
        inp=raw_input("Input your option:")
        if(int(inp)<=len(self.ph_controller)):
            self.ph_calib_interface2(Reactor,self.ph_controller[int(inp)-1])

    def ph_calib_interface2(self,Reactor,pHCtrllr):
        ph=raw_input("Val1 pH>>")
        print "Wait for 5 Sec"
        time.sleep(5)
        self.calib_page(Reactor,0,self.ph_controller[0],ph)

        ph=raw_input("Val2 pH>>")
        print "Wait for 5 Sec"
        time.sleep(5)
        self.calib_page(Reactor,1,self.ph_controller[0],ph)

        ph=raw_input("Val3 pH>>")
        print "Wait for 5 Sec"
        time.sleep(5)
        self.calib_page(Reactor,2,self.ph_controller[0],ph)

        self.calib_output(Reactor,self.ph_controller[0])

        ph=raw_input("Save data(Y/N)>>")
        if(ph=='Y'):
            self.save_ph_calib_data(Reactor,pHCtrllr)

    def display_txt(self,lcd_txt):
        print " "
        for i in range(4):
            print lcd_txt[i]