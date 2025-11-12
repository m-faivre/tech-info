# 🧩 Projet de formation – Migration Windows

## 📘 Description du projet

Vous êtes **technicien supérieur systèmes et réseaux** au service informatique de l’entreprise **Axe Plane**, spécialisée dans la fabrication de pièces mécaniques pour l’aviation.  
L’entreprise compte environ **150 salariés** utilisant principalement **Linux Ubuntu 18.04 / 20.04**, et quelques postes sous Windows.  

Afin de disposer d’un parc plus récent et homogène, la direction a décidé de migrer l’ensemble des postes clients vers **Windows**.  
Vous êtes mobilisé sur ce chantier, et votre première journée débute par une réunion avec :
- **Anthony Pacaut**, responsable du service informatique  
- **Aaron Scott**, administrateur systèmes et réseaux  

Au cours de cette réunion, vous échangez sur les **modifications à apporter à l’infrastructure** et sur les **outils d’administration** à automatiser.

---

## ⚙️ Scripts développés

### 🧱 1. `creation user.ps1`
**Objectif :** automatiser la création d’un utilisateur Active Directory complet.

#### ✨ Fonctionnalités principales
- Création d’un **compte utilisateur AD** avec :
  - login généré automatiquement (`p.nom`) ou saisi manuellement  
  - mot de passe saisi ou généré aléatoirement (conforme à la PSO du domaine)
  - options d’activation du compte et de changement de mot de passe à la première connexion
- Rattachement au **groupe global** du service
- Création et partage du **dossier personnel** sur le serveur de fichiers
  - Partage caché (`\\serveur\login$`)
  - Droits NTFS configurés : contrôle total accordé uniquement à l’utilisateur
- Attribution du **lecteur réseau** (`P:`) dans les attributs AD

#### 🔐 Points techniques
- Utilise le module **ActiveDirectory** de PowerShell
- Vérifie les **droits** et l’**unicité** du login
- Génération de mot de passe via un **RNG sécurisé**
- Validation de la **complexité** selon la **PSO** (Password Settings Object)
- Affichage d’un **récapitulatif** détaillé après création

#### ⚠️ Limites / améliorations possibles
- Compatibilité partielle avec les systèmes en anglais (libellé “Utilisateurs” dans les ACL)
- Nécessite que les OU et groupes globaux existent déjà
- Possible extension : journalisation, mode non interactif, normalisation des accents

---

### 🔁 2. `reset password.ps1`
**Objectif :** automatiser la réinitialisation du mot de passe d’un utilisateur AD.

#### ✨ Fonctionnalités principales
- Recherche d’un utilisateur par **DisplayName** (“Prénom Nom”) ou identifiant (`p.nom`)
- Réinitialisation du mot de passe avec :
  - mot de passe **généré aléatoirement** ou **saisi manuellement**
  - option pour **déverrouiller le compte**
  - option pour **forcer le changement à la prochaine connexion**
- Journalisation complète des actions effectuées (fonction `Write-Log`)

#### 🔐 Points techniques
- Module **ActiveDirectory**
- Logs détaillés horodatés (`reset password.log`)
- Mot de passe géré en **SecureString**
- Options configurables en début de script :
  - génération automatique, longueur, caractères, déverrouillage, etc.

#### ⚠️ Limites / améliorations possibles
- Recherche par nom sensible à la casse et aux formats de `DisplayName`
- Pas de rotation de logs
- Le mot de passe généré est affiché une fois (bonne pratique : le transmettre via un canal sécurisé)

---

## 📄 Conclusion

Ces deux scripts PowerShell illustrent la mise en œuvre d’outils d’administration simples et robustes pour un environnement Active Directory :
- **standardisation** des comptes utilisateurs,  
- **sécurisation** des opérations courantes,  
- **gain de temps** pour les techniciens systèmes.

Ils s’inscrivent dans le cadre du projet de migration Windows d’Axe Plane, mené dans la formation **Technicien Informatique (RNCP niv.5 – Bac+2)**.

---

## 🧰 Technologies utilisées
- **Windows Server / Active Directory**
- **PowerShell 5+**
- **RSAT – Remote Server Administration Tools**
- **SMB / NTFS ACL**

---

## 👤 Auteur
Projet réalisé dans le cadre de la formation **Technicien Informatique** – OpenClassrooms  
Tous les scripts sont fournis à titre **démonstratif (code figé)**.
