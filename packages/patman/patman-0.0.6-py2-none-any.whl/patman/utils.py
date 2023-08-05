from json_tricks import (
    dumps as ddumps, 
    loads as lloads
)
from json import dumps as ordumps, loads as orloads



def dumps(obj, **kwargs) -> str:
    complex_obj = ddumps(obj, **kwargs)
    return ordumps(complex_obj)
    

def loads(string, **kwargs) -> dict:
    orloaded = orloads(string)
    return lloads(orloaded)