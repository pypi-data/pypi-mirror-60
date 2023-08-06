from . import linear_model_pb2
import logging
from . import OptConstraint
from . import OptVariable
import string
import sys

class OptMPModel():
    """OptiLab mathematical programming model class.

    MP models encapsulates the definition of any
    mathematical programming models including:
    - Linear Programming (LP)
    - Mixed Integer Programming (MIP)
    - Integer Programming (IP)
    """

    # Name of the model
    name = ""

    # Maximization vs minimization problem
    maximize = False

    # Offset on the objective function
    objective_offset = 0.0

    # Objective value set only after solvig the model
    objective_value = sys.float_info.min

    # Variable name to index map
    var_to_idx_map = {}

    def __init__(self, name, maximize=False, objective_offset = 0.0):
        # List of variables in the model
        self.variable_list = []

        # List of constraint in the model
        self.constraint_list = []

        self.name = name
        self.maximize = maximize
        self.objective_offset = objective_offset

    def getModelName(self):
        return self.name

    def clear(self):
        self.variable_list.clear()
        self.constraint_list.clear()

    def setObjectiveValue(self, val):
        self.objective_value = val

    def getObjectiveValue(self):
        return self.objective_value

    def addVariable(self, var):
        if not isinstance(var, OptVariable.OptVariable):
            errMsg = "OptMPModel - addVariable: invalid type " + type(var)
            logging.error(errMsg)
            raise Exception(errMsg)
        var.setVarIndex(len(self.variable_list))
        self.var_to_idx_map[var.getName()] = var.getVarIndex()
        self.variable_list.append(var)

    def removeVariable(self, var):
        if not isinstance(var, OptVariable.OptVariable):
            errMsg = "OptMPModel - removeVariables: invalid type " + type(var)
            logging.error(errMsg)
            raise Exception(errMsg)
        self.var_to_idx_map.remove(var.getName())
        self.variable_list.remove(var)
        idx = 0
        for v in self.variable_list:
            v.setVarIndex(idx)
            idx += 1

    def getVariableFromName(self, var_name):
        return self.variable_list[self.var_to_idx_map[var_name]]

    def getVariable(self, idx):
        return self.variable_list[idx]

    def addConstraint(self, con):
        if not isinstance(con, OptConstraint.OptConstraint):
            errMsg = "OptMPModel - addConstraint: invalid type " + type(con)
            logging.error(errMsg)
            raise Exception(errMsg)
        self.constraint_list.append(con)

    def removeConstraint(self, con):
        if not isinstance(con, OptConstraint.OptConstraint):
            errMsg = "OptMPModel - removeConstraint: invalid type " + type(con)
            logging.error(errMsg)
            raise Exception(errMsg)
        self.constraint_list.remove(con)

    def getConstraint(self, idx):
        return self.constraint_list[idx]

    def setObjectiveDirection(self, maximize):
        self.maximize = maximize

    def isMaximization(self):
        return self.maximize

    def setObjectiveOffset(self, offset):
        self.objective_offset = offset

    def getObjectiveOffset(self):
        return self.objective_offset

    def toString(self):
        modelPP = "model:\n\tid: " + self.name + "\n"
        modelPP += "\tmaximize: " + str(self.maximize) + "\n"
        modelPP += "\tnum. variables: " + str(len(self.variable_list)) + "\n"
        modelPP += "\tnum. constraint: " + str(len(self.constraint_list)) + "\n"
        return modelPP

    def toProtobuf(self):
        protoModelSpec = linear_model_pb2.LinearModelSpecProto();
        protoModel = protoModelSpec.model

        # Set model parameters
        protoModel.maximize = self.maximize
        protoModel.objective_offset = self.objective_offset
        protoModel.name = self.name

        # Add variables into the model
        for var in self.variable_list:
            protoVar = protoModel.variable.add()
            protoVar.CopyFrom(var.toProtobuf())

        for con in self.constraint_list:
            protoCon = protoModel.constraint.add()
            protoCon.CopyFrom(con.toProtobuf())

        return protoModelSpec
