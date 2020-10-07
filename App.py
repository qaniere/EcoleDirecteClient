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
            self.menu()
        elif login_status == "Invalids credentials": 
            print("Vos identifiants sont incorrects")
        else: 
            print("Erreur serveur")

    def menu(self):

        """ Method which contain the menu of the app """

        self.prenom = self.account_data['prenom'].lower().capitalize() #Convert BOB to Bob 
        print(f"Bienvenue {self.prenom} !")


if __name__ == "__main__":

    app = EcoleDirecteClient("QuentinAniere", "Buster67")
