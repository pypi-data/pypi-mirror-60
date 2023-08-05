import json
from optilab.module import Module


class CP(Module):

    framework = "OR"
    classType = "CP"
    searchList = []
    searchObjects = []

    def add_searchList(self, searchId, searchType, numSolutions):
        self.searchList.append(
            {
                "searchId":searchId,
                "searchType":searchType,
                "numSolutions":numSolutions
            }
        )

    def add_searchObjects(self, obj_id, combinatorType, varSelection, valSelection, branchingList):
        self.searchObjects.append(
            {
                "id":obj_id,
                "combinatorType":combinatorType,
                "varSelection":varSelection,
                "valSelection":valSelection,
                "branchingList":branchingList
            }
        )

    def add_constraint(self, semantic, c_type, name, propagation_type, args_list):
        self.constraintsList.append(
            {
                "semantic":semantic,
                "type":c_type,
                "name":name,
                "propagation_type":propagation_type,
                "args_list":args_list
            }
        )

    def load_result(self, json_string):
        json_string = json_string.split(",\nmetrics")[0] + "}"
        data = json.loads(json_string)

        print("Model: " + data['modelId'])
        print("Number of solutions: " + str(data['numSolutions']))
        print("Status: " + data['modelStatus'])
        print("Variables: ")
        vars = data['solutionList']
        for x in vars:
            for y in x:
                print(y['id'] + ": " + str(y['dom'][0]))

    def load_from_json(self, jsonfile):
        data = json.load(open(jsonfile))

        self.framework = "OR"
        self.classType = "CP"
        self.framework = data['framework']
        self.package = data['package']
        self.model = data['model']
        self.variablesList = data['variablesList']
        self.constraintsList = data['constraintsList']
        self.searchList = data['searchList']
        self.searchObjects = data['searchObjects']

    def get_json(self):
        return self.__dict__
