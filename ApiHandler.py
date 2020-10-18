import json
import requests

class ApiCaller:

    """ The class which contains methods to connect to EcoleDirecte API. 
    The method "login" has to be called before any other methods"""

    def __init__(self):
        self.grades = None

    def login(self, username:str, password:str):

        """ Method which send credentials to server. Take the username and password in str format in argument. Return a json 
        string with requests code and account data"""
    
        backend_url = "https://api.ecoledirecte.com/v3/login.awp"
        connection_data = 'data={"identifiant": "' + username + '", "motdepasse": "' + password + '"}'
        server_response = requests.post(backend_url, data=connection_data)

        if json.loads(server_response.text)["code"] == 200:
        #HTTP code which mean the request was succesfull and credentials was valid

            received_data = json.loads(server_response.text)
            self.account_token = received_data["token"]
            self.account_data = received_data["data"]["accounts"][0]
            return "Connection ok"

        elif json.loads(server_response.text)["code"] == 505:
        #HTTP requests was succesful but credentials are invaldids

            return "Invalids credentials"
        
        else:
            print(server_response.text)
            return "Server error"

    def get_grades(self):

        """Method wich get the grades and store it in self.grades"""

        url = 'https://api.ecoledirecte.com/v3/eleves/' + str(self.account_data['id']) + '/notes.awp?verbe=get&'
        data = 'data={"token": "' + self.account_token + '"}'
        request = requests.post(url, data=data)
        data = json.loads(request.text)
        self.grades = data["data"]["notes"]
        