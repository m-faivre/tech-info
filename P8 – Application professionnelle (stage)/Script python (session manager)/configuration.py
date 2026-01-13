import os
import json
from tkinter import Tk, Entry, Text, Label, Button, ttk, font, Frame, messagebox

def charger_configuration():
    try:
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)

        entry_titre_avertissement.insert(0, config_data["titres"]["avertissement"])
        entry_titre_avertissement_2.insert(0, config_data["titres"]["avertissement_2"])
        entry_titre_avertissement_3.insert(0, config_data["titres"]["avertissement_3"])

        text_titre_avertissement.delete("1.0", "end")
        text_titre_avertissement.insert("1.0", config_data["textes"]["avertissement"].replace("\\n", "\n"))

        text_titre_avertissement_2.delete("1.0", "end")
        text_titre_avertissement_2.insert("1.0", config_data["textes"]["avertissement_2"].replace("\\n", "\n"))

        text_titre_avertissement_3.delete("1.0", "end")
        text_titre_avertissement_3.insert("1.0", config_data["textes"]["avertissement_3"].replace("\\n", "\n"))


        entry_largeur_popup.insert(0, config_data["popup"]["largeur"])
        entry_hauteur_popup.insert(0, config_data["popup"]["hauteur"])
        combo_police_popup.set(config_data["popup"]["police"])
        entry_taille_police_popup.insert(0, config_data["popup"]["taille_police"])

        entry_temps_session.insert(0, config_data["temps"]["session"])
        entry_temps_avertissement.insert(0, config_data["temps"]["avertissement"])
        entry_temps_final.insert(0, config_data["temps"]["final"])

        combo_choix.set(config_data["choix"])

    except FileNotFoundError:
        messagebox.showerror("Erreur", f"Le fichier de configuration n'a pas été trouvé")
    except json.JSONDecodeError:
        messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier de configuration.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la configuration : {e}")

def enregistrer_configuration():
    try:
        config = {
            "titres": {
                "avertissement": entry_titre_avertissement.get(),
                "avertissement_2": entry_titre_avertissement_2.get(),
                "avertissement_3": entry_titre_avertissement_3.get(),
            },
            "textes": {
                "avertissement": text_titre_avertissement.get("1.0", "end-1c").replace("\n", "\\n"),
                "avertissement_2": text_titre_avertissement_2.get("1.0", "end-1c").replace("\n", "\\n"),
                "avertissement_3": text_titre_avertissement_3.get("1.0", "end-1c").replace("\n", "\\n"),
            },
            "popup": {
                "largeur": int(entry_largeur_popup.get()),
                "hauteur": int(entry_hauteur_popup.get()),
                "police": combo_police_popup.get(),
                "taille_police": int(entry_taille_police_popup.get())
            },
            "temps": {
                "session": int(entry_temps_session.get()),
                "avertissement": int(entry_temps_avertissement.get()),
                "final": int(entry_temps_final.get())
            },
            "choix": combo_choix.get(),
        }

        with open("config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)

        root.destroy()

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement de la configuration : {e}")

def afficher_aide(titre, contenu):
    aide_popup = Tk()
    aide_popup.title(titre)

    label_aide = Label(aide_popup, text=contenu, padx=10, pady=10, justify="left")
    label_aide.pack()

    bouton_fermer = Button(aide_popup, text="Fermer", command=aide_popup.destroy)
    bouton_fermer.pack(pady=10)

    aide_popup.mainloop()


# Fenêtre d'aide contextuelle
# Aide pour l'onglet titre
def afficher_aide_titres():
    titre_aide = "Aide pour l'onglet Titres"
    contenu_aide = "Cet onglet sert à définir le titre des popus qui vont s'ouvrir.\nLe titre est présent dans la barre supérieure du popup.\nPar exemple, pour ce popup, le titre est Aide pour l'onglet Titres"
    afficher_aide(titre_aide, contenu_aide)

# Aide pour l'onglet texte
def afficher_aide_textes():
    titre_aide = "Aide pour l'onglet Textes"
    contenu_aide = "Cet onglet sert à définir le texte des popus qui vont s'ouvrir.\nLe texte doit être explicite de façon à ce que l'utilisateur comprenne parfaitement ce qui va se passer.\nIl est conseillé, pour le second et le dernier popup, d'inciter l'utilisateur à sauvegarder ses données.\n\nImportant : Vous pouvez utiliser les variables %session, %avertissement et %final dans les zones de textes.\nCes variables seront automatiquement remplacées par leur valeur numéraire.\n\n%session : Sera remplacée par la durée totale de la session.\n%avertissement : Sera remplacée par le temps entre le second popup et la fermeture de la session.\n%final : Sera remplacée par le temps entre le dernier popup et la fermeture effective de la session."
    afficher_aide(titre_aide, contenu_aide)

# Aide pour l'onglet apparence
def afficher_aide_popup():
    titre_aide = "Aide pour l'onglet Apparence"
    contenu_aide = "Cet onglet sert à définir l'apparence des popups qui vont s'ouvrir.\nLa largeur et de la hauteur doivent être exprimées en pixels.\nCes données correspondent à la largeur et à la hauteur du popup qui s'affichera."
    afficher_aide(titre_aide, contenu_aide)

 # Aide pour l'onglet temps
def afficher_aide_temps():
    titre_aide = "Aide pour l'onglet Temps"
    contenu_aide = "Cet onglet sert à définir le temps de la session et le temps d'apparition des popups.\nLes temps doivent tous être exprimés en minutes.\n\nPremier timer : Délai avant l'apparition du second popup.\nSecond timer : Délai avant l'apparition du troisième popup.\nDernier timer : Délai entre l'apparition du dernier popup et de la fermeture de la session.\n\nLe temps de session est donc égal à l'ensemble des timers additionnés.\n\nExemple :\nPremier timer : 40\nSecond timer : 10\nDernier timer : 2\n\nLe temps de session totale est donc de 52 minutes."
    afficher_aide(titre_aide, contenu_aide)

# Aide pour l'onglet choix
def afficher_aide_choix():
    titre_aide = "Aide pour l'onglet Titres"
    contenu_aide = "Cet onglet sert à définir le type de fermeture de session.\nSi la session est verrouillée, alors l'utilisateur pourra retrouver les programmes ouverts.\nSi la session est déconnectée, alors tous les programmes seront fermés.\n\nAttention : Si vous choississez de verrouiller la session, il faudra la déconnecter manuellement si vous souhaitez que le manager de session se lance automatiquement."
    afficher_aide(titre_aide, contenu_aide)




if __name__ == "__main__":
    root = Tk()
    root.title("Configuration de session_manager")
    root.geometry("500x250")

    notebook = ttk.Notebook(root)

    x_position = 480
    y_position = 0


    # Onglet titres
    onglet_titres = ttk.Frame(notebook)
    notebook.add(onglet_titres, text="Titres")

    bouton_aide_titres = Button(onglet_titres, text="?", command=afficher_aide_titres)
    bouton_aide_titres.place(x=x_position, y=y_position)


    Label(onglet_titres, text="Titre du premier popup :").grid(row=1, column=0, sticky="w")
    entry_titre_avertissement = Entry(onglet_titres, width=50)
    entry_titre_avertissement.grid(row=1, column=1, padx=10, pady=5)

    Label(onglet_titres, text="Titre du second popup :").grid(row=2, column=0, sticky="w")
    entry_titre_avertissement_2 = Entry(onglet_titres, width=50)
    entry_titre_avertissement_2.grid(row=2, column=1, padx=10, pady=5)

    Label(onglet_titres, text="Titre du dernier popup :").grid(row=3, column=0, sticky="w")
    entry_titre_avertissement_3 = Entry(onglet_titres, width=50)
    entry_titre_avertissement_3.grid(row=3, column=1, padx=10, pady=5)



    # Onglet textes
    onglet_textes = ttk.Frame(notebook)
    notebook.add(onglet_textes, text="Textes")

    bouton_aide_textes = Button(onglet_textes, text="?", command=afficher_aide_textes)
    bouton_aide_textes.place(x=x_position, y=y_position)

    # Création d'un Notebook pour les sous-onglets
    sous_notebook = ttk.Notebook(onglet_textes)
    sous_notebook.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    # Sous-onglet Avertissement 1
    onglet_avertissement_1 = ttk.Frame(sous_notebook)
    sous_notebook.add(onglet_avertissement_1, text="Premier popup")

    text_titre_avertissement = Text(onglet_avertissement_1, height=5, width=54)
    text_titre_avertissement.grid(row=0, column=0, padx=10, pady=5)

    # sous-onglet Avertissement 2
    onglet_avertissement_2 = ttk.Frame(sous_notebook)
    sous_notebook.add(onglet_avertissement_2, text="Second popup")

    text_titre_avertissement_2 = Text(onglet_avertissement_2, height=5, width=54)
    text_titre_avertissement_2.grid(row=0, column=0, padx=10, pady=5)

    # sous-onglet Avertissement 3
    onglet_avertissement_3 = ttk.Frame(sous_notebook)
    sous_notebook.add(onglet_avertissement_3, text="Dernier popup")

    text_titre_avertissement_3 = Text(onglet_avertissement_3, height=5, width=54)
    text_titre_avertissement_3.grid(row=0, column=0, padx=10, pady=5)




    # Onglet apparence
    onglet_popup = ttk.Frame(notebook)
    notebook.add(onglet_popup, text="Apparence")

    bouton_aide_popup = Button(onglet_popup, text="?", command=afficher_aide_popup)
    bouton_aide_popup.place(x=x_position, y=y_position)

    # Colonnes pour les éléments de configuration
    label_largeur_popup = Label(onglet_popup, text="Largeur du popup:")
    label_largeur_popup.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    entry_largeur_popup = Entry(onglet_popup)
    entry_largeur_popup.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    label_hauteur_popup = Label(onglet_popup, text="Hauteur du popup:")
    label_hauteur_popup.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    entry_hauteur_popup = Entry(onglet_popup)
    entry_hauteur_popup.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    label_police_popup = Label(onglet_popup, text="Police de caractère :")
    label_police_popup.grid(row=3, column=0, padx=10, pady=5, sticky="w")

    polices_disponibles = font.families()
    combo_police_popup = ttk.Combobox(onglet_popup, values=polices_disponibles, width=15)
    combo_police_popup.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    label_taille_police_popup = Label(onglet_popup, text="Taille de la police:")
    label_taille_police_popup.grid(row=4, column=0, padx=10, pady=5, sticky="w")

    entry_taille_police_popup = Entry(onglet_popup)
    entry_taille_police_popup.grid(row=4, column=1, padx=10, pady=5, sticky="w")



    # Onglet Temps
    onglet_temps = ttk.Frame(notebook)
    notebook.add(onglet_temps, text="Temps")

    bouton_aide_temps = Button(onglet_temps, text="?", command=afficher_aide_temps)
    bouton_aide_temps.place(x=x_position, y=y_position)


    Label(onglet_temps, text="Premier timer :").grid(row=0, column=0, sticky="w")
    entry_temps_session = Entry(onglet_temps)
    entry_temps_session.grid(row=0, column=1, padx=10, pady=5)

    Label(onglet_temps, text="Second timer :").grid(row=1, column=0, sticky="w")
    entry_temps_avertissement = Entry(onglet_temps)
    entry_temps_avertissement.grid(row=1, column=1, padx=10, pady=5)

    Label(onglet_temps, text="Dernier timer :").grid(row=2, column=0, sticky="w")
    entry_temps_final = Entry(onglet_temps)
    entry_temps_final.grid(row=2, column=1, padx=10, pady=5)


    # Onglet choix 
    onglet_choix = ttk.Frame(notebook)
    notebook.add(onglet_choix, text="Choix")

    bouton_aide_choix = Button(onglet_choix, text="?", command=afficher_aide_choix)
    bouton_aide_choix.place(x=x_position, y=y_position)

    Label(onglet_choix, text="Choix de fermeture de session :").grid(row=0, column=0, sticky="w")
    combo_choix = ttk.Combobox(onglet_choix, values=["Verrouiller", "Déconnecter"], width=15)
    combo_choix.grid(row=0, column=1, padx=10, pady=5)

    button_frame = Frame(root)
    button_frame.pack(side="bottom", pady=10)




    def enregistrer_callback():
        try:
            enregistrer_configuration()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la configuration : {e}")

    def annuler_callback():
        try:
            root.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'annulation : {e}")

    Button(button_frame, text="Enregistrer", command=enregistrer_callback).grid(row=0, column=0, padx=30)
    Button(button_frame, text="Annuler", command=annuler_callback).grid(row=0, column=1, padx=5)

    notebook.pack(expand=1, fill="both")

    if os.path.exists("config.json"):
        charger_configuration()

    root.protocol("WM_DELETE_WINDOW", enregistrer_callback)
    root.mainloop()

