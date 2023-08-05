from enum import Enum
import routing_model_pb2
import logging
import string

# Type of the routing model
class RoutingModelType(Enum):
    VRP = 1
    TSP = 2

# The "RoutingEngineType" sets the type of engine
# to be used to solve a routing model of
# type "RoutingModelType".
# For example, a VRP model can be solved by an
# engine implementing "ACTOR_POLICY_VRP", i.e., using
# an actor executing a policy learned with
# Reinforcement Learning.
# @note not all combinations of model types and engine
# types are valid combinations
class RoutingEngineType(Enum):
    ACTOR_POLICY_VRP = 1

class RoutingModel:
    """OptiLab Routing model solved by back-end optimizers"""

    model_type = None
    engine_type = None
    model_name = ""

    def __init__(self, name, model_type):
        """Generates a new routing model"""
        if not name.strip():
            errMsg = "RoutingModel - empty model name"
            logging.error(errMsg)
            raise Exception(errMsg)
        self.model_name = name
        self.distance_matrix = []
        self.distance_matrix_rows = -1
        self.distance_matrix_cols = -1
        self.distance_matrix_mult = 1

        if not isinstance(model_type, RoutingModelType):
            errMsg = "RoutingModel - invalid model type " + type(model_type)
            logging.error(errMsg)
            raise Exception(errMsg)
        self.model_type = model_type

    def SetEngineType(self, engine_type):
        if not isinstance(model_type, RoutingEngineType):
            errMsg = "RoutingModel - SetEngineType: invalid engine type " + type(engine_type)
            logging.error(errMsg)
            raise Exception(errMsg)
        self.engine_type = engine_type

    def Name(self):
        return self.model_name

    def SetDistanceMatrix(self, dist_matrix, mult_data = 1):
        self.distance_matrix = dist_matrix
        self.distance_matrix_mult = mult_data
        rows = len(self.distance_matrix)

        # Check distance matrix:
        # must be a non-empty, square matrix
        if rows == 0:
            errMsg = "RoutingModel - SetDistanceMatrix: invalid matrix (empty)"
            logging.error(errMsg)
            raise Exception(errMsg)
        for idx in range(len(self.distance_matrix)):
            if len(self.distance_matrix[idx]) != rows:
                errMsg = "RoutingModel - SetDistanceMatrix: invalid matrix size " + str(len(self.distance_matrix[idx]))
                logging.error(errMsg)
                raise Exception(errMsg)

        # Set distance matrix size
        self.distance_matrix_rows = rows
        self.distance_matrix_cols = rows

    def GetDistanceMatrix(self):
        return self.distance_matrix

    def GetDistanceMatrixsRows(self):
        return self.distance_matrix_rows

    def GetDistanceMatrixsCols(self):
        return self.distance_matrix_cols

    def Serialize(self):
        """Serialization method: to be overriden by derived classes"""
        return self.toProtobuf().SerializeToString()

    def toProtobuf(self):
        """To protocol buffer method: to be overriden by derived classes"""
        raise Exception("RoutingModel - toProtobuf")

        optimizerModel = optimizer_model_pb2.OptimizerModel()
        if self.MPModel is not None:
            optimizerModel.linear_model.CopyFrom(self.MPModel.toProtobuf())
        elif self.MPModel_file_path.strip():
            optimizerModel.linear_model = linear_model_pb2.LinearModelSpecProto()
            optimizerModel.linear_model.model_path = self.MPModel_file_path
        else:
            errMsg = "OptimizerMPModel - Serialize: model not set"
            logging.error(errMsg)
            raise Exception(errMsg)

        # Set model name
        optimizerModel.linear_model.model_id = self.model_name

        # Set model and package type
        if self.model_type is OptimizerModelType.MIP:
            optimizerModel.linear_model.class_type = linear_model_pb2.LinearModelSpecProto.MIP
        elif self.class_type is OptimizerModelType.LP:
            optimizerModel.linear_model.class_type = linear_model_pb2.LinearModelSpecProto.LP
        elif self.class_type is OptimizerModelType.IP:
            optimizerModel.linear_model.class_type = linear_model_pb2.LinearModelSpecProto.IP
        else:
            errMsg = "OptimizerMPModel - Serialize: invalid model class type"
            logging.error(errMsg)
            raise Exception(errMsg)

        if self.package_type is OptimizerPackageType.SCIP:
            optimizerModel.linear_model.package_type = linear_model_pb2.LinearModelSpecProto.SCIP
        elif self.package_type is OptimizerPackageType.GLOP:
            optimizerModel.linear_model.package_type = linear_model_pb2.LinearModelSpecProto.OR_TOOLS_GLOP
        elif self.package_type is OptimizerPackageType.CLP:
            optimizerModel.linear_model.package_type = linear_model_pb2.LinearModelSpecProto.OR_TOOLS_CLP
        elif self.package_type is OptimizerPackageType.GLPK:
            optimizerModel.linear_model.package_type = linear_model_pb2.LinearModelSpecProto.OR_TOOLS_GLPK
        elif self.package_type is OptimizerPackageType.CBC:
            optimizerModel.linear_model.package_type = linear_model_pb2.LinearModelSpecProto.OR_TOOLS_CBC
        elif self.package_type is OptimizerPackageType.BOP:
            optimizerModel.linear_model.package_type = linear_model_pb2.LinearModelSpecProto.OR_TOOLS_BOP
        else:
            errMsg = "OptimizerMPModel - Serialize: invalid package type"
            logging.error(errMsg)
            raise Exception(errMsg)

        # Serialize the string
        return optimizerModel
