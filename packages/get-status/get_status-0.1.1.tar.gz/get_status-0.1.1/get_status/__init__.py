import requests

class __init__():

    def get_status(url,user_agent):
        if user_agent == "auto":
            user_agent = "Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0"
        if user_agent == "None":
            header = None
        else:
            header = {"user-agent":user_agent}

        r = requests.get(url, headers=header)
        return(r.status_code)
