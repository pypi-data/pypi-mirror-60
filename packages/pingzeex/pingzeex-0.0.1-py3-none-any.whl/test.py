import paho.mqtt.client as mqtt
import json
from datetime import datetime



class Helloworld:
    """
        Tests the functionality of handshaking for Helloworld
    """
    def __init__(self, node_uid="12345678", node_key="123456870"):


        self._node_uid = node_uid
        self._node_key = node_key

        self.transport = "tcp"

        self.topic =  self._node_uid + "/dkcs/dead/node"
        self.rx_uid = "0"
        self.payload = {
            "type" : 2,
            "data":{
                "created_at": str(datetime. now()),
                "config_id": self._node_key,
                "uid": self._node_uid,
                "rx_uid": self.rx_uid

            },
            "channel": "",
            "to": None

        }
        
        self.json_payload = json.dumps(self.payload)


        self.client = mqtt.Client(transport = self.transport)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        self.data = {
                        "type": "0",
                        "data": {
    
                            'uid': self._node_uid,
                            'config_id': self._node_key,
                            'lwt': True,
    
                        },
                        "channel": "",
                        "to": None
                    }
        self.json_data = json.dumps(self.data)


    def connect(self):
        self.client.connect("mqtt.pingzee.xyz", 1883, 2)
    
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.subscribe()
        self.publish()

    def on_disconnect(self):
        print("Test")

    def will_set(self):
        # will_set (topic, payload, qos = , retain = False)
        self.client.will_set(self.topic, self.json_payload)

    def set_options(self):
        self.client.ws_set_options(path="/mqtt", headers = None)


    def publish(self):
        print("Custom Publish Called")
        print(self.json_data)
        self.client.publish("pingzee/dkcs/auth/fullflow", self.json_data)

    def subscribe(self):
        print("Custom Sub Called")
        print(type(self._node_uid+"/pingzee/dkcs/auth/response"))
        print(self.client.subscribe(self._node_uid+"/pingzee/dkcs/auth/response"))
        print("Custom Sub Done")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

    def run(self):
        self.will_set()
        #self.set_options()
        self.connect()
        self.client.loop_forever()


if __name__ == "__main__":
    t = Helloworld()
    t.run()


