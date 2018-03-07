
class pHCalibration:
	def __init__(self,ID):
		self.ReactorID=ID
		self.FMT='%Y-%m-%d %H:%M:%S'
		self.Time=datetime.fromtimestamp(time.time()).strftime(self.FMT)	
		self.Buffer={}
		self.Buffer[0]={}
		self.Buffer[1]={}
		self.Buffer[2]={}
		self.Const={}
		self.Temp=0
		self.Const["Slope"]=0
		self.Const["Constant"]=0
		self.cnt=0
		self.lcd_txt=["####################","####################","####################","####################"]

	def read_buff_data(self,ph,volt):
		n=3
		for i in range(n):
			self.Buffer[i]["Buffer_Voltage"]=volt[i]
			self.Buffer[i]["Buffer_pH"]=ph[i]

	def cal_calib_constant(self):
		xsum=0
		x2sum=0
		ysum=0
		xysum=0
		n=3
		for i in range(n):
			xsum=xsum+self.Buffer[i]["Buffer_Voltage"]
			ysum=ysum+self.Buffer[i]["Buffer_pH"]
			x2sum=x2sum+pow(self.Buffer[i]["Buffer_Voltage"],2)
			xysum=xysum+self.Buffer[i]["Buffer_Voltage"]*self.Buffer[i]["Buffer_pH"]
		self.Const["Slope"]=round((n*xysum-xsum*ysum)/(n*x2sum-xsum*xsum),2)		
		self.Const["Constant"]=round((x2sum*ysum-xsum*xysum)/(x2sum*n-xsum*xsum),2)

	def write_data(self,PSBR):
		PSBR.pHCalib.insert_one(
			        {
			        "ID": self.ReactorID,
			        "Time":self.Time,
			        "Buffer":[
			        {
			        "pH":self.Buffer[0]["Buffer_pH"],
			        "Voltage":self.Buffer[0]["Buffer_Voltage"]
			        },
			        {
			        "pH":self.Buffer[1]["Buffer_pH"],
			        "Voltage":self.Buffer[1]["Buffer_Voltage"]
			        },
			        {
			        "pH":self.Buffer[2]["Buffer_pH"],
			        "Voltage":self.Buffer[2]["Buffer_Voltage"]
			        }],
			        "Slope":self.Const["Slope"],
			        "Constant":self.Const["Constant"]
			        })

	def display_txt(self):
		print " "
		for i in range(4):
			print self.lcd_txt[i]
	
	def conv_txt2str(self,txt):
		l=int(len(txt))
		val=""
		for i in range(l):
			if txt[i]=="*":
				self.txt[i]="."
			val=val+str(txt[i])
		return val

	def calib_page(self,no,val):
		FMT='%Y-%m-%d'
		self.lcd_txt[0]="PSBR "+str(self.ReactorID)+" |Temp="+str(self.Temp)
		self.lcd_txt[1]="Prev Calib "+str(datetime.strptime(self.Time, self.FMT))
		self.lcd_txt[3]="Sample No:"+str(no)+" Val="+str(val)
		self.lcd_txt[2]="m:"+str(self.Const["Slope"])+" c:"+str(self.Const["Constant"])+" Buf.Sol"
		self.display_txt()
		return self.lcd_txt

	def calib_output(self):
		self.lcd_txt[0]="#"+self.ReactorID+"# -1-  -2-  -3-   "
		self.lcd_txt[1]="pH    "+str(self.Buffer[0]["Buffer_pH"])+" "+str(self.Buffer[1]["Buffer_pH"])+" "+str(self.Buffer[2]["Buffer_pH"])
		self.lcd_txt[2]="Val   "+str(self.Buffer[0]["Buffer_Voltage"])+" "+str(self.Buffer[1]["Buffer_Voltage"])+" "+str(self.Buffer[2]["Buffer_Voltage"])
		self.lcd_txt[3]="m="+str(self.Const["Slope"])+" c="+str(self.Const["Constant"])
		self.display_txt()
		return self.lcd_txt

				