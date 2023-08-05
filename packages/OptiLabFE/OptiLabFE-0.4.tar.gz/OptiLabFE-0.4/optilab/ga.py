import json
from optilab.module import Module


class GA(Module):

    framework="EC"
    classType="GA"
    package = "OPEN-GA"
    objectivesList=[]

    def add_constraint(self, c_id, lb, ub, coefficientsList):
        self.constraintList.append(
            {
                "id":c_id,
                "lb":lb,
                "ub":ub,
                "coefficientsList":coefficientsList
            }
        )

    def add_objective(self, optimizationDirection, coefficientsList):
        self.objectivesList.append(
            {
                "optimizationDirection":optimizationDirection,
                "coefficientsList":coefficientsList
            }
        )

    def load_result(self, json_string):
        data = json.loads(json_string)

        print("Model: " + data['modelId'])
        print("Status: " + data['modelStatus'])
        sol = data['solutionList']
        for x in sol:
            obj = x['objectiveValueList']
            print("Objective: " + str(obj[0]))
            print("Variables: ")
            var = x['solutionAssignmentList']
            print(var['id'] + ":")
            for v in var['dom']:
                print (v)

    def load_from_json(self, jsonfile):
        data = json.load(open(jsonfile))

        self.framework = data['framework']
        self.classType = data['classType']
        self.package = data['package']
        self.model = data['model']
        self.gaParameters = data['gaParameters']
        self.gaEnvironmentList = data['gaEnvironmentList']
        self.gaEnvironmentObjects = data['gaEnvironmentObjects']
        try:
            self.constraintsList = data['constraintsList']
            self.objectivesList = data['objectivesList']
        except:
            self.constraintsList = []
            self.objectivesList = []
