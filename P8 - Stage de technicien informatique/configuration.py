import json
import os
import subprocess
import pickle
import ctypes
import ctypes.wintypes
import subprocess
import chardet
import winshell
import threading
import markdown
import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QComboBox, QDialog, QVBoxLayout, QLineEdit,
                             QPushButton, QLabel, QCheckBox, QScrollArea, QWidget, QFrame, QTableWidget,
                             QTableWidgetItem, QSpacerItem, QSizePolicy, QHBoxLayout, QScrollArea)
from PyQt6.QtGui import QFontDatabase, QMovie, QFont, QColor
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread, QSize, QTranslator, QLocale, QLibraryInfo
from PyQt6.QtWebEngineWidgets import QWebEngineView # Importe la classe QWebEngineView
from Ui_configuration import Ui_Configuration # Importe la classe Ui_MainWindow du fichier Ui_mainwindow.py
from fiche import FicheWindow as FicheEntreeWindow



# Classe pour la gestion de la fiche d'entrée
class AjouterChampDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter des champs")
        self.resize(600, 600)
        self.mainLayout = QVBoxLayout(self)  # Créez un layout pour le widget principal
        self.scrollArea = QScrollArea(self)  # Créez une QScrollArea
        self.scrollArea.setWidgetResizable(True)  # Permet au widget de se redimensionner
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Désactive le défilement horizontal
        self.scrollAreaContent = QWidget()  # Créez un widget pour le contenu de la zone de défilement
        self.layout = QVBoxLayout(self.scrollAreaContent)  # Ajoutez un layout à ce widget
        self.layout.addWidget(QLabel("Nombre de champs à ajouter :"))
        self.number_of_fields_line_edit = QLineEdit(self)
        self.layout.addWidget(self.number_of_fields_line_edit)
        self.enregistrer_button = QPushButton("Enregistrer", self)
        self.enregistrer_button.clicked.connect(self.enregistrer)
        self.layout.addWidget(self.enregistrer_button)
        self.fields = []  # Liste pour stocker les widgets
        self.table = QTableWidget(0, 2)  # Créez un QTableWidget avec 0 lignes et 2 colonnes
        self.table.setHorizontalHeaderLabels(["Contenu du label", "Ajouter un champ de saisie"])
        # Ajustez la largeur des colonnes
        self.table.setColumnWidth(0, 350)
        self.table.setColumnWidth(1, 200)
        self.layout.addWidget(self.table)
        self.scrollArea.setWidget(self.scrollAreaContent)  # Définissez le widget de la zone de défilement
        self.mainLayout.addWidget(self.scrollArea)  # Ajoutez la QScrollArea au layout principal




    def enregistrer(self):
        if not self.number_of_fields_line_edit.text():
            QMessageBox.critical(self, "Erreur", "Veuillez entrer le nombre de champs à ajouter.")
            return
        try:
            number_of_fields = int(self.number_of_fields_line_edit.text())
        except ValueError:
            QMessageBox.critical(self, "Erreur", "Veuillez entrer un nombre valide.")
            return
        for i in range(number_of_fields):
            self.table.insertRow(self.table.rowCount())  # Ajoutez une nouvelle ligne à la fin du tableau
            label_content_line_edit = QLineEdit(self)
            self.table.setCellWidget(i, 0, label_content_line_edit)
            add_line_edit_checkbox = QCheckBox("Ajouter un champ de saisie", self)
            self.table.setCellWidget(i, 1, add_line_edit_checkbox)
            self.fields.append((label_content_line_edit, add_line_edit_checkbox))
        # Vérifiez si le bouton "Enregistrer les champs" existe déjà
        if hasattr(self, 'enregistrer_button'):
            self.layout.removeWidget(self.enregistrer_button)
            self.enregistrer_button.deleteLater()
        self.enregistrer_button = QPushButton("Enregistrer les champs", self)
        self.enregistrer_button.clicked.connect(self.enregistrer_champs)
        self.layout.addWidget(self.enregistrer_button)



    def enregistrer_champs(self):
        fields = {}
        # Vérifiez si le fichier fiche.json existe déjà
        if os.path.exists('fiche.json'):
            with open('fiche.json', 'r') as f:
                fields = json.load(f)
        # Parcourez la liste et récupérez les informations de chaque champ
        for i, (label_content_line_edit, add_line_edit_checkbox) in enumerate(self.fields):
            label_content = label_content_line_edit.text()
            add_line_edit = add_line_edit_checkbox.isChecked()
            # Vérifiez si le champ est vide
            if not label_content.strip():
                QMessageBox.critical(self, "Erreur", "Veuillez remplir tous les champs avant d'enregistrer.")
                return
            display_order = str(max([int(k) for k in fields.keys()], default=0) + 1)
            # Enregistrez les données dans un dictionnaire
            fields[display_order] = {"label_content": label_content, "add_line_edit": add_line_edit}
        # Triez les champs par ordre d'affichage
        fields = dict(sorted(fields.items()))
        # Enregistrez les champs dans votre fichier JSON
        with open('fiche.json', 'w') as f:
            json.dump(fields, f)
        self.close()



    def add_champ(self):
        self.dialog_ajouter_champ = AjouterChampDialog(self)
        self.dialog_ajouter_champ.show()



class SupprimerChampDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Supprimer des champs")
        self.setMinimumSize(300, 500)  # Définir une taille minimale pour la fenêtre
        self.layout = QVBoxLayout(self)
        # Crée un QTableWidget pour afficher les éléments
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Label", "Supprimer"])
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Désactivez le défilement horizontal
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 100)
        self.layout.addWidget(self.table)
        # Bouton pour confirmer la suppression
        self.confirm_button = QPushButton("Confirmer", self)
        self.confirm_button.clicked.connect(self.supprimer_champs)
        self.layout.addWidget(self.confirm_button)
        self.showEvent = self.update_liste
        self.update_liste()



    def update_liste(self, event=None):
        # Supprime les anciennes lignes
        self.table.setRowCount(0)
        # Vérifiez si le fichier fiche.json existe
        if not os.path.exists('fiche.json'):
            QMessageBox.critical(self, "Erreur", "Le fichier fiche.json n'existe pas.")
            return
        # Chargez les données de fiche.json
        with open('fiche.json', 'r') as f:
            fields = json.load(f)
        # Créez une ligne pour chaque entrée
        for field in fields.values():
            # Prenez les deux premiers mots du contenu du label
            label_content = field['label_content']
            words = label_content.split()
            label_text = ' '.join(words[:4])
            # Créez un QTableWidgetItem pour le label
            label_item = QTableWidgetItem(label_text)
            label_item.setFlags(label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Rend l'item non éditable
            # Créez un QCheckBox pour la case à cocher
            checkbox = QCheckBox()
            # Ajoutez une nouvelle ligne à la table
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, label_item)
            self.table.setCellWidget(row, 1, checkbox)



    def supprimer_champs(self):
        # Créez une liste pour stocker les labels à supprimer
        labels_to_remove = []
        # Parcourez les lignes de la table
        for row in range(self.table.rowCount()):
            # Obtenez la case à cocher pour cette ligne
            checkbox = self.table.cellWidget(row, 1)
            # Si la case à cocher est cochée, ajoutez le label à la liste des labels à supprimer
            if checkbox.isChecked():
                label_item = self.table.item(row, 0)
                labels_to_remove.append(label_item.text())
        # Maintenant, vous pouvez utiliser labels_to_remove pour supprimer les champs correspondants
        with open('fiche.json', 'r') as f:
            fields = json.load(f)
        keys_to_remove = []
        # Parcourez le dictionnaire pour trouver les clés correspondant aux labels à supprimer
        for key, value in fields.items():
            if value['label_content'] in labels_to_remove:
                keys_to_remove.append(key)
        # Supprimez les entrées correspondant aux clés à supprimer
        for key in keys_to_remove:
            del fields[key]
        with open('fiche.json', 'w') as f:
            json.dump(fields, f)
        # Ferme la fenêtre
        self.close()
        self.update_liste()



class ModifierOrdreDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Chargez les données de fiche.json
        with open('fiche.json', 'r') as f:
            self.champs = json.load(f)
        self.setWindowTitle("Modifier l'ordre des champs")
        # Triez les champs par le numéro d'ordre (qui est la clé du dictionnaire)
        self.champs_sorted = sorted(self.champs.items(), key=lambda item: int(item[0]))
        # Créez un QTableWidget pour afficher les éléments
        self.table = QTableWidget(len(self.champs_sorted), 2)
        self.table.setHorizontalHeaderLabels(["Label", "Numéro d'ordre"])
        # Parcourez tous les champs
        for i, (order, champ) in enumerate(self.champs_sorted):
            # Ajoutez le label de l'élément à la première colonne
            self.table.setItem(i, 0, QTableWidgetItem(champ.get("label_content", "")))
            # Ajoutez un QLineEdit pour modifier le numéro d'ordre à la deuxième colonne
            line_edit = QLineEdit(order)
            self.table.setCellWidget(i, 1, line_edit)
        # Créez un bouton pour enregistrer les modifications
        self.enregistrer_button = QPushButton('Enregistrer')
        self.enregistrer_button.clicked.connect(self.enregistrer)
        # Augmentez la taille de la fenêtre
        self.table.setFixedSize(240, 400)
        # Créez un QScrollArea et ajoutez le QTableWidget à celui-ci
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.table)
        # Ajoutez le QScrollArea et le bouton à la fenêtre
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.addWidget(self.enregistrer_button)
        self.table.setCellWidget(i, 1, line_edit)
        # Créez un bouton pour enregistrer les modifications
        self.enregistrer_button = QPushButton('Enregistrer')
        self.enregistrer_button.clicked.connect(self.enregistrer)
        # Ajoutez le QTableWidget et le bouton à la fenêtre
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.enregistrer_button)
        self.showEvent = self.update_liste



    def update_liste(self, event):
        # Chargez les données de fiche.json
        with open('fiche.json', 'r') as f:
            self.champs = json.load(f)
        # Triez les champs par le numéro d'ordre (qui est la clé du dictionnaire)
        self.champs_sorted = sorted(self.champs.items(), key=lambda item: int(item[0]))
        # Mettez à jour le nombre de lignes de la table
        self.table.setRowCount(len(self.champs_sorted))
        # Parcourez tous les champs
        for i, (order, champ) in enumerate(self.champs_sorted):
            # Ajoutez le label de l'élément à la première colonne
            self.table.setItem(i, 0, QTableWidgetItem(champ.get("label_content", "")))
            # Ajoutez un QLineEdit pour modifier le numéro d'ordre à la deuxième colonne
            line_edit = QLineEdit(order)
            self.table.setCellWidget(i, 1, line_edit)



    def enregistrer(self):
        # Collectez tous les nouveaux numéros d'ordre
        new_orders = [self.table.cellWidget(i, 1).text() for i in range(self.table.rowCount())]
        # Vérifiez si la liste contient des doublons
        if len(new_orders) != len(set(new_orders)):
            QMessageBox.critical(self, "Erreur", "Le numéro d'ordre est déjà utilisé.")
            return
        # Créez un nouveau dictionnaire pour les champs avec les nouveaux numéros d'ordre
        new_champs = {}
        for i, (order, champ) in enumerate(self.champs_sorted):
            new_champs[new_orders[i]] = champ
        # Enregistrez les modifications dans fiche.json
        with open('fiche.json', 'w') as f:
            json.dump(new_champs, f)
        # Mettez à jour self.champs et self.champs_sorted
        self.champs = new_champs
        self.champs_sorted = sorted(self.champs.items(), key=lambda item: int(item[0]))
        # Fermez la fenêtre
        self.accept()



# Classe pour exécuter la commande gpupdate dans un thread
class Worker(QObject):
    output = pyqtSignal(str)
           
    # def run_gpupdate(self):
    #     try:
    #         # Exécute la commande et capture la sortie
    #         result = subprocess.run(["gpupdate", "/force"], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    #         lines = result.stdout.split('\n')
    #         non_empty_lines = [line for line in lines if line.strip() != '']
    #         cleaned_output = '\n'.join(non_empty_lines)
    #         self.output.emit(cleaned_output)
    #     except subprocess.CalledProcessError as e:
    #         # Si la commande échoue, affiche l'erreur dans le label
    #         self.output.emit(f"Erreur : {e.stderr}")
    def run_gpupdate(self):
        process = subprocess.Popen(['gpupdate', '/force'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        output, _ = process.communicate()
        # Utilisez chardet pour déterminer l'encodage de la sortie
        encoding = chardet.detect(output)['encoding']
        # Décodez la sortie en utilisant l'encodage déterminé
        try:
            output = output.decode(encoding)
        except UnicodeDecodeError:
            output = output.decode('utf-8', 'ignore')
        self.output.emit(output)

# Classe principale de l'application
class MainWindow(QMainWindow):
    
    # Constructeur de la classe
    def __init__(self, parent=None):
        super().__init__(parent) # Appelle le constructeur de la classe parente
        self.ui = Ui_Configuration() # Crée une instance de Ui_MainWindow
        self.ui.setupUi(self) # Charge l'interface utilisateur
        
        if not os.path.isdir('aide'):
            self.show_error("Le dossier 'aide' n'a pas été trouvé dans le répertoire courant.")
            sys.exit(1)
        aide_files = ['textes', 'temps', 'fiche', 'gestion', 'style', 'accueil']
        for file in aide_files:
            if not os.path.isfile(f'aide/{file}.md'):
                self.show_error(f"Le fichier d'aide '{file}.md' n'a pas été trouvé dans le dossier 'aide'.")
                sys.exit(1)
        
        if not os.path.isfile('session_manager.exe'):
            self.show_error("Le fichier 'session_manager.exe' n'a pas été trouvé dans le répertoire courant.")
            sys.exit(1)
            # Récupération des users
            
            
        # def get_users():
        #     command = "net user"
        #     output = subprocess.check_output(command)
        #     encoding = chardet.detect(output)['encoding']
        #     users_to_exclude = ['Administrateur', 'Invit']
        #     users = []
        #     for line in output.decode(encoding).splitlines():
        #         user = line.strip()
        #         if user and user not in users_to_exclude and re.match(r"^[a-zA-Z0-9_\- ]+$", user):
        #             users.append(user)
        #     return users
        
        
        def get_users():
            try:
                # Exécute une commande PowerShell pour obtenir la liste des utilisateurs
                result = subprocess.run(["powershell", "-Command", "Get-WmiObject -Class Win32_UserAccount | Select-Object Name | Out-File -FilePath .\\users.txt -Encoding utf8"], capture_output=True, text=True)
                if os.path.exists('.\\users.txt'):
                    with open('.\\users.txt', 'r', encoding='utf-8') as file:
                        users = file.read().split('\n')
                    # Supprime le fichier une fois qu'il n'est plus utilisé
                    os.remove('.\\users.txt')
                    # Supprime la première ligne vide
                    users.pop(0)
                    # Retire les éléments vides de la liste (dû aux sauts de ligne)
                    users = [user.strip() for user in users if user.strip() != '']
                    # Exclut les utilisateurs 'Administrateur', 'Invit', 'WDAGUtilityAccount', et les lignes non désirées
                    users_to_exclude = ['Administrateur', 'Invité', 'WDAGUtilityAccount', 'Name', '----', 'DefaultAccount']
                    users = [user for user in users if user not in users_to_exclude]
                    return users
                else:
                    self.show_error("Erreur", "Erreur lors de l'exécution de la commande PowerShell : " + result.stderr)
                    return []
            except Exception as e:
                self.show_error("Erreur lors de la récupération de la liste des utilisateurs : " + str(e))
                return []
        
        
        
        self.charger_conf() # Charge les données à partir du fichier JSON
        self.ui.annuler.clicked.connect(self.close) # Ferme la fenêtre (annule les modifications)
        self.ui.Enregistrer.clicked.connect(self.enregistrer_conf) # Enregistrement de la configuration
        self.ui.gpupdate.clicked.connect(self.make_gpupdate) # Exécution de gpupdate
        self.ui.aide_textes.clicked.connect(lambda: self.afficher_aide('textes')) # Affiche l'aide pour le texte
        self.ui.aide_temps.clicked.connect(lambda: self.afficher_aide('temps')) # Affiche l'aide pour le timer
        self.ui.aide_fiche.clicked.connect(lambda: self.afficher_aide('fiche')) # Affiche l'aide pour la fiche
        self.ui.aide_gestion.clicked.connect(lambda: self.afficher_aide('gestion')) # Affiche l'aide pour la gestion
        self.ui.aide_style.clicked.connect(lambda: self.afficher_aide('style')) # Affiche l'aide pour le style
        self.ui.aide_accueil.clicked.connect(lambda: self.afficher_aide('accueil')) # Affiche l'aide pour l'accueil
        self.ui.mod_fond.clicked.connect(lambda: self.modifier_couleur('fond')) # Modifie le fond de la fenêtre
        self.ui.mod_texte.clicked.connect(lambda: self.modifier_couleur('texte')) # Modifie le texte de la fenêtre
        self.ui.mod_bouton.clicked.connect(lambda: self.modifier_couleur('bouton')) # Modifie la couleur des boutons
        self.ui.mod_bouton_texte.clicked.connect(lambda: self.modifier_couleur('bouton_texte')) # Modifie la couleur du texte des boutons
        self.ui.mod_bouton_survol.clicked.connect(lambda: self.modifier_couleur('bouton_survol')) # Modifie la couleur des boutons au survol
        self.ui.police.addItems(QFontDatabase.families()) # Ajoute les polices disponibles dans la liste déroulante
        users = get_users() # Récupère la liste des utilisateurs
        self.ui.session_user.addItems(users) # Ajoute les noms des utilisateurs dans la liste déroulante
        self.ui.session_activation.stateChanged.connect(self.session_activation_changed)
        # Crée l'instance de classe pour l'ajout de champs de la fiche d'entrée
        self.ajouterchamp = AjouterChampDialog()
        self.ui.ajouter_champ.clicked.connect(self.ajouterchamp.add_champ)
        # Crée l'instance de classe pour la suppression de champs de la fiche d'entrée
        self.supprimerchamp = SupprimerChampDialog()
        self.ui.supprimer_champ.clicked.connect(self.supprimerchamp.show)
        # Crée l'instance de classe pour la modification de l'ordre des champs de la fiche d'entrée
        self.ui.modifierordre = ModifierOrdreDialog()
        self.ui.modifier_ordre.clicked.connect(self.ui.modifierordre.show)
        # Connecte le signal clicked du bouton fiche_afficher à la méthode afficher_fiche_entree
        self.ui.fiche_afficher.clicked.connect(self.afficher_fiche_entree)
        # Ajouter les choix à la QComboBox fermeture_session
        self.ui.fermeture_session.addItem("Déconnecter")
        self.ui.fermeture_session.addItem("Verrouiller")
        # Connectez le signal currentTextChanged à une nouvelle méthode
        self.ui.fermeture_session.currentTextChanged.connect(self.on_combobox_changed)
        # Crée et affiche un QLabel avec un QMovie
        self.movie = QMovie("img\\loading.gif")  # Remplacez "loading.gif" par le chemin de votre fichier GIF
        self.movie.setScaledSize(QSize(140, 80)) 
        self.gpupdate_thread = QThread()
        self.ui.retour_gpupdate.setMovie(self.movie)
        # Arrête le QMovie et cache le QLabel lorsque le thread est terminé
        self.gpupdate_thread.finished.connect(self.movie.stop)
        # Gestion des différentes checkbox en fonction de l'état des autres checkbox qui leurs sont liées
        self.ui.fiche_activation.toggled.connect(self.fiche_activation_changed)
        self.ui.fiche_log.setEnabled(False)
        self.ui.fiche_15min.stateChanged.connect(self.check_duration_options)
        self.ui.fiche_30min.stateChanged.connect(self.check_duration_options)
        self.ui.fiche_1h.stateChanged.connect(self.check_duration_options)
        self.ui.fiche_duree_session.stateChanged.connect(self.fiche_duree_session_changed)
        self.ui.fiche_15min.stateChanged.connect(self.update_fiche_duree_session)
        self.ui.fiche_30min.stateChanged.connect(self.update_fiche_duree_session)
        self.ui.fiche_1h.stateChanged.connect(self.update_fiche_duree_session)
        # Gestion des couleurs de la fenêtre popup
        self.ui.couleur_fond.textChanged.connect(lambda text: self.save_tmp('couleur_fond', text))
        self.ui.couleur_fond.textChanged.connect(self.update_color)
        self.ui.couleur_texte.textChanged.connect(lambda text: self.save_tmp('couleur_texte', text))
        self.ui.couleur_texte.textChanged.connect(self.update_color)
        self.ui.couleur_bouton.textChanged.connect(lambda text: self.save_tmp('couleur_bouton', text))
        self.ui.couleur_bouton.textChanged.connect(self.update_color)
        self.ui.couleur_bouton_texte.textChanged.connect(lambda text: self.save_tmp('couleur_bouton_texte', text))
        self.ui.couleur_bouton_texte.textChanged.connect(self.update_color)
        self.ui.couleur_bouton_survol.textChanged.connect(lambda text: self.save_tmp('couleur_bouton_survol', text))
        self.ui.couleur_bouton_survol.textChanged.connect(self.update_color)
        self.ui.texte_bouton.textChanged.connect(lambda text: self.save_tmp('texte_bouton', text))
        self.ui.largeur_popup.textChanged.connect(lambda text: self.save_tmp('largeur_popup', text))
        self.ui.hauteur_popup.textChanged.connect(lambda text: self.save_tmp('hauteur_popup', text))
        self.ui.police.currentTextChanged.connect(lambda text: self.save_tmp('police', text))
        self.ui.taille_police.textChanged.connect(lambda text: self.save_tmp('taille_police', text))
        
        self.ui.previsu_popup.clicked.connect(self.afficher_popup)
        
        self.update_color()
        # Charge les données à partir du fichier JSON
        try:
            with open("config.json", "r") as f: # Ouvre le fichier JSON en lecture
                data = json.load(f) # Charge les données dans un dictionnaire
        except FileNotFoundError: # Si le fichier n'est pas trouvé, crée un dictionnaire vide
            data = {}
        if data.get('fiche', {}).get('fiche_log', False):
            self.ui.fiche_log.setEnabled(True)



    # Gestion des erreurs
    def show_error(self, message):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Erreur")
        error_dialog.setText(message)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.exec()



    # Fonction pour sauvegarder les données dans la popup dans un fichier tmp
    # Les données tmp sont enregistrées lors d'un changement de champ dans l'onglet Style
    def save_tmp(self, field_name, text):
        # Charger les données existantes
        try:
            with open('data.tmp', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        # Mettre à jour les données avec la nouvelle valeur
        data[field_name] = text
        # Écrire les données dans le fichier
        with open('data.tmp', 'w') as f:
            json.dump(data, f)
    
    
    
    def update_color(self):
        try:
            with open('data.tmp') as f:
                tmp = json.load(f)
        except FileNotFoundError:
            tmp = {}
        with open('config.json') as f:
            config = json.load(f)            
        data = {**config['style'], **tmp}
        self.ui.label_fond.setStyleSheet(f"background-color: {data['couleur_fond']}; border: 1px solid black;")
        self.ui.label_texte.setStyleSheet(f"background-color: {data['couleur_texte']}; border: 1px solid black;")
        self.ui.label_bouton.setStyleSheet(f"background-color: {data['couleur_bouton']}; border: 1px solid black;")
        self.ui.label_bouton_texte.setStyleSheet(f"background-color: {data['couleur_bouton_texte']}; border: 1px solid black;")
        self.ui.label_survol.setStyleSheet(f"background-color: {data['couleur_bouton_survol']}; border: 1px solid black;")
    
    
    
    # Fonction pour supprimer le fichier data.tmp à la fermeture de la fenêtre
    def closeEvent(self, event):
        try:
            os.remove('data.tmp')
        except FileNotFoundError:
            pass
        super().closeEvent(event)
    
    
    
    # Fonction pour afficher le popup de prévisualisation
    def afficher_popup(self):
        # Chargement des données depuis data.tmp
        try: 
            with open('data.tmp') as f:
                tmp = json.load(f)
        except FileNotFoundError:
            tmp = {}
            
        with open('config.json') as f:
            config = json.load(f)            
        data = {**config['style'], **tmp}
        
        fenetre = QDialog()
        fenetre.setFixedSize(int(data['largeur_popup']), int(data['hauteur_popup']))
        fenetre.setStyleSheet(f"background-color: {data['couleur_fond']};")
        fenetre.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        fenetre.setWindowFlags(fenetre.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout(fenetre)

        # Créer un nouveau layout pour le label
        layout_texte = QVBoxLayout()
        layout_texte.setContentsMargins(20, 0, 20, 0)  # Appliquer une marge de 10 pixels

        label = QLabel(config['text']['text_popup_1'])
        label.setWordWrap(True)
        label.setStyleSheet(f"color : {data['couleur_texte']};")
        police = data['police']
        taille_police = int(data['taille_police'])
        font = QFont(police, taille_police)
        label.setFont(font)

        # Ajouter le label au layout_texte au lieu du layout principal
        layout_texte.addWidget(label)

        # Ajouter le layout_texte au layout principal
        layout.addLayout(layout_texte)

        bouton = QPushButton(f"{data['texte_bouton']}")
        bouton.setFixedSize(200,35)
        bouton.setStyleSheet(f"""
        QPushButton:enabled {{
            background-color: {data['couleur_bouton']};
            border-radius: 15px;
            border: 1px solid black;
            color: {data['couleur_bouton_texte']};
            font-family: {data['police']};
            font-size: {taille_police}px;
            font-weight: bold;
            padding: 5px 1px;
            text-decoration: none;
        }}
        QPushButton:hover {{
            background-color: {data['couleur_bouton_survol']};
        }}
        QPushButton:pressed {{
            position: relative;
            top: 1px;
        }}
        """)
        bouton.clicked.connect(fenetre.close)
        layout.addWidget(bouton)
        # Créer un QHBoxLayout
        layout_bouton = QHBoxLayout()
        # Ajouter un QSpacerItem à gauche
        layout_bouton.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        # Ajouter le bouton au layout
        layout_bouton.addWidget(bouton)
        # Ajouter un QSpacerItem à droite
        layout_bouton.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        # Ajouter le layout_bouton au layout principal
        layout.addLayout(layout_bouton)
        fenetre.setLayout(layout)
        fenetre.show()
        #print("Popup créée.") # Pour débugger
        fenetre.exec()



    # On affiche un message d'informations si l'utilisateur sélectionne "Verrouiller"
    def on_combobox_changed(self, text):
        if text == "Verrouiller":
            QMessageBox.information(self, "Information", "Le verrouillage ne permettra pas de lancer le Session Manager automatiquement à la prochaine connexion de la session.\n\nVous devrez déconnecter la session manuellement pour que Session Manager fonctionne automatiquement.")



    # Fonction pour corréler l'activation de la fenêtre de log avec l'activation de la fiche d'entrée
    def fiche_activation_changed(self, checked):
        if not checked:
            self.ui.fiche_log.setChecked(False)
            self.ui.fiche_log.setEnabled(False)
        else:
            self.ui.fiche_log.setEnabled(True)



    # Fonction pour décocher et désactiver la checkbox "Durée de la session" si aucune des cases à cocher "15 min", "30 min" et "1h" n'est cochée
    def check_duration_options(self):
        if not self.ui.fiche_15min.isChecked() and not self.ui.fiche_30min.isChecked() and not self.ui.fiche_1h.isChecked():
            self.ui.fiche_duree_session.setChecked(False)
            self.ui.fiche_duree_session.setEnabled(False)
        else:
            self.ui.fiche_duree_session.setEnabled(True)


    # Fonction pour cocher automatiquement la checkbox "Durée de la session" si une des cases à cocher "15 min", "30 min" et "1h" est cochée
    def update_fiche_duree_session(self):
        if self.ui.fiche_15min.isChecked() or self.ui.fiche_30min.isChecked() or self.ui.fiche_1h.isChecked():
            self.ui.fiche_duree_session.setChecked(True)
            self.ui.fiche_duree_session.setEnabled(True)
        else:
            self.ui.fiche_duree_session.setChecked(False)
            self.ui.fiche_duree_session.setEnabled(False)



    # Fonction pour afficher la popup de la fiche d'entrée
    def afficher_fiche_entree(self):
        # Crée et affiche une instance de FicheEntreeWindow
        self.fiche_entree_window = FicheEntreeWindow()
        self.fiche_entree_window.show()



    # Fonction qui désactive la checkbox "Durée de la session" si aucune des cases à cocher "15 min", "30 min" et "1h" n'est cochée
    def fiche_duree_session_changed(self, checked):
        if not checked:
            self.ui.fiche_15min.setChecked(False)
            self.ui.fiche_30min.setChecked(False)
            self.ui.fiche_1h.setChecked(False)



    # Fonction pour créer le raccourci
    def create_shortcut(self):
        try:
            if getattr(sys, 'frozen', False):
                # Le programme a été compilé avec PyInstaller
                directory = os.path.dirname(sys.executable)
            else:
                # Le programme est exécuté en tant que script Python
                directory = os.path.dirname(os.path.abspath(__file__))
            # Défini current_folder comme le répertoire courant
            file_path = os.path.join(directory, "session_manager.exe")
            # Vérifie que le fichier session_manager.exe existe dans le répertoire courant
            if not os.path.exists(file_path):
                return f"Erreur : l'éxecutable session_manager.exe est introuvable dans le répertoire courant.\nIl doit se trouver dans le répertoire : {directory}."
            # Récupère le nom de l'utilisateur sélectionné dans la liste déroulante
            user = self.ui.session_user.currentText()
            shortcut_path = f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\session_manager.lnk"
            # Crée le raccourci
            with winshell.shortcut(shortcut_path) as shortcut:
                shortcut.path = file_path
                shortcut.working_directory = directory
            return "Le raccourci a été créé correctement."
        except FileNotFoundError:
            return "Erreur : le fichier session_manager.exe n'a pas été trouvé."
        except Exception as e:
            return f"Erreur inattendue : {e}"




    # Fonction pour gérer l'activation du raccourci
    def session_activation_changed(self, state):
        user = self.ui.session_user.currentText()
        shortcut_path = f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\session_manager.lnk"
        # Si la case est cochée, crée le raccourci
        if self.ui.session_activation.isChecked():
            message = self.create_shortcut()
            self.ui.retour_activation.setText(message)
        # Sinon, supprime le raccourci
        else:
            if os.path.exists(shortcut_path):
                try:
                    os.remove(shortcut_path)
                    self.ui.retour_activation.setText("Le raccourci a été supprimé correctement.")
                except FileNotFoundError:
                    self.ui.retour_activation.setText("Erreur : Le raccourci n'existe pas.")
                except Exception as e:
                    self.ui.retour_activation.setText(f"Erreur inattendue : {e}")
    



    # Fonction pour afficher l'aide 
    def afficher_aide(self, type_aide):
        try:
            if getattr(sys, 'frozen', False):
                # Le programme a été compilé avec PyInstaller
                directory = os.path.dirname(sys.executable)
            else:
                # Le programme est exécuté en tant que script Python
                directory = os.path.dirname(os.path.abspath(__file__))
            chemin_fichier = os.path.join(directory, "aide\\"f"{type_aide}.md")
            with open(chemin_fichier, "r",encoding="utf-8") as f:
                aide = f.read()
            aide_html = markdown.markdown(aide)  # Convertit le Markdown en HTML
            msgBox = QMessageBox()
            msgBox.setTextFormat(Qt.TextFormat.RichText)  # Utilise un format de texte riche pour prendre en compte le HTML
            msgBox.setText(aide_html)  # Définit le texte de la fenêtre
            msgBox.setWindowTitle(f"Aide pour l'onglet {type_aide.capitalize()}")  # Définit le titre de la fenêtre
            msgBox.exec()
        except FileNotFoundError:  # Si le fichier n'est pas trouvé, affiche un message d'erreur
            QMessageBox.warning(self, "Erreur", f"Le fichier d'aide pour {type_aide} n'a pas été trouvé.")



    # Fonction pour modifier les couleurs de la fenêtre popup
    def modifier_couleur(self, type_modification):
        translator = QTranslator(app)
        locale = QLocale.system().name()
        path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        translator.load("qt_" + locale, path)
        app.installTranslator(translator)
        
        # Affiche, par défaut, la couleur présent dans le QLineEdit
        if type_modification == "fond":
            couleur_initiale = QColor(self.ui.couleur_fond.text())
        elif type_modification == "texte":      
            couleur_initiale = QColor(self.ui.couleur_texte.text())
        elif type_modification == "bouton":
            couleur_initiale = QColor(self.ui.couleur_bouton.text())
        elif type_modification == "bouton_texte":
            couleur_initiale = QColor(self.ui.couleur_bouton_texte.text())
        elif type_modification == "bouton_survol":
            couleur_initiale = QColor(self.ui.couleur_bouton_survol.text())
        
        
        # Affiche une fenêtre de dialogue pour choisir la couleur
        couleur = QtWidgets.QColorDialog.getColor(couleur_initiale)
        if couleur.isValid():
            # Récupère le code hexadécimal de la couleur
            code_hexa = couleur.name()
            # Définit la couleur du bouton en fonction du type de modification
            if type_modification == "fond":
                self.ui.couleur_fond.setText(code_hexa)
            elif type_modification == "texte":
                self.ui.couleur_texte.setText(code_hexa)
            elif type_modification == "bouton":
                self.ui.couleur_bouton.setText(code_hexa)
            elif type_modification == "bouton_texte":
                self.ui.couleur_bouton_texte.setText(code_hexa)
            elif type_modification == "bouton_survol":
                self.ui.couleur_bouton_survol.setText(code_hexa)
    
    
    
        
        
    # Fonction pour modifier le label retour_gpupdate et éxecuter la fonction run_gpupdate dans un thread
    def make_gpupdate(self):
        if hasattr(self, 'gpupdate_thread') and self.gpupdate_thread.isRunning():
            self.gpupdate_thread.quit()
            self.gpupdate_thread.wait()
        # Crée un Worker et un QThread
        self.gpupdate_thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.gpupdate_thread)
        # Connecte les signaux
        self.worker.output.connect(self.update_output)
        self.gpupdate_thread.started.connect(self.worker.run_gpupdate)
        self.gpupdate_thread.finished.connect(self.gpupdate_thread.deleteLater)
        self.movie.start()
        # Démarre le thread
        self.gpupdate_thread.start()  
    
        
        
        
    def update_output(self, text):
        # Met à jour le QLabel avec le résultat de la commande gpupdate /force
        self.ui.retour_gpupdate.setText(text)
        
        
       
    # Fonction pour vérifier que les champs sont des entiers positifs
    def verifier_entier_positif(self, nom_champ, valeur):
        try:
            valeur_int = int(valeur)
            if valeur_int <= 0:
                raise ValueError
        except ValueError:
            if nom_champ == "timer_popup_1":
                nom_champ = "Le délai entre l'affichage de la première fenêtre et l'ouverture de la session"
            elif nom_champ == "timer_popup_2":
                nom_champ = "Le délai entre l'affichage de la deuxième fenêtre et la fermeture de la session"
            elif nom_champ == "timer_popup_3":
                nom_champ = "Le délai entre l'affichage de la fenêtre de fermeture et la fermeture de la session"
            elif nom_champ == "duree_session":
                nom_champ = "La durée de la session"
            elif nom_champ == "delai_fermeture":
                nom_champ = "Le délai de fermeture automatique des fenêtres"
            elif nom_champ == "largeur_popup":
                nom_champ = "La largeur des fenêtres"
            elif nom_champ == "hauteur_popup":
                nom_champ = "La hauteur des fenêtres"
            elif nom_champ == "taille_police":
                nom_champ = "La taille de la police"
            QMessageBox.warning(self, "Erreur", f"{nom_champ} doit être un entier strictement positif.")
            return False

        return True
       
        
        
    # Fonction pour enregistrer les données dans un fichier JSON
    def enregistrer_conf(self):
        timer_popup_1 = int(self.ui.timer_popup_1.text())
        timer_popup_2 = int(self.ui.timer_popup_2.text())
        duree_session = int(self.ui.duree_session.text())
        # Enregistre les données dans une liste de tuples
        champs_a_verifier = [
            ("timer_popup_1", timer_popup_1),
            ("timer_popup_2", timer_popup_2),
            ("timer_popup_3", self.ui.timer_popup_3.text()),
            ("duree_session", duree_session),
            ("delai_fermeture", self.ui.delai_fermeture.text()),
            ("largeur_popup", self.ui.largeur_popup.text()),
            ("hauteur_popup", self.ui.hauteur_popup.text()),
            ("taille_police", self.ui.taille_police.text())
        ]
        # Vérifie que les champs sont des entiers positifs
        for nom_champ, valeur in champs_a_verifier:
            if not self.verifier_entier_positif(nom_champ, valeur):
                return
        # Vérifie que la somme des timers est inférieure à la durée de la session
        if timer_popup_1 + timer_popup_2 > duree_session:
            QMessageBox.warning(self, "Erreur", "La somme de du délai entre l'affichage de la première fenêtre et le délai entre l'affichage de la dernière fenêtre avant la fermeture de la session ne peut pas être supérieure à la durée de la session.")
            return
        try:
            # Crée un dictionnaire avec les données de l'interface utilisateur
            # Les données sont stockées dans un dictionnaire imbriqué
            config = {
                "text" :{
                    "text_popup_1" : self.ui.text_popup_1.toPlainText(), # Récupère le texte du champ text_popup_1
                    "text_popup_2" : self.ui.text_popup_2.toPlainText(), # Récupère le texte du champ text_popup_2
                    "text_fermeture" : self.ui.text_fermeture.toPlainText(), # Récupère le texte du champ text_popup_4
                },
                "timer" :{
                    "delai_fermeture" : self.ui.delai_fermeture.text(), # Etc etc... other champ, same principe
                    "duree_session" : self.ui.duree_session.text(),
                    "timer_popup_1" : self.ui.timer_popup_1.text(),
                    "timer_popup_2" : self.ui.timer_popup_2.text(),
                    "timer_popup_3" : self.ui.timer_popup_3.text(),
                },
                "fiche" :{
                    "fiche_log" : self.ui.fiche_log.isChecked(),
                    "fiche_activation" : self.ui.fiche_activation.isChecked(),
                    "fiche_duree_session" : self.ui.fiche_duree_session.isChecked(),
                    "fiche_15min" : self.ui.fiche_15min.isChecked(),
                    "fiche_30min" : self.ui.fiche_30min.isChecked(),
                    "fiche_1h" : self.ui.fiche_1h.isChecked(),
                },
                "session" :{
                    "session_user" : self.ui.session_user.currentText(),
                    "session_activation" : self.ui.session_activation.isChecked(),
                },
                "style" :{
                    "largeur_popup" : self.ui.largeur_popup.text(),
                    "hauteur_popup" : self.ui.hauteur_popup.text(),
                    "police" : self.ui.police.currentText(),
                    "taille_police" : self.ui.taille_police.text(),
                    "couleur_fond" : self.ui.couleur_fond.text(),
                    "couleur_texte" : self.ui.couleur_texte.text(),
                    "couleur_bouton" : self.ui.couleur_bouton.text(),
                    "couleur_bouton_texte" : self.ui.couleur_bouton_texte.text(),
                    "couleur_bouton_survol" : self.ui.couleur_bouton_survol.text(),
                    "texte_bouton" : self.ui.texte_bouton.text(),
                },
                "fermeture" :{
                    "fermeture_session" : self.ui.fermeture_session.currentText(),
                    "fermeture_popup" : self.ui.activation_fermeture.isChecked(), 
                }
            }

            # Enregistrez les données dans un fichier JSON
            with open("config.json", "w") as f:
                json.dump(config, f,indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer la configuration : {e}")
        # Ferme la fenêtre
        self.close()
            
            
            
    # Fonction pour charger les données à partir du fichier JSON
    def charger_conf(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        # Charge les données dans l'interface utilisateur
        self.ui.text_popup_1.setPlainText(data.get("text", {}).get("text_popup_1", ""))
        self.ui.text_popup_2.setPlainText(data.get("text", {}).get("text_popup_2", ""))
        self.ui.text_fermeture.setPlainText(data.get("text", {}).get("text_fermeture", ""))
        self.ui.delai_fermeture.setText(data.get("timer", {}).get("delai_fermeture", ""))
        self.ui.duree_session.setText(data.get("timer", {}).get("duree_session", ""))
        self.ui.timer_popup_1.setText(data.get("timer", {}).get("timer_popup_1", ""))
        self.ui.timer_popup_2.setText(data.get("timer", {}).get("timer_popup_2", ""))
        self.ui.timer_popup_3.setText(data.get("timer", {}).get("timer_popup_3", ""))
        self.ui.fiche_log.setChecked(data.get("fiche", {}).get("fiche_log", False))
        self.ui.fiche_activation.setChecked(data.get("fiche", {}).get("fiche_activation", False))
        self.ui.fiche_duree_session.setChecked(data.get("fiche", {}).get("fiche_duree_session", False))
        self.ui.fiche_15min.setChecked(data.get("fiche", {}).get("fiche_15min", False))
        self.ui.fiche_30min.setChecked(data.get("fiche", {}).get("fiche_30min", False))
        self.ui.fiche_1h.setChecked(data.get("fiche", {}).get("fiche_1h", False))
        QTimer.singleShot(100, lambda: self.ui.session_user.setCurrentText(data.get("session", {}).get("session_user", "")))
        self.ui.session_activation.setChecked(data.get("session", {}).get("session_activation", False))
        self.ui.largeur_popup.setText(data.get("style", {}).get("largeur_popup", ""))
        self.ui.hauteur_popup.setText(data.get("style", {}).get("hauteur_popup", ""))
        QTimer.singleShot(100, lambda: self.ui.police.setCurrentText(data.get("style", {}).get("police", "")))
        self.ui.taille_police.setText(data.get("style", {}).get("taille_police", ""))
        self.ui.couleur_fond.setText(data.get("style", {}).get("couleur_fond", ""))
        self.ui.couleur_texte.setText(data.get("style", {}).get("couleur_texte", ""))
        self.ui.couleur_bouton.setText(data.get("style", {}).get("couleur_bouton", ""))
        self.ui.couleur_bouton_texte.setText(data.get("style", {}).get("couleur_bouton_texte", ""))
        self.ui.texte_bouton.setText(data.get("style", {}).get("texte_bouton", ""))
        self.ui.couleur_bouton_survol.setText(data.get("style", {}).get("couleur_bouton_survol", ""))
        self.ui.fermeture_session.setCurrentText(data.get("fermeture", {}).get("fermeture_session", ""))
        self.ui.activation_fermeture.setChecked(data.get("fermeture", {}).get("fermeture_popup", False))
        
        
        
    # Fonction pour ajouter un champ à la fiche d'entrée
    def ajouter_champ(self):
        self.dialog_ajouter = QDialog()
        self.dialog_ajouter.show()



# Point d'entrée de l'application
if __name__ == "__main__":
    app = QApplication(sys.argv) # Crée une instance de QApplication
    window = MainWindow() # Crée une instance de MainWindow
    window.show() # Affiche la fenêtre
    app.exec() # Lance l'application
