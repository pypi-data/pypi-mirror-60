import json
from optilab.module import Module


class MIP(Module):

    framework = "OR"
    classType = "MIP"
    modelDescriptor = ""
    model_format = ""
    model_data = ""
    use_file_descriptors = True
    model_descriptor = []

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
        json_string = json_string.split(",\nmetrics")[0] + "}"
        data = json.loads(json_string)

        print("Model: " + data['modelId'])
        print("Status: " + data['modelStatus'])
        obj = data['objectiveValuesList']
        for x in obj:
            print("Objective: " + str(x))
        print("Variables: ")
        vars = data['solutionList']
        for x in vars:
            print(x['id'] + ": " + str(x['dom'][0]))

    def load_from_json(self, jsonfile):
        data = json.load(open(jsonfile))

        self.classType = "MIP"
        self.framework = data['framework']
        self.package = data['package']
        self.model = data['model']
        self.model_format = data['model_format']
        self.model_data = ""
        self.use_file_descriptors = data['use_file_descriptors']
        if self.use_file_descriptors:
            self.model_descriptor = data['model_descriptor']
        try:
            self.variablesList = data['variablesList']
            self.constraintsList = data['constraintsList']
            self.objectivesList = data['objectivesList']
        except:
            self.variablesList = []
            self.constraintsList = []
            self.objectivesList = []

    def get_json(self):
        return self.__dict__
