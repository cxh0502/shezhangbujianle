import requests
import hashlib
import time
import json
import os

ACCOUNT = ''
PHONE = ''

SUBMIT_URL = "http://api-air.inspur.com:32102/v1/interface/api/requestId?"
REPLY_URL = "http://api-air.inspur.com:32102/v1/interface/api/result?"

def code_md5(str):
    code=str.encode("utf-8")
    m = hashlib.md5()
    m.update(code)
    result= m.hexdigest()
    return result

def rest_get(url, header,timeout, show_error=False):
    '''Call rest get method'''
    try:
        response = requests.get(url, headers=header,timeout=timeout, verify=False)
        return response
    except Exception as exception:
        if show_error:
            print(exception)
        return None

def header_generation():
    """Generate header for API request."""
    t=time.strftime("%Y-%m-%d", time.localtime())
    global ACCOUNT, PHONE
    ACCOUNT, PHONE = os.environ.get('YUAN_ACCOUNT').split('||')
    token=code_md5(ACCOUNT+PHONE+t)
    headers = {'token': token}
    return headers

def submit_request(query,temperature,topP,topK,max_tokens,):
    """Submit query to the backend server and get requestID."""
    headers=header_generation()
    url=SUBMIT_URL + "account={0}&data={1}&temperature={2}&topP={3}&topK={4}&tokensToGenerate={5}&type={6}".format(ACCOUNT,query,temperature,topP,topK,max_tokens,"api")
    response=rest_get(url,headers,30)
    response_text = json.loads(response.text)
    #print(response_text)
    if  response_text["flag"]:
        requestId = response_text["resData"]
        return requestId
    else:
        raise  RuntimeWarning(response_text)

def reply_request(requestId,):
    """Check reply API to get the inference response."""
    url = REPLY_URL + "account={0}&requestId={1}".format(ACCOUNT, requestId)
    headers=header_generation()
    for i in range(3):
        response = rest_get(url, headers, 30)
        response_text = json.loads(response.text)
        #print(response_text)
        if response_text["resData"] != None:
            return response_text
        if response_text["flag"] == False and i ==2:
            raise  RuntimeWarning(response_text)
        time.sleep(3)

