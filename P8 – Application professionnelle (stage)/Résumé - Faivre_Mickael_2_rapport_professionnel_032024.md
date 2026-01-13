# Rapport de Stage - Technicien Informatique (Collectivité Territoriale)

Ce dépôt contient la synthèse technique de mon stage de fin d'études (Technicien Informatique), effectué au sein de la Direction des Systèmes d'Information (DSI) d'une collectivité territoriale de ~7000 habitants.

## 📋 Contexte de la mission
**Environnement :** Mairie et services annexes (~50 postes, 3 sites interconnectés).
**Durée :** 3 mois (Décembre 2023 - Février 2024).
**Objectif :** Support utilisateur, administration système et participation à la rénovation de l'infrastructure réseau.

## 🛠️ Réalisations techniques majeures

### 1. Développement & Automatisation (Python/Qt)
Développement de **"Session Manager"**, une application GUI pour la gestion du "Point Cyber" (Espace Public Numérique).
* **Problématique :** Gestion manuelle chronophage des temps de connexion et des statistiques d'usage.
* **Solution :**
    * Interface graphique avec **PyQt6** (Qt Designer).
    * Gestion automatisée des sessions (déconnexion automatique, popups d'avertissement).
    * Collecte de données statistiques conformes RGPD (export Excel automatique).
    * Compilation en `.exe` autonome (via PyInstaller) pour déploiement sans dépendances.
    * [Lien vers le dépôt du code source](https://github.com/m-faivre) *(Note : Mettez ici le lien vers le repo du code si vous l'avez mis sur GitHub, sinon supprimez cette ligne)*.

### 2. Infrastructure & Réseau
Participation active à la rénovation du câblage et du réseau de deux salles (130m² et 70m²).
* **Câblage :** Brassage de baies informatiques, sertissage RJ45 (Norme T568B).
* **Architecture :**
    * Mise en place d'un sous-réseau dédié (VLAN) pour le Wi-Fi public.
    * Configuration d'un routeur Wi-Fi indépendant pour la salle du conseil (segmentation du réseau LAN/Invité).
    * Installation de Switchs L3 et routeurs.

### 3. Administration Système (Windows Server / Linux)
* **Audit Active Directory :** Analyse de la structure existante et proposition d'une refonte **AGDLP** (Account, Global, Domain Local, Permissions) pour sécuriser les partages de fichiers.
* **Serveur d'impression (Linux) :** Déploiement d'un serveur **CUPS** sous Debian pour pallier les limitations de partage d'imprimante Windows (erreur 0x00000709).
* **Virtualisation :** Mise en place d'un environnement de maquettage sous **Proxmox VE** (Cluster, HA, Debian/Windows Server).

### 4. Cybersécurité & RGPD
* Proposition de déploiement de **KeePass** via GPO pour renforcer la politique de mots de passe.
* Sensibilisation aux bonnes pratiques (verrouillage de session, nettoyage des navigateurs).

---

## 🔒 Note de confidentialité

> **Le rapport complet (50+ pages) détaille l'architecture interne, les plans d'adressage IP et les politiques de sécurité spécifiques de la collectivité.**
>
> Par souci de confidentialité et de sécurité ("Security by Design"), ce document n'est pas publié en libre accès sur ce dépôt. Il est consultable **uniquement sur demande** dans le cadre d'un processus de recrutement.

---
*Mots-clés : Administration Système, Python, Réseau, Active Directory, Proxmox, CUPS, RGPD, Collectivité.*
