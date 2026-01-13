
# Session Manager

L'utilitaire Session Manager est utilisé pour gérer les sessions utilisateurs "Salle connectée" sur les PC de prêt de la mairie de Louhans-Chateaurenaud.




## Auteur

- [Mickaël Faivre (mrimpli@gmail.com)]


## Installation & Pré-requis

Session Manager nécessite l'installation de Python 3.12 sur la machine hôte.

Python doit être installé pour l'ensemble des utilisateurs. Le PATH doit être configuré et les droits administrateurs doivent être utilisés lors de l'installation.


Aucune autre installation n'est nécessaire, vous pouvez copier les fichier session_manager.exe, configuration.exe et config.json d'un ordinateur à l'autre.


Pour que session_manager.exe soit lancé au démarrage de la session concernée par le verrouillage automatique, vous devez placer un raccourci de session_manager.exe dans le répertoire suivant :
C:\Users\%USERS%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

Le programme ne peut pas fonctionner s'il est utilisé via le planificateur de tâches. Ceci est du à l'utilisation de la librairie Tkinter dans le projet. Le planificateur de tâches nécessitant de pouvoir s'éxecuter dans un environnement sans interface graphique, ce blocage n'est pas contournable en l'état.

Un menu d'aide contextuel est disponible dans chaque onglet de configuration.exe, via le bouton "?"


## Documentation

L'utilitaire est composé de deux programmes éxécutable :

- session_manager.exe
- configuration.exe

Un troisième fichier est créé lorsque la configuration a été faite :
- config.json


Ces trois fichiers doivent impérativement être placés dans le même répertoire. Dans le cas contraire, session_manager.exe ne peut fonctionner et un message d'erreur s'affichera.


---

- Session_manager.exe
C'est le programme qui se lancera en tâche de fond lors de l'ouverture d'une session par l'utilisateur concerné.
Ce programme se charge de :
- Afficher un popup à l'ouverture de session
- Afficher un popup après une durée déterminée 
- Afficher un popup peut de temps avant la fermeture de session

Les informations affichées et les délais sont enregistrés dans config.json.

- configuration.exe
Ce programme permet de personnaliser l'ensemble des données requises par session_manager.exe

Quand ce programme est lancé pour la première fois et que l'ensemble des champs ont été renseignés, alors le fichier config.json est ajouté au répertoire courant de l'utilitaire.



- config.json
Ce fichier ne doit pas être édité manuellement afin d'éviter les erreurs de syntaxe, entre autre.
Si vous avez besoin de modifier les informations de fonctionnement de l'utilitaire, vous devez utiliser configuration.exe


Le fichier de configuration sera automatiquement chargé à l'ouverture de configuration.exe afin de récupérer les données en temps réelles.

---
Compilation 
-

La compilation des deux scripts s'est faite via pyinstaller.
Pour l'installer, ouvrez une invite de commande administrateur sur un PC disposant de Python :

pip install pyinstaller

Pour compiler les programmes pour qu'ils soient portables et que la fenêtre python ne s'affiche pas :

pyinstaller --onefile --noconsole le_script.py


L'éxecutable sera disponible dans le répertoire \dist de l'emplacement de votre script.
A partir de ce moment là, l'éxecutable peut-être déplacé sans se soucier des dépendances (hormis l'installation de python 3.12)


## Features

- Gestion de la durée de la session
- Gestion de la durée d'affichage des popups
- Personnalisation des textes affichés dans les popups
- Personnalisation de la taille des popups
- Personnalisation de la police et de la taille de la police de caractère
- Modification des titres des popups
- Sélection du type de fermeture de session : Verrouiller/déconnecter



## Support

En cas de problème ou d'informations complémentaires, contactez mrimpli@gmail.com

Les code-source au format .py de session_manager et de configuration sont disponibles auprès d'Antoine Armanet.
