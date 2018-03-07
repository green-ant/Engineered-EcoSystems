#  ______       _________     _______     _______   _____     __
# /\  ____\    / \   __  \   /\  ____\   /\  ____\  \ \  \ _  \ \
# \ \ \    ___ \  \  \ \  \  \ \ \_____  \ \ \_____  \ \   _ \ \ \
#  \ \ \__\  _\ \  \  \\_ \_  \ \  ____\  \ \  ____\  \ \ \ \ \_\ \ 
#   \ \______\   \  \  \ \_ \_ \ \ \_____  \ \ \_____  \ \ \ \   \ \ 
#    \/_______\   \__\__\  \ _\ \/_______\  \/_______\  \/_/   \_ \_\



class Element:
    def __init__(self,ID,item,tm,cmdOn,cmdOff):
        self.ID=ID
        self.current={}
        self.current["status"]="Off"
        self.current["timestamp"]=tm
        self.previous=[]
        self.item=item
        self.cmdOn=cmdOn
        self.cmdOff=cmdOff

    def get_status(self,Reactor):
        cmd=str(self.ID)+":Status\r\n"
        Reactor.write(cmd)
        time.sleep(5)
        data = Reactor.readline()
        data=data.rstrip()
        cntrllr=data.split(':')
        if len(cntrllr) == 2:
            print self.ID+" Status is "+cntrllr[1]
            self.current["status"]=cntrllr[1]
            tm=(datetime.fromtimestamp(time.time())).strftime(FMT)
            self.current["timestamp"]=tm
        
