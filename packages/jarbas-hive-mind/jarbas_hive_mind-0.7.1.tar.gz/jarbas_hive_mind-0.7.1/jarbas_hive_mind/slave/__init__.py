import json
from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

from jarbas_utils.log import LOG
from jarbas_utils.messagebus import Message, get_mycroft_bus
from jarbas_hive_mind.exceptions import UnauthorizedKeyError
from jarbas_hive_mind.utils import decrypt_from_json, encrypt_as_json, \
    serialize_message


platform = "HiveMindSlaveV0.2"


class HiveMindSlaveProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        LOG.info("HiveMind connected: {0}".format(response.peer))
        self.factory.bus.emit(Message("hive.mind.connected",
                                      {"server_id": response.headers[
                                              "server"]}))
        self.factory.client = self
        self.factory.status = "connected"

    def onOpen(self):
        LOG.info("HiveMind WebSocket connection open. ")
        self.factory.bus.emit(Message("hive.mind.websocket.open"))

    def onMessage(self, payload, isBinary):
        LOG.info("status: " + self.factory.status)
        if not isBinary:
            payload = self.decode(payload)
            data = {"payload": payload, "isBinary": isBinary}
        else:
            data = {"payload": None, "isBinary": isBinary}
        self.factory.bus.emit(Message("hive.mind.message.received",
                                      data))

    def decode(self, payload):
        payload = payload.decode("utf-8")
        if self.factory.crypto_key:
            LOG.debug("Decrypting message with key: {key}".format(
                key=self.factory.crypto_key))
            payload = decrypt_from_json(self.factory.crypto_key, payload)
        msg = json.loads(payload)
        return msg

    def onClose(self, wasClean, code, reason):
        if "WebSocket connection upgrade failed" in reason:
            # key rejected
            LOG.error("Key rejected")
        LOG.warning("HiveMind WebSocket connection closed: {0}".format(reason))
        self.factory.bus.emit(Message("hive.mind.connection.closed",
                                      {"wasClean": wasClean,
                                       "reason": reason,
                                       "code": code}))
        self.factory.client = None
        self.factory.status = "disconnected"
        if "WebSocket connection upgrade failed" in reason:
            # key rejected
            LOG.error("Key rejected")
            raise UnauthorizedKeyError

    def sendMessage(self,
                    payload,
                    isBinary=False,
                    fragmentSize=None,
                    sync=False,
                    doNotCompress=False):
        if self.factory.crypto_key and not isBinary:
            LOG.debug("Encrypting message with key: {key}".format(
                key=self.factory.crypto_key))
            payload = encrypt_as_json(self.factory.crypto_key,
                                      bytes(payload, encoding="utf-8"))
        if isinstance(payload, str):
            payload = bytes(payload, encoding="utf-8")
        super().sendMessage(payload, isBinary, fragmentSize=fragmentSize,
                            sync=sync, doNotCompress=doNotCompress)


class HiveMindSlave(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = HiveMindSlaveProtocol

    def __init__(self, bus=None, crypto_key=None, *args, **kwargs):
        super(HiveMindSlave, self).__init__(*args, **kwargs)
        self.client = None
        self.status = "disconnected"
        self.crypto_key = crypto_key
        # mycroft_ws
        self.bus = bus or get_mycroft_bus()
        self.register_mycroft_messages()

    # initialize methods
    def register_mycroft_messages(self):
        self.bus.on("hive.mind.message.received",
                    self.handle_incoming_message)
        self.bus.on("hive.mind.message.send",
                    self.handle_outgoing_message)

    def shutdown(self):
        self.bus.remove("hive.mind.message.received",
                        self.handle_incoming_message)
        self.bus.remove("hive.mind.message.send",
                        self.handle_outgoing_message)

    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        LOG.error(
            "HiveMind connection failed: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        LOG.error(
            "HiveMind connection lost: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    # mycroft handlers
    def handle_incoming_message(self, message):
        server_msg = message.data.get("payload")
        is_file = message.data.get("isBinary")
        if is_file:
            # TODO received file
            pass
        else:
            # forward server message to internal bus
            message = Message.deserialize(server_msg)
            self.bus.emit(message)

    def handle_outgoing_message(self, message):
        server_msg = message.data.get("payload")
        is_file = message.data.get("isBinary")
        if is_file:
            # TODO send file
            pass
        else:
            # send message to server
            server_msg = Message.deserialize(server_msg)
            server_msg.context["platform"] = platform
            self.sendMessage(server_msg.msg_type,
                             server_msg.data,
                             server_msg.context)

    def sendRaw(self, data):
        if self.client is None:
            LOG.error("Client is none")
            return
        self.client.sendMessage(data, isBinary=True)

    def sendMessage(self, type, data, context=None):
        if self.client is None:
            LOG.error("Client is none")
            return
        if context is None:
            context = {}
        msg = serialize_message(Message(type, data, context))

        self.client.sendMessage(msg, isBinary=False)

        self.bus.emit(Message("hive.mind.message.sent",
                              {"type": type,
                               "data": data,
                               "context": context,
                               "raw": msg}))


