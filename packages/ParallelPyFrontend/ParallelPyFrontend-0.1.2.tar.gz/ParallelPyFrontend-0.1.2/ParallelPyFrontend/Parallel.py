from . import FrontendClientRunner

kOptiLabSocketPort = 8080

class Parallel():
    address = ""
    port = -1
    client_runner = None
    use_protobuf = True

    def __init__(self, addr, port=kOptiLabSocketPort, use_protobuf=True):
        # Set the address
        self.address = addr

        # Set port if defined, otherwise use standard port 8080
        self.port = port

        # Set use of protobuf as communication protocol
        self.use_protobuf = use_protobuf

    def Connect(self):
        """Connect Parallel front-end interface to the service"""
        self.client_runner = FrontendClientRunner.FrontendClientRunner(
            self.address,
            self.port,
            self.use_protobuf)
        connected = self.client_runner.connectToServer()
        if not connected:
            raise Exception('Cannot connect to the Parallel service.')

    def Disconnect(self):
        """Disconnect Parallel front-end interface from the service"""
        self.client_runner.disconnectFromServer()

    def RunOptimizer(self, model):
        """Sends the given model to the Parallel back-end service.

        Creates back-end optimizers and run the service on the serialized
        model provided by the caller.
        """
        if self.client_runner is None:
            raise Exception('Parallel is not connected to the service, return.')
        self.client_runner.sendMessageToBackendServer(model)
