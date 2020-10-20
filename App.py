import os
import json
import time
import getpass
import platform
import requests
from terminaltables import AsciiTable

class EcoleDirecteClient:

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

    
    def fetch_timeline(self):

        """ Method which return the four last elements of timeline """

        url = 'https://api.ecoledirecte.com/v3/eleves/' + str(self.account_data['id']) + '/timeline.awp?verbe=get&'
        data = 'data={"token": "' + self.account_token + '"}'
        request = requests.post(url, data=data)
        data = json.loads(request.text)
        data = data["data"]
        result = []
        for i in range(4):
            event_type = data[i]["typeElement"]
            if event_type == "Note":
                final_string = f"- Nouvelle note en {data[i]['soustitre'].lower().capitalize()}"
            elif event_type == "VieScolaire":
                final_string = f"- {data[i]['titre']} du {data[i]['date']} ({data[i]['contenu']})"
            else:
                final_string = "Event not implemted. Please open Github issue"
            result.append(final_string)
        return result


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
            timeline_data = self.fetch_timeline()

            table_data = [["Menu", "Derniers événements"]]
            table_data.append(["1 - Voir vos informations          ", timeline_data[0]])
            table_data.append(["2 - Voir vos notes", timeline_data[1]])
            table_data.append(["q - Quitter l'application", timeline_data[2]])
            table = AsciiTable(table_data)
            print(table.table)

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

        """ Method which sort and display grade in a ASCII table"""

        self.clear_screen()
        self.get_grades()
        grades_dict = {}

        for grade in self.grades:
        #Loop that create a dict key per subject with empty list as value, 
        #then append each assignments to this list
            subject = grade["libelleMatiere"]  
            assignment = {
                "title": grade["devoir"],
                "result": grade["valeur"] + "/" + grade["noteSur"], 
                "coefficient": grade["coef"],
                "class_average": grade["moyenneClasse"] + "/" + grade["noteSur"],
                "no_mandatory": grade["nonSignificatif"]
            }

            if subject not in grades_dict:
                grades_dict[subject] = []
            
            grades_dict[subject].append(assignment)
              
        iteration = 0
        averages = []
        table_data = [["Matière", "Notes"]]
        for key, value in grades_dict.items():
        #Get subject and the list of assignments of this subject
        
            products = [] 
            terms = []
            iteration += 1 #Allow to subject left
            no_mandatory = ""
            if value[0]["no_mandatory"]:
                no_mandatory = "- Non significatif"
            else:
            #Calculate and add to average only if it's a signifiant grade
                grade_on_20 = self.convert_grade_to_20(value[0]["result"])
                products.append(grade_on_20 * float(value[0]["coefficient"]))
                terms.append(float(value[0]["coefficient"]))
            
            table_data.append([key, f"{value[0]['title']} : {value[0]['result']} (Coef {value[0]['coefficient']} - Moyenne : {value[0]['class_average']} {no_mandatory})"])
            #Key it's the subjet 

            if len(value) > 1:
            #If the subject has more than one asignements

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
            #Calculation of the subject average
            table_data.append(["--------------------", "-------------------------------------------------------------------------"])
            if iteration == len(grades_dict): 
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
