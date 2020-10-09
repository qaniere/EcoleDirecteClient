import json
import requests

class ApiCaller:

    """ The class which contains methods to connect to EcoleDirecte API. 
    The method "login" has to be called before any other methods"""

    def __init__(self):
        self.login_ok = False

    def login(self, username:str, password:str):

        """ Method which send credentials to server. Take the username and password in str format in argument. Return a json 
        string with requests code and account data"""
    
        backend_url = "https://api.ecoledirecte.com/v3/login.awp"
        connection_data = 'data={"identifiant": "' + username + '", "motdepasse": "' + password + '"}'
        server_response = requests.post(backend_url, data=connection_data)

        if json.loads(server_response.text)["code"] == 200:
        #HTTP code which mean the request was succesfull and credentials was valid

            received_data = json.loads(server_response.text)
            self.login_ok = True
            self.account_token = received_data["token"]
            self.account_data = received_data["data"]["accounts"][0]
            return "Connection ok"

        elif json.loads(server_response.text)["message"] == "Mot de passe invalide !":
        #HTTP requests was succesful but credentials are invaldids

            return "Invalids credentials"
        
        else:
            print(server_response)
            return "Server error"

    def get_grades(self, account_token, account_data):

        """ WIP - Method which return a json string with grades informations """

        assert self.login == False, "You must use the login method before perfom any actions"

        url = 'https://api.ecoledirecte.com/v3/eleves/' + str(account_data['id']) + '/notes.awp?verbe=get&'
        data = 'data={"token": "' + account_token + '"}'
        request = requests.post(url, data=data)
        data = json.loads(request.text)
        