import shortuuid
from mycroft.configuration.config import ConfigurationManager
from mycroft.identity import IdentityManager
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util import str2bool

_config = ConfigurationManager().get_config().get("pairing_client")


def generate_pairing_code():
    shortuuid.set_alphabet("0123456789ABCDEF")
    return shortuuid.random(length=6)


class DevicePairingClient(object):
    def __init__(self, config=_config, pairing_code=None):
        self.config = config
        self.ws_client = WebsocketClient(host=config.get("host"),
                                         port=config.get("port"),
                                         path=config.get("route"),
                                         ssl=str2bool(config.get("ssl")))
        self.identity_manager = IdentityManager()
        self.identity = self.identity_manager.identity
        self.pairing_code = (
            pairing_code if pairing_code else generate_pairing_code())

    def on_registration(self, message):
        # TODO: actually accept the configuration message and store it in
        # identity
        identity = self.identity_manager.get()
        register_payload = message.metadata
        if register_payload.get("device_id") == identity.device_id:
            identity.token = register_payload.get('token')
            identity.owner = register_payload.get('user')
            self.identity_manager.update(identity)
            self.ws_client.close()

    def send_device_info(self):
        msg = Message("device_info",
                      metadata={
                          "pairing_code": self.pairing_code,
                          "device_id": self.identity.device_id
                      })

        self.ws_client.emit(msg)

    def print_error(self, message):
        print(repr(message))

    def run(self):
        self.ws_client.on('registration', self.on_registration)
        self.ws_client.on('open', self.send_device_info)
        self.ws_client.on('error', self.print_error)
        self.ws_client.run_forever()


def main():
    DevicePairingClient().run()

if __name__ == "__main__":
    main()
