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
                "result": grade["valeur"] + "/" + grade["noteSur"], 
                "coefficient": grade["coef"],
                "class_average": grade["moyenneClasse"],
                "no_mandatory": grade["nonSignificatif"]
            }

            if subject not in grades_dict:
                grades_dict[subject] = []
            
            grades_dict[subject].append(assignment)
            table_data = [["Matière", "Notes"]]
        
        iteration = 0
        averages = []
        for key, value in grades_dict.items():
        #Get subject and list of assignments
        
            products = []
            terms = []
            iteration += 1 #Allow to subject left
            no_mandatory = ""
            if value[0]["no_mandatory"]:
                no_mandatory = "- Non significatif"
            else:
                grade_on_20 = self.convert_grade_to_20(value[0]["result"])
                products.append(grade_on_20 * float(value[0]["coefficient"]))
                terms.append(float(value[0]["coefficient"]))
            table_data.append([key, f"{value[0]['title']} : {value[0]['result']} (Coef {value[0]['coefficient']} - Moyenne : {value[0]['class_average']} {no_mandatory})"])
            if len(value) > 1:
            #If it still assignments 
                for assignment in value:
                    no_mandatory = ""
                    if assignment != value[0]:
                    #Do not work again with the first one
                        if assignment["no_mandatory"]:
                            no_mandatory = "- Non significatif"
                        else:
                            grade_on_20 = self.convert_grade_to_20(assignment["result"])
                            products.append(grade_on_20 * float(assignment["coefficient"]))
                            terms.append(float(assignment["coefficient"]))
                        table_data.append(["    ",  f"{assignment['title']} : {assignment['result']} (Coef {assignment['coefficient']} - Moyenne : {assignment['class_average']} {no_mandatory})"])
            subject_average = round(sum(products) / sum(terms), 2)
            averages.append(subject_average)
            table_data.append(["Moyenne", str(subject_average)])
            if iteration != len(grades_dict): 
                table_data.append(["--------------------", "--------------------------------------------------------------------"])
            else:
                table_data.append(["--------------------", "--------------------------------------------------------------------"])
                table_data.append(["Moyenne générale", str(round(sum(averages) / len(averages), 2))])
        table = AsciiTable(table_data)
        print(table.table)
        input()

    def convert_grade_to_20(self, grades):

        """ Method wich convert x/y to x/20 """

        grades = grades.replace(",", ".")
        grades = grades.split("/")
        for i in range(len(grades)): grades[i] = float(grades[i])
        result = (grades[0] / grades[1]) * 20
        return result


if __name__ == "__main__":
    app = EcoleDirecteClient()
