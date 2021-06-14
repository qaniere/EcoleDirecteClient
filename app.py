import os
import json
import time
import getpass
import platform
import requests
from terminaltables import AsciiTable


class EcoleDirecteClient:

    """ An Ecole Directe unofficial client in the terminal"""

    def __init__(self, username = False, password = False):

        """ If username and password are entered in the constructor, they will not be requested to the user"""
        self.clear_screen()

        if username == False or password == False:
            print("Connexion à EcoleDirecte :")
            username = str(input("Nom d'utilisateur : "))
            password = getpass.getpass(prompt="Mot de passe : ")
            self.clear_screen()

        print("Connexion en cours...")
        login_status= self.login(username, password)

        if login_status == "Connection ok": 
            self.menu()
        elif login_status == "Invalids credentials": 
            print("Vos identifiants sont incorrects")
        else: 
            print("Erreur serveur")

    
    def clear_screen(self):

        """ Method which clear screen on every os"""

        if platform.system() == "Windows":
            command = "cls"
        else: 
            command = "clear"
        os.system(command)


    def login(self, username:str, password:str) -> str:

        """ Method which send credentials to server. Take the username and password in str format in argument. Return a json 
        string with requests code and account data"""

        backend_url = "https://api.ecoledirecte.com/v3/login.awp"
        connection_data = 'data={"identifiant": "' + username + '", "motdepasse": "' + password + '"}'
        server_response = requests.post(backend_url, data=connection_data)

        if json.loads(server_response.text)["code"] == 200:
        #The request was succesfull and credentials was valid

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


    def menu(self):

        """ Method which contain the menu of the app """

        app_is_running = True
        while app_is_running:
            self.clear_screen()
            print("Récupération des données en cours...")
            timeline_data = self.fetch_timeline()
            self.clear_screen()

            print(f"Bienvenue {self.account_data['prenom'].lower().capitalize()}.")
            table_data = [["Menu", "Derniers événements"]]
            table_data.append(["1 - Voir vos informations          ", timeline_data[0]])
            table_data.append(["2 - Voir vos notes", timeline_data[1]])
            table_data.append(["q - Quitter l'application", timeline_data[2]])
            table = AsciiTable(table_data)
            print(table.table)

            choice = input(">>> ")
            if choice == "1": self.display_informations()
            elif choice == "2": self.show_grades()
            elif choice == "q": exit(0)


    def fetch_timeline(self):

        """ Method which return the four last elements of timeline """

        url = 'https://api.ecoledirecte.com/v3/eleves/' + str(self.account_data['id']) + '/timeline.awp?verbe=get&'
        request_data = 'data={"token": "' + self.account_token + '"}'
        request = requests.post(url, data=request_data)
        data = json.loads(request.text)
        try:
            data = data["data"]
        except:
            result = ["Timeline is not working currently", "Timeline is not working currently", "Timeline is not working currently", "Timeline is not working currently"]
        else:

            result = []
            for i in range(4):

                event_type = data[i]["typeElement"]
                if event_type == "Note":
                    final_string = f"- Nouvelle note en {data[i]['contenu'].lower().capitalize()}"
                elif event_type == "VieScolaire":
                    final_string = f"- {data[i]['titre']} du {data[i]['date']} ({data[i]['contenu']})"
                else:
                    final_string = "Event not implemented. Please open Github issue"
                result.append(final_string)

        return result


    def display_informations(self):

        self.clear_screen()
        print("Vos informations EcoleDirecte :")
        print()
        print("  Identité :", self.account_data["prenom"].lower().capitalize(), self.account_data["nom"].upper())
        print("  Classe :", self.account_data["profile"]["classe"]["libelle"])
        print("  Numéro RNE de l'établissement :", self.account_data["profile"]["rneEtablissement"])
        print("  Dernière connexion :", self.account_data["lastConnexion"])
        print("  Adresse e-mail :", self.account_data["email"])
        print("  Numéro de téléphone : ", self.account_data["profile"]["telPortable"])
        print("  Régime :", self.account_data["modules"][10]["params"]["regime"])
        print("  Numéro de carte de cantine :", self.account_data["modules"][0]["params"]["numeroBadge"])
        print()
        input("Appuyez sur entrée pour continuer...")


    def get_grades(self):

        """Method wich get the grades and store it in self.grades"""

        url = 'https://api.ecoledirecte.com/v3/eleves/' + str(self.account_data['id']) + '/notes.awp?verbe=get&'
        data = 'data={"token": "' + self.account_token + '"}'
        request = requests.post(url, data=data)
        data = json.loads(request.text)
        self.grades = data["data"]["notes"]

    



    


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
