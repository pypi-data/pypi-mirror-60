from . import OptimizerMPModel
from .OptimizerMPModel import OptimizerModelType, OptimizerPackageType

def Infinity():
    return OptimizerMPModel.infinity()

def MPModel(model_name, model_type=OptimizerMPModel.OptimizerModelType.UNDEF):
    """Builds and returns a new instance of a Mathematical Programming (MP)
    model. The caller can specify the type of model (e.g., LP, MIP) which is,
    otherwise, inferred from the model itself.
    By default, the model type is undefined.
    """
    if not isinstance(model_type, OptimizerMPModel.OptimizerModelType):
        errMsg = "MPModel - invalid model type " + type(model_type)
        logging.error(errMsg)
        raise Exception(errMsg)
    mdl = OptimizerMPModel.OptimizerMPModel(model_name)
    mdl.SetModelType(OptimizerMPModel.OptimizerModelType.MIP)
    return mdl
