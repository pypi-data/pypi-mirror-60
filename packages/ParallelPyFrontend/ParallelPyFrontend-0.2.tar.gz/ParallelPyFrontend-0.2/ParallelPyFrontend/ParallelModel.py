from . import optilab_pb2

class ParallelModel:
    def __init__(self, fname):
        self.name = fname

    def GetName(self):
        return self.name

    def OnMessage(self, proto_message):
        repMsg = optilab_pb2.OptiLabReplyMessage()
        repMsg.ParseFromString(proto_message);
        msgType = repMsg.type
        if msgType == optilab_pb2.OptiLabReplyMessage.Metrics:
            metMsg = optilab_pb2.OptimizerMetricsRep()
            if repMsg.details.Is(optilab_pb2.OptimizerMetricsRep.DESCRIPTOR):
                repMsg.details.Unpack(metMsg)
            else:
                logging.error("ParallelModel - OnMessage: invalid metrics type message")
                print("Error on receiving metrics from the back-end")
            print(metMsg.metrics)
        elif msgType == optilab_pb2.OptiLabReplyMessage.Metadata:
            mtdMsg = optilab_pb2.OptimizerMetadataRep()
            if repMsg.details.Is(optilab_pb2.OptimizerMetadataRep.DESCRIPTOR):
                repMsg.details.Unpack(mtdMsg)
            else:
                logging.error("ParallelModel - OnMessage: invalid metadata type message")
                print("Error on receiving meta-data from the back-end")
            print(mtdMsg.metadata)
        elif msgType == optilab_pb2.OptiLabReplyMessage.Solution:
            self.OnMessageImpl(repMsg)
        else:
            logging.error("ParallelModel - OnMessage: received invalid message type")
            print("Unrecognized message type received from the back-end")

    def OnMessageImpl(self, optilab_reply_message):
        raise Exception("ParallelModel - OnMessage: requires implementation")
