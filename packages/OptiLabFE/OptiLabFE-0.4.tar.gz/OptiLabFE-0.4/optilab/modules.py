import json

class modules():
	package="OR-TOOLS"
	model="simple_model"
	variablesList=[]
	constraintsList=[]
	name=None
	left=None
	right=None
	combor=None
	comband=None
	def __init__(self,name):
		self.name = name

	def add_variable(self,id,dims,lb,ub,type):
		self.variablesList.append(
			{
				"id":id,
				"dims":dims,
				"lb":lb,
				"ub":ub,
				"type":type
			}
			)

	def __lt__(self,other):
		#self.left=other
		other.left = self
		return self

	def __gt__(self,other):
		self.right=other
		#other.left = self
		return other

	def __and__(self,other):
		self.comband=other
		other.comband = self
		return other

	def __or__(self,other):
		self.combor=other
		other.combor=self
		return other

	def get_json(self):
		return self.__dict__


