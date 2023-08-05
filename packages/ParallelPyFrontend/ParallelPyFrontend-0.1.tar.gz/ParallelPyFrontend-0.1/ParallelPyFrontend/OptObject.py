class OptObject:
    """OptiLab base class for any MP model object"""

    # Constraint's name
    name = ""

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

    def toProtobuf(self):
        raise Exception("OptObject - toProtobuf: not implemented")

    def toString(self):
        raise Exception("OptObject - toString: not implemented")

    def print(self):
        print(self.toString())
