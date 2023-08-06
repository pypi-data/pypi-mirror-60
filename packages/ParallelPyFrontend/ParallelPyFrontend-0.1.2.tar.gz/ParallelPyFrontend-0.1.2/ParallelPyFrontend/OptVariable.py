from . import linear_model_pb2
from . import OptObject
import string
import sys
from sympy import Symbol

class OptVariable(Symbol):
    """OptiLab variable class"""

    name = ""
    branching_priority = 0
    lower_bound = -sys.float_info.max
    upper_bound = sys.float_info.max
    is_integer = False
    solution_value = -sys.float_info.max
    reduced_cost = -sys.float_info.max
    var_counter = 0
    objective_coefficient = 0.0
    var_index = -1

    def __new__(cls, lb, ub, is_integer, name=""):
        """ defined because sympy.Symbol defines __new__ """
        if not name.strip():
            # Empty name, assign a default name
            name = "_v_" + str(OptVariable.var_counter)
            OptVariable.var_counter += 1
        return Symbol.__new__(cls, name)

    def __init__(self, lb, ub, is_integer, name=""):
        # don't do anything with name b/c it was taken care of in __new__
        self.lower_bound = lb
        self.upper_bound = ub
        self.is_integer = is_integer
        self.objective_coefficient = 0.0

    def setObjectiveCoefficient(self, val):
        self.objective_coefficient = val

    def getObjectiveCoefficient(self):
        return self.objective_coefficient

    def setVarIndex(self, idx):
        self.var_index = idx

    def getVarIndex(self):
        return self.var_index

    def getName(self):
        return self.name

    def getLowerBound(self):
        return self.lower_bound

    def getUpperBound(self):
        return self.upper_bound

    def isInteger(self):
        return self.is_integer

    def setBranchingPriority(self, bprior):
        self.branching_priority = bprior

    def getBranchingPriority(self):
        return self.branching_priority

    def getSolutionValue(self):
        if self.solution_value < self.lower_bound or self.solution_value > self.upper_bound:
            return "N/A"
        return self.solution_value

    def setSolutionValue(self, val):
        self.solution_value = val

    def lockSolutionValue(self):
        self.lower_bound = self.solution_value
        self.upper_bound = self.solution_value

    def getReducedCost(self):
        return self.reduced_cost

    def setReducedCost(self, val):
        self.reduced_cost = val

    def toProtobuf(self):
        protoVar = linear_model_pb2.OptVariableProto();
        protoVar.lower_bound = self.lower_bound
        protoVar.upper_bound = self.upper_bound
        protoVar.is_integer = self.is_integer
        protoVar.name = self.name
        protoVar.branching_priority = self.branching_priority
        protoVar.objective_coefficient = self.objective_coefficient
        return protoVar

    def toString(self):
        varPP = "var:\n\tid: " + self.name
        varPP += "\n\tsolution value: " + str(self.getSolutionValue())
        varPP += "\n\tis integer: " + str(self.is_integer)
        if self.is_integer:
            varPP += "\n\tdomain: [" + str(self.lower_bound) + ", " + str(self.upper_bound) + "]"
        else:
            varPP += "\n\tdomain: (" + str(self.lower_bound) + ", " + str(self.upper_bound) + ")"
        varPP += "\n\tbranching priority: " + str(self.branching_priority)
        if self.objective_coefficient != 0.0:
            varPP += "\n\tobjective coefficient: " + str(self.objective_coefficient)
        return varPP

    def print(self):
        print(self.toString())
