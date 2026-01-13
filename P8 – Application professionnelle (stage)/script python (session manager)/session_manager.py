from tkinter import Tk, Label, Button, StringVar, LEFT, BOTTOM, messagebox
import json
import time
import threading
import subprocess

def charger_configuration():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        messagebox.showerror("Erreur", "Fichier de configuration introuvable. Vérifiez que le fichier 'config.json' existe.")
        return None
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier de configuration : {e}")
        return None

def fermer_popup(fenetre):
    fenetre.destroy()

def remplacer_variables(texte, config):
    texte = texte.replace("%avertissement", str(config["temps"]["avertissement"] + config["temps"]["final"]))
    texte = texte.replace("%final", str(config["temps"]["final"]))
    texte = texte.replace("%session", str(config["temps"]["session"] + config["temps"]["avertissement"] + config["temps"]["final"]))
    texte = texte.replace("\\n", "\n")
    return texte

def afficher_popup(titre, texte, largeur, hauteur, police, taille_police, config):
    texte_popup = remplacer_variables(texte, config)
    fenetre = Tk()
    fenetre.title(titre)

    texte_variable = StringVar()
    texte_variable.set(texte_popup)

    etiquette = Label(fenetre, textvariable=texte_variable, font=(police, taille_police), justify=LEFT, padx=2, pady=2, wraplength=largeur-40)
    etiquette.pack(fill="both", expand=True)

    taille_police_bouton = config["popup"]["taille_police"]
    police_bouton = config["popup"]["police"]
    bouton_bas = Button(fenetre, text="J'ai compris", command=lambda: fermer_popup(fenetre), font=(police_bouton, taille_police_bouton))
    bouton_bas.pack(side=BOTTOM, pady=10)

    nouvelle_hauteur = hauteur + bouton_bas.winfo_reqheight()
    fenetre.geometry(f"{largeur}x{nouvelle_hauteur}")

    fenetre.update_idletasks()
    fenetre_width = fenetre.winfo_width()
    fenetre_height = fenetre.winfo_height()
    x_position = (fenetre.winfo_screenwidth() - fenetre_width) // 2
    y_position = (fenetre.winfo_screenheight() - fenetre_height) // 2
    fenetre.geometry(f"{fenetre_width}x{fenetre_height}+{x_position}+{y_position}")

    # Fermer automatiquement le popup après un certain délai (par exemple, 20 secondes)
    fenetre.after(20000, lambda: fermer_popup(fenetre))
    fenetre.protocol("WM_DELETE_WINDOW", lambda: fermer_popup(fenetre))

    fenetre.mainloop()  # Ajoutez cette ligne pour afficher la fenêtre et attendre que l'utilisateur la ferme

def session_manager():
    config = charger_configuration()

    if config is None:
        return

    try:
        afficher_popup(config["titres"]["avertissement"], config["textes"]["avertissement"],
                       config["popup"]["largeur"], config["popup"]["hauteur"],
                       config["popup"]["police"], config["popup"]["taille_police"], config)

        # Attendre le temps de session
        time.sleep(config["temps"]["session"] * 60)

        afficher_popup(config["titres"]["avertissement_2"], config["textes"]["avertissement_2"],
                       config["popup"]["largeur"], config["popup"]["hauteur"],
                       config["popup"]["police"], config["popup"]["taille_police"], config)

        # Attendre le temps d'avertissement
        time.sleep(config["temps"]["avertissement"] * 60)

        afficher_popup(config["titres"]["avertissement_3"], config["textes"]["avertissement_3"],
                       config["popup"]["largeur"], config["popup"]["hauteur"],
                       config["popup"]["police"], config["popup"]["taille_police"], config)

        # Attendre le temps final
        time.sleep(config["temps"]["final"] * 60)

        if config["choix"] == "Déconnecter":
            subprocess.run(["logoff"])
        elif config["choix"] == "Verrouiller":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}.")

# Lancer le gestionnaire de session
session_manager()
