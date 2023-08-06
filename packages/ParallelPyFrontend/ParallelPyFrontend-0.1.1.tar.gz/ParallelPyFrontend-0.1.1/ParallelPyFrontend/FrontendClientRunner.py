import logging
import ssl
import threading
try:
    import thread
except ImportError:
    import _thread as thread
import time
from threading import Thread, Lock, Condition
import websocket

kDefaultWebSocketPort = 8080
kCondition = Condition()
kQueue = []
kCurrentModel = None

def on_message(ws, message):
    global kCurrentModel
    if kCurrentModel is None:
        msg = "The model is not set, return"
        logging.info(msg)
        print(msg)
        return
    kCurrentModel.OnMessage(message)
    #global kQueue
    #print(message)
    #kCondition.acquire()
    #kQueue.append(message)
    #kCondition.notify()
    #kCondition.release()

def on_error(ws, error):
    logging.error(error)
    print(error)

def on_close(ws):
    msg = "### Connection closed ###"
    logging.info(msg)

def on_open(ws):
    msg = "Client connected to back-end server"
    logging.info(msg)
    print(msg)

class FrontendClientRunner():
    address = "";
    port = 0;
    websocket = None;
    wsURL = "";

    def __init__(self, addr, port=kDefaultWebSocketPort, use_protobuf=True):
        # websocket.enableTrace(True)

        # Set port if defined, otherwise use standard port 8080
        self.port = port

        # Set the address
        self.address = addr

        # Prepare the full address
        if use_protobuf:
            self.wsURL = "ws://" + self.address + ":" + str(self.port) + "/proto_service"
        else:
            self.wsURL = "ws://" + self.address + ":" + str(self.port) + "/optilab_service"

    def connectToServerImpl(self, wbsocket):
        # , sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY),)
        wbsocket.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})

    def connectToServer(self):
        # websocket.enableTrace(True)
        logging.info("Connecting to back-end server...")
        # print(self.wsURL)
        header = {
            'Sec-WebSocket-Protocol': 'graphql-subscriptions'
        }
        try:
            self.websocket = websocket.WebSocketApp(self.wsURL,
                header = header,
                on_message = on_message,
                on_error = on_error,
                on_close = on_close)
            self.websocket.on_open = on_open
            # self.websocket.run_forever()
            th = threading.Thread(target=self.connectToServerImpl, args=(self.websocket, ), daemon=True)
            th.start()
        except:
            errMsg = "Cannot connect to the back-end server, return"
            logging.error(errMsg)
            return False;
        return True;

    def disconnectFromServer(self):
        # Initiate closing protocol with server
        self.websocket.sock.send("__CLIENT_LOG_OFF__");

        # Wait to logoff from server
        time.sleep(1)
        try:
            self.websocket.sock.close()
        except:
            logging.info("Connection close and exception threw")
        finally:
            msg = "### Connection closed ###"
            print(msg)
        # self.websocket.sock.close()

    def sendMessageToBackendServer(self, model):
        if self.websocket is None:
            logging.error("Client not connected to back-end server, return")
            return
        # Set the current global model and send the request to the back-end
        global kCurrentModel
        kCurrentModel = model
        self.websocket.sock.send_binary(model.Serialize())

    def getMessageFromBackendServer(self):
        global kQueue
        kCondition.acquire()
        if not kQueue:
            kCondition.wait()
        msg = kQueue.pop(0)
        kCondition.notify()
        kCondition.release()
        return msg
