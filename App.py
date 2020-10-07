import os
import json
import time
import getpass
import requests
from ApiHandler import ApiCaller

class EcoleDirecteClient(ApiCaller):

    """ An "wonderfool" Ecole Directe unofficial client"""

    def __init__(self, username = False, password = False):

        """ If username and password are entered in the constructor, they will not be requested to the user"""

        if username == False or password == False:
            username = str(input("Nom d'utilisateur : "))
            password = getpass.getpass(prompt="Mot de passe : ")

        login_status= self.login(username, password)

        if login_status == "Connection ok": 
            print("Bienvenue")
        elif login_status == "Invalids credentials": 
            print("Indentiants incorrects")
        else: 
            print("Erreur serveur")

if __name__ == "__main__":

    app = EcoleDirecteClient()
