class Module():

    package = "OR-TOOLS"
    model = "simple_model"
    variablesList = []
    constraintsList = []
    name = None
    left = None
    right = None
    combor = None
    comband = None

    def __init__(self, name):
        self.name = name

    def add_variable(self, var_id, dims, lb, ub, var_type):
        self.variablesList.append(
            {
                "id":var_id,
                "dims":dims,
                "lb":lb,
                "ub":ub,
                "type":var_type
            }
        )

    def __lt__(self, other):
        #self.left = other
        other.left = self
        return self

    def __gt__(self, other):
        self.right = other
        #other.left = self
        return other

    def __and__(self, other):
        self.comband = other
        other.comband = self
        return other

    def __or__(self,other):
        self.combor = other
        other.combor = self
        return other

    # def get_json(self):
    #     return self.__dict__

    def get_json(self):
        return self.data
