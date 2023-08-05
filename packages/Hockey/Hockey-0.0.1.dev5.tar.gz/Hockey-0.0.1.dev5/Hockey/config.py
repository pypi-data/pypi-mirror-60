import os
import json

class config():
	def __init__(self,name):
		self.configfile=os.environ['HOME']+"/."+name
		self.status= os.path.isfile(self.configfile)
	
	def readConf(self):
		with open(self.configfile) as f:
			return json.load(f)

	def write(self,data):
		with open(self.configfile,"w") as f:
			json.dump(data, f, ensure_ascii=False)
		return 0	


if (__name__=="__main__"):
	el=config("hockey")
#	a={}
#	a['config']='name'
#	a['test']="test"
#	el.write(a)
	m=el.readConf()
	print(m)
