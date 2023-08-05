import json
import requests

class Api:
    credential = {
        "id" : "",
        "password":""
    }
    cookie = None
    
    user = {}
    
    API = {}
    endpoint = "https://judgeapi.u-aizu.ac.jp"
    path = {
        "session":"/session",
        "submit":"/submissions",
        "submit_record_recent":"/submission_records/users/%s/problems/%s",
    }
    
    status_codes={
        0 : "STATE_COMPILEERROR",
        1 : "STATE_WRONGANSWER",
        2 : "STATE_TIMELIMIT",
        3 : "STATE_MEMORYLIMIT",
        4 : "STATE_ACCEPTED",
        5 : "STATE_WAITING",
        6 : "STATE_OUTPUTLIMIT",
        7 : "STATE_RUNTIMEERROR",
        8 : "STATE_PRESENTATIONERROR",
        9 : "STATE_RUNNING"
    }
    
    post_header_base = {'content-type': 'application/json'}
    
    def __init__(self, user_id, password):
        for k, v in list(self.path.items()):
            self.API[k] =  self.endpoint + v
        self.credential["id"] = user_id
        self.credential["password"] = password
        
        self._get_session()
    
    def _get_session(self):
        cred = {
            "id" : self.credential["id"],
            "password" : self.credential["password"]
        }
        
        resp = requests.post(
            self.API["session"],
            headers =  self.post_header_base,
            data = json.dumps(cred)
        )
        
        if resp.status_code != 200:
            raise AojApiError("auth error", detail=resp)
        
        self.user = resp.json()
        self.cookie = resp.cookies
        
    def submit(self, problem_id, language, source_code):
        data = {
            "problemId" : problem_id,
            "language" : language,
            "sourceCode" : source_code
        }
        
        resp = requests.post(
            self.API["submit"],
            headers =  self.post_header_base,
            cookies = self.cookie,
            data = json.dumps(data)
        )
        
        if resp.status_code != 200:
            raise AojApiError("submit error", detail=resp)
        
        resp_data = resp.json()
        if "token" not in list(resp_data.keys()):
            raise AojApiError("submit success, but receive invalid responce", detail=resp)
        
        return resp_data
    
    def get_my_submit_record(self, problem_id):
        url = self.API["submit_record_recent"] % (self.user["id"], problem_id)
        
        resp = requests.get(
            url,
        )
        return resp.json()
    

class AojApiError(Exception):
    err_message = None
    err_detail = None
    
    def __init__(self, message, detail=None):
        self.set_message(message)
        self.set_detail(detail)
        
    def set_message(self, message):
        self.err_message = message
    
    def set_detail(self, detail):
        self.err_detail = detail
    
    def get_message(self):
        return self.err_message
    
    def get_detail(self):
        return self.err_detail
    

