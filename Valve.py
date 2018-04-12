class Valve:
	def __init__(self,ID,dur_on,tm):
		self.ID=ID
		self.dur_on=dur_on
		self.current={}
		self.current["status"]="Off"
		self.current["timestamp"]=tm
		self.previous=[]
		self.item="Valve"