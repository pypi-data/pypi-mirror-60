from . import linear_model_pb2
from . import OptVariable
import string
import sys

class OptConstraint:
    """OptiLab constraint class"""

    # Constraint's name
    name = ""

    # Constraint counter for creating unique constraint identifiers
    con_counter = 0

    # Flag for lazy constraints
    is_lazy = False

    def __init__(self, lb, ub, name=""):
        # List of variable indices and names of the i-th
        # linear term involved in this constraint
        self.var_index = []
        self.var_name = []

        # List of the coefficient corresponding to the variables in "var_index"
        self.coefficient = []

        if not name.strip():
            # Empty name, assign a default name
            self.name = "_c_" + str(OptConstraint.con_counter)
            OptConstraint.con_counter += 1
        else:
            self.name = name
        self.lower_bound = lb
        self.upper_bound = ub

    def addScopeVariable(self, var, coeff):
        if not isinstance(var, OptVariable.OptVariable):
            errMsg = "OptConstraint - addVariable: invalid type " + type(var)
            logging.error(errMsg)
            raise Exception(errMsg)
        self.var_index.append(var.getVarIndex())
        self.var_name.append(var.getName())
        self.coefficient.append(coeff)

    def getName(self):
        return self.name

    def getLowerBound(self):
        return self.lower_bound

    def getUpperBound(self):
        return self.upper_bound

    def toProtobuf(self):
        protoCon = linear_model_pb2.OptConstraintProto();
        protoCon.lower_bound = self.lower_bound
        protoCon.upper_bound = self.upper_bound
        protoCon.name = self.name
        protoCon.var_index.extend(self.var_index)
        protoCon.coefficient.extend(self.coefficient)
        protoCon.is_lazy = self.is_lazy
        return protoCon

    def toString(self):
        conPP = "con:\n\tid: " + self.name
        conPP += "\n\tbounds: (" + str(self.lower_bound) + ", " + str(self.upper_bound) + ")"
        conPP += "\n\tscope:"
        conPP += "\n\t " + str(self.var_name)
        conPP += "\n\t " + str(self.coefficient)
        return conPP

    def print(self):
        print(self.toString())
