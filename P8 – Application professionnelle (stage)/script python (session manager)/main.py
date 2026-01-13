import json
from PyQt6.QtWidgets import QApplication, QMainWindow
from interface import Ui_Configuration  # Assurez-vous que c'est le bon chemin d'importation

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Configuration()
        self.ui.setupUi(self)
            
        # Load data from the JSON file
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
                data = {}
        """  
        # Fill the user interface fields with the data
        self.ui.fermeture_session.setText(data.get("fermeture_session", ""))
        self.ui.activation_fermeture.setChecked(data.get("activation_fermeture", False))
        """
        self.ui.Enregistrer.clicked.connect(self.on_save_clicked)
                    
    def on_save_clicked(self):
        # Cette fonction est appelée lorsque l'utilisateur clique sur le bouton "Enregistrer"

        # Récupérez les données de l'interface utilisateur
        data = {
            "fermeture_session": self.ui.fermeture_session.text(),
            "activation_fermeture": self.ui.activation_fermeture.isChecked(),
            # Ajoutez ici d'autres champs si nécessaire
        }

        # Enregistrez les données dans un fichier JSON
        with open("config.json", "w") as f:
            json.dump(data, f)
            
            

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()