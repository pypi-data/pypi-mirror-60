import cytoolz
from abc import ABC
from cachetools import cached, LRUCache
import faster_than_requests as requests
from patman.utils import dumps
import json

class Patman(ABC):
    """ 
        A way to handle reads and writes consistently without having to write every single variable:

         
    """
    def __init__(self, host:str):
        self.host = host
        self._parameter_types = ["port", "protocol"]
        self._accepted_protocols = ["http", "https", "tcp"]
        self._parameters = {
            "port": 80,
            "protocol": "http"
        }
        # Data that we'll have to serialize after
        self._data = {}


    @property
    def parameters(self) -> dict:
        return self._parameters

    def _add_protocol(self, protocol:str):
        if protocol in self._accepted_protocols:
            self._parameters["protocol"] = protocol

    def __setitem__(self, key, value):
        if key in self._parameter_types:
            if key == "port":
                self._parameters["port"] = value
            elif key == "protocol":
                self._add_protocol(value)
            return
        self._data[key] = value
        return self._data

    def __getitem__(self, key):
        if key in self._data.keys():
            return self._data.get(key, None)
        return None
    
    def cereal(self, data:dict) -> str:
        return dumps(data)

    @cached(cache=LRUCache(maxsize=2048))
    def _create_url_call(self, url:str):
        port = self.parameters['port']
        protocol = self.parameters['protocol']
        host = self.host
        if port == 80:
            return f"{protocol}://{host}/{url}"
        return f"{protocol}://{host}:{port}/{url}"

    def get(self, url:str):
        call = self._create_url_call(url)
        response = requests.get2json(call)
        return json.loads(response)

    def post(self, url:str, body:dict): 
        call = self._create_url_call(url)
        cbody = self.cereal(body)
        response = requests.post2json(call, cbody)
        return json.loads(response)


    def put(self, url:str, body:dict):
        call = self._create_url_call(url)
        cbody = self.cereal(body)
        response = requests.put2json(call, cbody)
        return json.loads(response)
    
    def delete(self, url:str, body:dict):
        call = self._create_url_call(url)
        cbody = self.cereal(body)
        response = requests.delete2json(call, cbody)
        return json.loads(response)

if __name__ == "__main__":
    patman = Patman(host="httpbin.org")
    # for _ in range(10000000):
    #     patman._create_url_call("get")
    print(patman)