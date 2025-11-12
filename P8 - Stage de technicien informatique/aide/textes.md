## Permet de définir les textes affichés dans les popups


**Texte de la première fenêtre** : Généralement un texte pour informer l'user qu'il lui X minutes avant la fin de session.<br>
En fonction du temps défini, ceci n'est pas un message d'urgence.


**Texte de la seconde fenêtre** : Ici, ça devient un peu plus urgent. Il convient d'informer l'user du peu de temps qu'il lui reste.<br>
Il faut également lui rappeler de sauvegarder ses données.


**Texte de la fenêtre de fermeture** : L'user ne pourra plus sauvegarder ses données. Il est temps, ici, de le remercier d'avoir utilisé le point Cuyber de la mairie.<br>A noter que l'user ne peut avoir aucun interaction avec cette fenêtre.


**Important** : Vous pouvez utiliser les variables {session}, {avertissement}, {avertissement2} et {fermeture} dans les zones de textes.<br>
Ces variables seront automatiquement remplacées par leur valeur numéraire.

*{session}* : Sera remplacée par la durée totale de la session.<br>
*{avertissement}* : Sera remplacée par le temps entre le premier popup et la fin de la session.<br>
*{avertissement2}* : Sera remplacée par le temps entre le second popup et la fin de la session.<br>
*{fermeture}* : Sera remplacée par la durée d'affichage de la fenêtre plein écran. 
