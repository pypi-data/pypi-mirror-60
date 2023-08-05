# Conventions for rendering at www.3za.org
from cachetools import cached,TTLCache,LRUCache
from jsonpath_ng.ext import parse
import requests
import json
from typing import Union, List
from .web_utils import get_url, is_url

# -----------------  Instruction interpretation   ------------------
#   www.3za.org/jsonpath/
#   www.3za.org/jsonpaths/
#   www.3za.org/mirror/
#   www.3za.org/pipe/        Invoke Algorithmia algorithm

def render_jsonpath(url,json_path:str,full=False,**ignored) -> str:
    instructions = {"url":url,"json_path":json_path,"full":full,"error_advice":"Try debugging at https://jsonpath.curiousconcept.com/"}
    obj   = json.loads(get_url(url))
    try:
        jsonpath_expr = parse(json_path)
    except Exception as e:
        instructions.update({"error":"Bad json_path  "+json_path+" "+str(e)})
        return json.dumps(instructions)

    try:
        if full:
            matches = dict( [(str(match.full_path),match.value) for match in jsonpath_expr.find(obj) ])
        else:
            matches = [match.value for match in jsonpath_expr.find(obj) ]
        return json.dumps(matches)
    except Exception as e:
        instructions.update({"error":"Error matching with  "+json_path+" "+str(e)})
        return json.dumps(instructions)



def render_jsonpaths(url:str,json_paths:List[str],**ignored) -> str:
    instructions = {"url":url,"json_paths":json_paths}
    try:
        obj   = json.loads(get_url(url))
    except Exception as e:
        instructions.update({"error":"Expecting url to contain JSON data "+str(e)})
        return json.dumps(instructions)

    results = dict()
    for ky,path_ in json_paths.items():
        try:
            jsonpath_expr = parse(path_)
            matches = [match.value for match in jsonpath_expr.find(obj) ]
            results[ky] = matches[0]
        except Exception as e:
            instructions.update( {"error":str(e),"key":ky,"path":path_,
                       "error_advice":"Try debugging at https://jsonpath.curiousconcept.com/"} )
            return json.dumps(instructions)
    return json.dumps(results)

def render_mirror(url:str) -> str:
    try:
        return get_url(url)
    except:
        try:
            return get_url(url.decode('utf-8'))
        except:
            try:
                return get_url(url["url"])
            except:
                return json.dumps({"url":url,"error":"Could not get_url"})

def render_pipe(algo_name,api_key,input=None,input_url=None,**ignored):
    """ Call Algorithmia algorithm """
    return cached_render_pipe(algo_name,api_key,input,input_url)

@cached(TTLCache(1000,1))
def cached_render_pipe(algo_name:str,api_key:str,input:str=None,input_url:str=None,**ignored)->str:

    instructions = {"algo_name":algo_name,"api_key":api_key,"input":input, "input_url":input_url}
    if not '/' in algo_name:
        instructions.update({"error":"Expecting full algo name (such as threezatests/double)"})
        return json.dumps(instructions)

    # Get input to algorithm
    if "input" is not None:
        try:
            input = json.loads(input)
        except:
            try:
                input = input.decode('utf-8')  # <-- Not sure about this being here
            except:
                pass

    elif "input_url" is not None:
        try:
            input = json.loads(get_url(input_url))
        except Exception as e:
            instructions.update({"error":"Error: expecting JSON input from "+url+" :"+ str(e)})
            return json.dumps(instructions)
    else:
        input = None

    # Call the algo
    headers = {'Content-Type':'application/json','Authorization':'Simple '+api_key}
    response = requests.post(
        'https://api.algorithmia.com/v1/algo/'+algo_name,
        headers=headers,
        data=json.dumps(input)
    )
    if response.status_code==200:
        output=response.json()
        return output
    else:
        instructions.update({"input":input,"error":"Issue calling algo: status_code="+str(response.status_code) })
        return json.dumps(instructions)
