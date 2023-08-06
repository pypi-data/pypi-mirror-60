from enum import Enum
from .import linear_model_pb2
import logging
from . import OptConstraint
from . import optilab_pb2
from . import optimizer_model_pb2
from . import OptMPModel
from . import OptVariable
from . import ParallelModel
import string
import sys

from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.relational import GreaterThan, StrictGreaterThan, LessThan, StrictLessThan

class OptimizerModelType(Enum):
    MIP = 1
    LP = 2
    IP = 3
    UNDEF = 4

class OptimizerPackageType(Enum):
    GLOP = 1
    CLP = 2
    CBC = 3
    SCIP = 4
    GLPK = 5

def infinity():
    return sys.float_info.max

class OptimizerMPModel(ParallelModel.ParallelModel):
    """OptiLab Mathematical Programming (MP) model
    solved by back-end optimizers"""

    variable_limit = 100
    constraint_limit = 100
    MPModel = None
    MPModel_file_path = ""
    model_type = None
    package_type = None
    model_name = ""
    model_status = None

    # Model type:
    # - 0b00: default
    # - 0b10: LP (all linear variables)
    # - 0b01: IP (all integer variables)
    # - 0b11: MIP (LP + IP)
    model_user_type = 0b00

    def __init__(self, name=""):
        super().__init__(name)
        """Generates a new model
        If the name is provided, creates a new OptiLab model.
        Otherwise creates an empty model instance and the caller must use
        BuildModel(...) or LoadFromFile(...) to build or load resp. a model.
        """
        self.model_name = name
        if name.strip():
            self.MPModel = OptMPModel.OptMPModel(name)

    def OnMessageImpl(self, optilab_reply_message):
        if optilab_reply_message.details.Is(optilab_pb2.OptimizerSolutionRep.DESCRIPTOR):
            # JSON solutions are printed verbatim on the screen
            solMsg = optilab_pb2.OptimizerSolutionRep()
            optilab_reply_message.details.Unpack(solMsg)
            print(solMsg.solution)
        elif optilab_reply_message.details.Is(linear_model_pb2.LinearModelSolutionProto.DESCRIPTOR):
            # Capture the protobuf solution
            solProto = linear_model_pb2.LinearModelSolutionProto()
            optilab_reply_message.details.Unpack(solProto)
            self.UploadProtoSolution(solProto)

    def GetModelStatus(self):
        return self.StatusToString(self.model_status)

    def GetObjectiveValue(self):
        return self.MPModel.getObjectiveValue()

    def StatusToString(self, status):
        if status is None:
            return "SOLVER_UNKNOWN_STATUS"
        else:
            return linear_model_pb2.LinearModelSolutionStatusProto.Name(status)

    def UploadProtoSolution(self, linear_model_solution_proto):
        # Set the model's status
        self.model_status = linear_model_solution_proto.status

        # Set the objective value
        self.MPModel.setObjectiveValue(linear_model_solution_proto.objective_value)

        # Set variable values
        if self.model_status == linear_model_pb2.LinearModelSolutionStatusProto.Value('SOLVER_FEASIBLE') or \
        self.model_status == linear_model_pb2.LinearModelSolutionStatusProto.Value('SOLVER_OPTIMAL'):
            for proto_var in linear_model_solution_proto.variable_assign:
                var = self.MPModel.getVariableFromName(proto_var.var_name)
                var.setSolutionValue(proto_var.var_value[0])

        # Notify the user about model upload
        print("MIPModel - solution uploaded")

    def SetModelType(self, model_type):
        """Forces the model to be of a specific type"""
        if not isinstance(model_type, OptimizerModelType):
            errMsg = "OptimizerMPModel - SetModelType: invalid model type " + type(model_type)
            logging.error(errMsg)
            raise Exception(errMsg)
        self.model_type = model_type
        if model_type == OptimizerModelType.MIP:
            self.model_user_type = 0b11
        elif model_type == OptimizerModelType.IP:
            self.model_user_type = 0b01
        elif model_type == OptimizerModelType.LP:
            self.model_user_type = 0b10
        else:
            self.model_user_type = 0b00

    def GetModelType(self):
        """Returns the type of this model"""
        if self.model_user_type == 0b11:
            return OptimizerModelType.MIP
        elif self.model_user_type == 0b01:
            return OptimizerModelType.IP
        elif self.model_user_type == 0b10:
            return OptimizerModelType.LP
        else:
            return OptimizerModelType.UNDEF

    def SupportedSolvers(self):
        if self.model_user_type == 0b11 or self.model_user_type == 0b01:
            # MIP solvers and IP solvers
            return [OptimizerPackageType.CBC, OptimizerPackageType.SCIP, OptimizerPackageType.GLPK]
        elif self.model_user_type == 0b10:
            # LP solvers
            return [OptimizerPackageType.GLOP, OptimizerPackageType.CLP, OptimizerPackageType.GLPK]
        else:
            raise Exception("OptimizerMPModel - SupportedSolvers: undefined model")

    def SetPackageType(self, package_type):
        if not isinstance(package_type, OptimizerPackageType):
            errMsg = "OptimizerMPModel - SetPackageType: invalid model type " + type(package_type)
            logging.error(errMsg)
            raise Exception(errMsg)
        self.package_type = package_type

    def BuildModel(self, name):
        if not name.strip():
            errMsg = "OptimizerMPModel - BuildNewModel: empty model name"
            logging.error(errMsg)
            raise Exception(errMsg)
        self.MPModel_file_path = None
        self.MPModel = OptMPModel.OptMPModel(name)

    def LoadModelFromFile(self, file_path, name):
        if not name.strip():
            errMsg = "OptimizerMPModel - LoadFromFile: empty model name"
            logging.error(errMsg)
            raise Exception(errMsg)
        self.MPModel = None
        self.MPModel_file_path = file_path

    def Clear(self):
        """Clears the model"""
        self.MPModel.clear()

    def BoolVar(self, name=""):
        """Creates, adds to the model, and returns a Boolean variable"""
        if len(self.MPModel.variable_list) >= self.variable_limit:
            raise(OverflowError("maximum variable limit exceeded"))
        var = OptVariable.OptVariable(0.0, 1.0, True, name)
        self.MPModel.addVariable(var)
        self.model_user_type = self.model_user_type | 0b01
        return var

    def IntVar(self, lower_bound, upper_bound, name=""):
        """Creates, adds to the model, and returns an Integer variable"""
        if len(self.MPModel.variable_list) >= self.variable_limit:
            raise(OverflowError("maximum variable limit exceeded"))
        var = OptVariable.OptVariable(lower_bound, upper_bound, True, name)
        var = OptVariable.OptVariable(lower_bound, upper_bound, True, name)
        self.MPModel.addVariable(var)
        self.model_user_type = self.model_user_type | 0b01
        return var

    def NumVar(self, lower_bound, upper_bound, name=""):
        """Creates, adds to the model, and returns a numeric continuous variable"""
        if len(self.MPModel.variable_list) >= self.variable_limit:
            raise(OverflowError("maximum variable limit exceeded"))
        var = OptVariable.OptVariable(lower_bound, upper_bound, False, name)
        self.MPModel.addVariable(var)
        self.model_user_type = self.model_user_type | 0b10
        return var

    def Constraint(self, *args, **kwargs):
        """Creates, adds to the model, and returns a constraint
        specified either as an expression, or as follows:
        lower_bound <= varList * coeffList <= upper_bound
        """
        name = kwargs["name"] if "name" in kwargs else ""
        if len(args) == 1:
            # PASSED expr
            expr = args[0]

            # TODO: switch sympy dependency to parser library, to allow
            # for bidirectional inequalities.
            if len(self.MPModel.constraint_list) >= self.constraint_limit:
                raise(OverflowError("maximum constraint limit exceeded"))
            if isinstance(expr, (GreaterThan, StrictGreaterThan)):
                var_expr, bound = expr.args
                con = OptConstraint.OptConstraint(bound, infinity(), name)
            elif isinstance(expr, (LessThan, StrictLessThan)):
                var_expr, bound = expr.args
                con = OptConstraint.OptConstraint(-infinity(), bound, name)
            else:
                raise ValueError("expression must be an inequality")
            for term in var_expr.args:
                if isinstance(term, OptVariable.OptVariable):
                    con.addScopeVariable(term, 1)
                else:
                    coeff, var = term.args
                    con.addScopeVariable(var, coeff)

            self.MPModel.addConstraint(con)
            return con
        elif len(args) <= 4:
            # PASSED var_list AND coeff_list

            # validate argument types and parse from args/kwargs
            var_list, coeff_list = args[0], args[1]
            if len(args) == 2:
                lower_bound = kwargs["lower_bound"] if "lower_bound" in kwargs else -infinity()
                upper_bound = kwargs["upper_bound"] if "upper_bound" in kwargs else infinity()
            elif len(args) == 4:
                lower_bound = args[2]
                upper_bound = args[3]
                if "lower_bound" in kwargs:
                    raise TypeError("Constraint() got multiple values for argument 'lower_bound'")
                elif "upper_bound" in kwargs:
                    raise TypeError("Constraint() got multiple values for argument 'upper_bound'")
            else:
                raise TypeError("Constraint() requires both 'lower_bound' and 'upper_bound' when specified as positional arguments")

            # add constraint
            con = OptConstraint.OptConstraint(lower_bound, upper_bound, name)
            if len(var_list) != len(coeff_list):
                err_msg = "OptimizerMPModel - Constraint: variable and coefficient lists lengths not matching"
                logging.error(err_msg)
                raise Exception(err_msg)
            for idx in range(0, len(var_list)):
                if not isinstance(var_list[idx], OptVariable.OptVariable):
                    err_msg = "OptimizerMPModel - Constraint: invalid type (expected variable) " + type(var_list[idx])
                    logging.error(err_msg)
                    raise Exception(err_msg)
                con.addScopeVariable(var_list[idx], coeff_list[idx])
            self.MPModel.addConstraint(con)
            return con
        else:
            raise TypeError("Constraint() received too many positional arguments")

    def Objective(self, *args, maximize = False):
        """Specifies the objective function either as an expression, or as:
        [maximize | minimize] varList * coeffList
        """
        if len(args) == 1:
            # PASSED expr
            expr = args[0]

            if isinstance(expr, Add):
                for term in expr.args:
                    if isinstance(term, OptVariable.OptVariable):
                        term.setObjectiveCoefficient(1)
                    else:
                        coeff, var = term.args
                        var.setObjectiveCoefficient(coeff)
            elif isinstance(expr, Mul):
                coeff, var = term.args
                var.setObjectiveCoefficient(coeff)
            elif isinstance(expr, OptVariable.OptVariable):
                expr.setObjectiveCoefficient(1)
            else:
                raise ValueError("expression must be an inequality")
            self.MPModel.setObjectiveDirection(maximize)
        elif len(args) == 2:
            # PASSED var_list AND coeff_list
            var_list, coeff_list = args
            if len(var_list) != len(coeff_list):
                err_msg = "OptimizerMPModel - Objective: variable and coefficient lists lengths not matching"
                logging.error(errMsg)
                raise Exception(errMsg)
            for idx in range(0, len(var_list)):
                if not isinstance(var_list[idx], OptVariable.OptVariable):
                    err_msg = "OptimizerMPModel - Objective: invalid type (expected variable) " + type(var_list[idx])
                    logging.error(err_msg)
                    raise Exception(err_msg)
                var_list[idx].setObjectiveCoefficient(coeff_list[idx])
            self.MPModel.setObjectiveDirection(maximize)
        else:
            raise TypeError("Constraint() received too many positional arguments")

    def Maximize(self, *args):
        self.Objective(*args, maximize = True)

    def Minimize(self, *args):
        self.Objective(*args, maximize = False)

    def Serialize(self):
        return self.toProtobuf().SerializeToString()

    def toProtobuf(self):
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
        m_type = self.GetModelType()
        if m_type is OptimizerModelType.MIP:
            optimizerModel.linear_model.class_type = linear_model_pb2.LinearModelSpecProto.MIP
        elif m_type is OptimizerModelType.LP:
            optimizerModel.linear_model.class_type = linear_model_pb2.LinearModelSpecProto.LP
        elif m_type is OptimizerModelType.IP:
            optimizerModel.linear_model.class_type = linear_model_pb2.LinearModelSpecProto.IP
        else:
            errMsg = "OptimizerMPModel - Serialize: invalid model type"
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
        else:
            errMsg = "OptimizerMPModel - Serialize: invalid package type"
            logging.error(errMsg)
            raise Exception(errMsg)

        # Serialize the string
        return optimizerModel
