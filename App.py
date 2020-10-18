import os
import json
import time
import getpass
import platform
import requests
from ApiHandler import ApiCaller
from terminaltables import AsciiTable

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
            2 - Afficher vos notes 
            q - Quitter l'application
            """)
            choice = input(">>> ")
            if choice == "1": self.informations()
            elif choice == "2": self.show_grades()
            elif choice == "q": exit(0)


    def informations(self):

        self.clear_screen()

        print("Vos informations EcoleDirecte :")
        print("  Nom complet :", self.first_name, self.account_data["nom"].upper())
        print("  Classe :", self.account_data["profile"]["classe"]["libelle"])
        print("  Dernière connexion :", self.account_data["lastConnexion"]) #TODO : Refactor date format
        print("  Adresse e-mail :", self.account_data["email"])
        print("  Régime :", self.account_data["modules"][10]["params"]["regime"]) #TODO (Afficher les jours)
        print("  Numéro de carte de cantine :", self.account_data["modules"][0]["params"]["numeroBadge"])
        input("")

    def show_grades(self):

        self.clear_screen()
        self.get_grades()
        grades_dict = {}

        for grade in self.grades:
            subject =  grade["libelleMatiere"]
            
            assignment = {
                "title": grade["devoir"],
                "result": grade["valeur"] + "/" + grade["noteSur"]          
            }

            if subject not in grades_dict:
                grades_dict[subject] = []
            
            grades_dict[subject].append(assignment)
            table_data = [["Matière", "Notes"]]
        
        iteration = 0
        for key, value in grades_dict.items():
            iteration += 1
            table_data.append([key, value[0]["title"] + " : " + value[0]["result"]])
            if len(value) > 1:
                for assignment in value:
                    if assignment != value[0]:
                        table_data.append(["    ", assignment["title"] + " : " + assignment["result"]])
            if iteration != len(grades_dict): 
                table_data.append(["--------------------", "------------------------------------------------------------------"])
        table = AsciiTable(table_data)
        print (table.table)
        input()

if __name__ == "__main__":
    app = EcoleDirecteClient()
