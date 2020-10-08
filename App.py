import os
import json
import time
import getpass
import platform
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


    def clear_screen(self):

        """ Method which clear screen, on Windows or Linux"""

        if platform.system() == "Windows": command = "cls"
        else: command = "clear"
        os.system(command)


    def menu(self):

        """ Method which contain the menu of the app """

        app_is_running = True
        while app_is_running:
            self.clear_screen()
            self.first_name = self.account_data['prenom'].lower().capitalize() #Convert BOB to Bob 
            print(f"Bienvenue {self.first_name} !")
            print(""" 
            Que voulez vous faire ?

            1 - Afficher vos informations personnelles
            q - Quitter l'application
            """)
            choice = input(">>> ")
            if choice == "1": self.informations()


    def informations(self):

        self.clear_screen()
        print("Vos informations :")
        print("Dernière connexion :", self.account_data["lastConnexion"])
        print("Votre classe :", self.account_data["profile"]["classe"]["libelle"])
        input("")


if __name__ == "__main__":

    app = EcoleDirecteClient()
