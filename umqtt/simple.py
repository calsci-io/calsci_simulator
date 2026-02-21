class MQTTClient:
    def __init__(self, client_id, server, port=1883, user=None, password=None, keepalive=0, ssl=False, ssl_params=None):
        self.client_id = client_id
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.keepalive = keepalive
        self.ssl = ssl
        self.ssl_params = ssl_params or {}
        self._callback = None
        self._connected = False

    def set_callback(self, callback):
        self._callback = callback

    def connect(self, clean_session=True):
        _ = clean_session
        self._connected = True
        return 0

    def publish(self, topic, msg, retain=False, qos=0):
        _ = (topic, msg, retain, qos)
        return True

    def subscribe(self, topic, qos=0):
        _ = (topic, qos)
        return True

    def wait_msg(self):
        return None

    def check_msg(self):
        return None

    def ping(self):
        return None

    def disconnect(self):
        self._connected = False
