# Session Manager v1.0b

Session Manager est un ensemble de deux programmes permettant la gestion des sessions invités dans le point Cyber de la mairie de Louhans-Chateaurenaud.

## Auteur
Session Manager a été forgé à la main par [Mickaël Faivre](mailto:contact@m-faivre.fr)<br>
J'en profite pour remercier Github Copilot qui a su m'éclairer quand j'en avais besoin.

## Code-source
Le code-source est disponible auprès de Mr Antoine Armanet. Conseiller numérique de la mairie de Louhans-Chateaurenaud.<br>
Il est également disponible, sur demande, en m'envoyant un mail à contact@m-faivre.fr

Vous pouvez également le trouver sur le Github du projet : https://github.com/impli-osx/session_manager

## Installation

Pour installer Session Manager, il suffit de copier l'ensemble du répertoire n'importe où sur le PC hôte.<br>
Il n'y a aucune autre manipulation à faire

## Utilisation

Pour personnaliser l'ensemble des paramètres dans le gestionnaire de session, vous pouvez utiliser le programme *configuration.exe*<br>
Le second exécutable, *session_manager.exe*, ne doit pas être lancé manuellement. Il sera exécuté par Windows, au démarrage de la session, s'il est activé.

## Features

L'exécutable de configuration permet une personnalisation assez grande du programme.<br>

 - Fonctions générales
	- Activer ou désactiver Session Manager
	- Choisir le compte qui sera concerné par la gestion de session
	- Recharger les GPO locales
 - Gestion de la fiche d'entrée
	 - Activer ou désactiver la fiche d'entrée
	 - Activer ou désactiver le stockage des données utilisateurs dans un document Excel
	 - Définir le temps de session voulu (donnée à usage statistique)
	 - Gestion des champs présents dans la fiche d'entrée
		 - Ajouter ou supprimer des champs (texte simple ou texte et champ de saisie)
		 - Modifier l'ordre d'affichage des données à remplir
		 - Afficher une prévisualisation de la fiche d'entrée
- Définir les textes qui seront affichés dans l'ensemble des popups
	- Possibilité d'utiliser des variables pour remplacer les valeurs dynamiques
- Personnaliser l'apparence des popups :
	- Taille de la fenêtre (largeur et hauteur)
	- Choix de la police de caractère et de sa taille
	- Choix des couleurs utilisées
		- Couleur de fond du popup
		- Couleur de la police de caractère
		- Couleur du bouton
		- Couleur du texte du bouton
		- Couleur du bouton au survol
		- Texte du bouton
	- Prévisualisation du popup
- Définir les différents timers (minuteurs) utilisés :
	- Durée globale d'une session
	- Délai avant affichage du premier popup de rappel
	- Délai avant affichage du second popup
	- Durée d'affichage des popups avant leur fermeture automatique
	- Durée d'affichage de la fenêtre avant la déconnexion de la session
-  Type de fermeture de session (déconnexion ou verrouillage de session)
- Activer ou désactiver la fenêtre de fermeture de session
- Personnalisation des fichiers d'aide (format markdown)

L'ensemble de la configuration est stockée dans le fichier *config.json*. C'est ce fichier qui sera lu par *session_manager.exe* afin d'adapter ses paramètres de fonctionnement.


## Documentation technique

Session Manager a été écrit en Python, dans sa version 3.12. Il utilise le framework PyQt6.<br>
Le design *configuration.exe* a été fait grâce à Qt Designer.

Les deux programmes ont été pseudo-compilés avec PyInstaller.<br>
La commande utilisée pour la compilation est :

    pyinstaller --onedir --noconsole session_manager.exe

Cela permet de décompresser l'ensemble des dépendances nécessaires au bon fonctionnement des programmes et ainsi de réduire leur temps d'exécution. L'option *--noconsole* permet de ne pas avoir de prompt Python qui s'affiche en arrière-plan.<br>
Cette pseudo-compilation permet d'utiliser Session Manager sans avoir besoin que Python soit installé sur la machine hôte. Un interpréteur Python étant automatiquement ajouté au programme lors de sa compilation en exécutable.


Lors de l'activation de Session Manager sur un PC hôte, un raccourci sera automatiquement créé dans le répertoire suivant :

> C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\

 Ceci permet que l'exécutable *session_manager.exe* soit activé à chaque nouveau démarrage de la session sans avoir à modifier les GPO locales de l'ordinateur.<br>
 Noter également qu'un verrouillage/déverrouillage de session n'est pas considéré comme l'ouverture d'une nouvelle session par Windows. Ainsi, si la session est verrouillée, le programme ne sera pas exécuté.

 ## Aide
 Chaque onglet du programme *configuration.exe* possède un bouton d'aide.<br>
 L'aide est stockée dans le dossier éponyme, dans le répertoire courant du script.
 

> C:\mon\répertoire\session_manager\aide

Il est parfaitement possible de personnaliser les fichiers d'aide avec un éditeur de texte.<br>
Néanmoins, vous devez savoir que l'aide est rédigée au format Markdown. Vous devez respecter cette syntaxe si vous ne souhaitez pas rencontrer de problème lors de son affichage.

Vous trouverez plus d'informations au sujet de Markdown et de sa syntaxe [sur le site officiel](https://www.markdownguide.org/cheat-sheet/).

## Règlement intérieur du point Cyber
Vous pouvez modifier le règlement intérieur en remplaçant simplement le PDF nommé *reglement.pdf*<br>
Attention toutefois à bien respecter le nom actuel. Si vous nommez le fichier différemment, il ne sera pas pris en compte par le programme.
Le PDF se trouve à l'emplacement suivant :

> C:\mon\répertoire\session_manager\reglement.pdf

## Logo de la mairie
Vous pouvez modifier le logo actuel en remplaçant le fichier logo.png présent dans le dossier /img/, dans le répertoire courant du script.

> C:\mon\répertoire\session_manager\img\logo.png

Attention à respecter les dimensions actuelles. Le programme ne modifie pas les dimensions de l'image. Un logo trop grand ou trop petit pourrait avoir un impact sur la mise en page des différentes fenêtres.<br>
Le programme n'a aucune considération quant au format utilisé (JPEG, PNG, etc.). Notez cependant que l'usage d'un PNG est recommandé afin d'apporter une transparence au logo.

## Données utilisateurs
Les données que l'utilisateur entre dans la fiche d'entrée sont stockées (si l'option est activé) dans le fichier Excel nommé *data.xlsx*
Vous le trouverez dans le répertoire courant du programme.

> C:\mon\répertoire\session_manager\data.xlsx

Ce fichier est mis à jour à chaque nouvelle entrée. Chaque ligne représente une entrée.

Sa structure dépend des champs que vous avez dans votre fiche d'entrée. Si, par exemple, vous créez un champ "Nom", alors une colonne "Nom" sera ajouté au tableau Excel.<br>
Si par la suite vous décidez de supprimer ce champ, il restera présent dans le tableau. Mais les utilisateurs suivants n'auront plus à le remplir et chaque nouvelle ligne sera vide.

Le tableau Excel enregistre une nouvelle feuille par année. Cela signifie que les utilisateurs entrant leurs données durant l'année 2024 seront stockés dans la feuille nommée "2024" du fichier data.xlsx. A chaque changement d'année, une nouvelle feuille sera créée et les données seront automatiquement enregistrées dans la nouvelle feuille.

## Fiche d'entrée
*configuration.exe* permet d'ajouter, de supprimer et de modifier l'ordre d'affichage des champs à remplir par l'utilisateur.<br>
Les données concernant la structure, le nom, l'ordre des champs sont stockées dans le fichier *fiche.json*

La structure de chaque entrée ressemble à ceci :

> {"1": {"label_content": "Nom", "add_line_edit": true}

Le numéro défini son ordre d'affichage. Le 1 sera donc le premier élément placé lors de la génération du formulaire.<br>
"label_content" défini le nom du champ. Ce sera également le nom utilisé pour nommer la colonne dans le fichier Excel.<br>
"add_line_edit" est un booléen (True ou False). True signifie que le label (le texte) sera accompagné d'un champ de saisie. False signifie que le label sera seul.

Dans tous les cas, je vous déconseille fortement d'éditer manuellement ce fichier.<br>
Ce chapitre est là à titre purement informatif.<br>
Si vous avez besoin de modifier, supprimer, ajouter des champs, vous devez passer par l'exécutable de configuration. Cela évitera les erreurs, notamment dans la gestion de l'ordre d'affichage.

## License

[GNU GENERAL PUBLIC LICENSE - Version 3](https://www.gnu.org/licenses/gpl-3.0.html)