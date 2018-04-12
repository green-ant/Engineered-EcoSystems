#  ______       _________     _______     _______   _____     __
# /\  ____\    / \   __  \   /\  ____\   /\  ____\  \ \  \ _  \ \
# \ \ \    ___ \  \  \ \  \  \ \ \_____  \ \ \_____  \ \   _ \ \ \
#  \ \ \__\  _\ \  \  \\_ \_  \ \  ____\  \ \  ____\  \ \ \ \ \_\ \ 
#   \ \______\   \  \  \ \_ \_ \ \ \_____  \ \ \_____  \ \ \ \   \ \ 
#    \/_______\   \__\__\  \ _\ \/_______\  \/_______\  \/_/   \_ \_\


class Element:
    def __init__(self,ID,item,tm):
        self.ID=ID
        self.current={}
        self.current["status"]="Off"
        self.current["timestamp"]=tm
        self.previous=[]
        self.item=item

        
