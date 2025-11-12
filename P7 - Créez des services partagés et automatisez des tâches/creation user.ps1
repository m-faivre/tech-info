<#
Script de création d'utilisateur pour Active-Directory

Auteur : Mickaël Faivre
Version : 0.1b
Date de création : 01/10/2023

Patchnotes :

0.1b :
- Correction de fautes de français
- Correction de bugs mineurs
- Optimisation du script

0.1a :
- Création du script

#>


<#



Pour configurer le script, vous pouvez modifier les variables suivantes



#>


# Domaine dans l'active directory
$domain = "axeplane.loc"

# Unité Organisationnelle globale 
$globalOU = "Axeplane_Services"

# Nom de la PSO
$PSOName = "PSO_GG"

# Préfixe des groupes globaux
$prefixGG = "GG_"

# Lettre du lecteur sur lequel sera mappé le partage personnel
$driveLetter = "P:"

# Répertoire où sont ajoutés les dossiers privés pour le partage personnel
$sharedFolder = "E:\Partages personnels\"


# Caractères utilisés dans la génération des mots de passe
$pwdChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+[]{}|;:'<>,.?/"






<#

-- A PARTIR DE LA, NE TOUCHEZ A RIEN --

#>





# On récupère les infos de la PSO
$PSO = Get-ADFineGrainedPasswordPolicy -Identity $PSOName

# Puis on récupère la longueur minimale du mot de passe de cette PSO
$pwdLength = ($PSO.MinPasswordLength)



# Fonction d'affichage du menu principal

function Get-MainMenu {
    # Si le texte entré n'a pas le format "un texte", on boucle
    do {
        if ($userAD -notmatch '\S\s\S') {
            Write-Host "Le nom d'utilisateur doit avoir la forme suivante : Prénom Nom"
        }
        $userAD = Read-Host "`nVeuillez entrer le nom et prénom de l'utilsateur [Prénom Nom]"
    }
    while ($userAD -notmatch '\S\s\S')

    # On utilise la fonction Check-ADUser pour vérifier si un user ayant le nom donné existe déjà
    $checkUser = Check-ADUser -User $userAD
    if ($checkUser) {
        Write-Host "`nCet utilisateur existe déjà dans Active Directory :"
        Write-Host $checkUser
        Get-MainMenu
    }

    # Si aucun user n'existe, on continu
    else {
        
        # On génère automatiquement un login sous la forme Prénom Nom -> p.nom
        $genLoginAD = Generate-Login -FullName $userAD

        # On propose soit de garder le login généré, soit d'en définir un autre
        do {
            Write-Host "`nLe script a généré automatiquement un identifiant pour cet utilisateur : $genLoginAD"
            $loginChoice = Read-Host "Voulez-vous garder cet identifiant [O] ou en entrer un manuellement [N] ?"
        }
        while ($loginChoice -inotin ("o","n"))
        if ($loginChoice -ieq "n") {
            # On boucle tant que le login n'a pas le bon format
            do {
                if ($loginAD -notmatch '^[a-zA-Z]+\.[a-zA-Z0-9]+$') {
                    Write-Host "L'identifiant doit avoir le format suivant : un.login"
                }
                $loginAD = Read-Host "Veuillez entrer un identifiant pour $userAD"
            }
            while ($loginAD -and $loginAD -notmatch '^[a-zA-Z]+\.[a-zA-Z0-9]+$')
        }
        # Sinon on prend le nouveau login donné par l'user du script
        else {
            $loginAD = $genLoginAD
        }

        # On passe à la gestion du mot de passe de l'user
        # On propose soit de définir un passe maintenant, soit de laisser l'user le définir lui même à sa connexion
        do {
            Write-Host "`nVous pouvez définir un mot de passe aléatoire que l'utilisateur devra changer à sa prochaine connexion."
            $pwdChoice = Read-Host "Voulez-vous que le mot de passe soit changé par l'utilisateur à sa prochaine connexion [O/N] ?"
        }
        while ($pwdChoice -inotin ("o","n"))
        #Si on laisse l'user choisir son pass, on défini quand même un pass aléatoire pour la requête New-ADUser
        if ($pwdChoice -ieq "o") {
            $pwd = Generate-Pwd
            $change = $true
        }
        else {
            $change = $false
            # On propose une génération automatique du passe ou une saisie manuelle
            do {
                $pwdGen = Read-Host "`nVoulez-vous générer un mot de passe aléatoire [O] ou définir un mot de passe manuellement [N] ?"
            }
            while ($pwdGen -inotin("o","n"))
            # En cas de saisie manuelle, on vérifie que la validité du mot de passe
            if ($pwdGen -ieq "n") {
                do {
                    if ($plainPwd -ne $plainConfPwd) {
                        Write-Host "Les mots de passe ne correspondent pas. Veuillez réessayer..."
                    }
                    elseif ($tryPwd -ne $null -and $tryPwd -eq $false) {
                        Write-Host "Le mot de passe ne respecte pas la PSO du serveur. Veuillez réessayer..."
                    }
                    $pwd = Read-Host "`nVeuillez saisir le mot de passe pour $userAD" -AsSecureString
                    $confirmPwd = Read-Host "Veuillez confirmer le mot de passe" -AsSecureString
                    $credPwd = New-Object System.Management.Automation.PSCredential("Username", $pwd)
                    $plainPwd = $credPwd.GetNetworkCredential().Password
                    $credConfPwd = New-Object System.Management.Automation.PSCredential("Username", $confirmPwd)
                    $plainConfPwd = $credConfPwd.GetNetworkCredential().Password

                    $tryPwd = Check-Pwd -pwd $plainPwd
                }
                while ($pwd -eq $null -or $plainPwd -ne $plainConfPwd -or $tryPwd -eq $false)
                $pwd = $plainPwd
            }
            # Sinon on génére un passe aléatoire
            else {
                $pwd = Generate-Pwd
                Write-Host "Nouveau mot de passe pour $userAD : $pwd"
            }
        }

        # On passe à la gestion des services

        # On créé un tableau pour enregistrer la liste des services existants
        $OUTable = @()
        $domainSplit = $domain.Split('.')
        $searchBase = "OU=$globalOU,DC=$($domainSplit[0]),DC=$($domainSplit[1])"
        $OUList = Get-ADOrganizationalUnit -Filter * -SearchBase $searchBase
        $i = 0
        foreach ($OU in $OUList) {
            $i++
            if ($i -eq 1) { continue }
            $OUTable += $($OU.Name)
        }

        do {
            Write-Host "`nLes Unités Organisationnelles existantes sont les suivantes :"
            foreach ($elem in $OUTable) {
                Write-Host $elem
            }
            $service = Read-Host "`nDans quel service (UO) voulez-vous ajouter l'utilisateur $userAD ?"
        }
        # On boucle tant que l'user du script n'a pas défini de service

        while ($OUTable -inotcontains $service)
        if ($OUTable -icontains $service) {
            $globalGroup = $prefixGG + $service
            Write-Host "$userAD sera également ajouté au groupe de sécurité global $globalGroup."

            # Et maintenant l'activation du compte
            do {
                $active = Read-Host "`nSouhaitez-vous que ce compte soit activé [O/N] ?"
            }
            while ($active -inotin("o","n"))
            if ($active -ieq "o") {
                $active = $true
                Write-Host "Le compte $userAD sera activé une fois sa création terminée."
            }
            else {
                $active = $false
                Write-Host "Le compte $userAD ne sera pas activé une fois sa création terminée."
            }
         # Puis on gère la description du compte
        $description = Read-Host "`nQuelle description souhaitez-vous ajouter au compte ?"
        if (!$description) { $description = "Aucune description ajoutée lors de la création du compte." }

        # On envoie la fonction de création d'utilisateur
        $addUser = Add-ADUser -user $userAD -login $loginAD -pwd $pwd -service $service -active $active -change $change -description $description
        Write-Host $addUser
        Get-MainMenu
        }
    }
}




# Fonction pour générer le login de l'user
# Cette fonction permet d'être sûr que le login de l'user sera unique
function Generate-Login {
    param (
        [Parameter(Position=0, Mandatory)]
        [string]$FullName
    )

    # On divise le nom complet en parties distinctes
    $nameParts = $FullName -split '\s+'

    # On obtient la première lettre du prénom et le nom
    $firstNameInitial = $nameParts[0].Substring(0, 1)
    $lastName = $nameParts[-1]

    # On forme le login en utilisant la première lettre du prénom et le nom
    $login = $firstNameInitial + '.' + $lastName
    $login = $login.ToLower()
    $checkUser = Get-ADUser -Filter {SamAccountName -eq $login}

    # On créer un samaccountname unique par incrémentation s'il en existe déjà un identique
    $i = 1
    while ($checkUser -ne $null) {
        $login = $login + $i
        $checkUser = Get-ADUser -Filter {SamAccountName -eq $login}
        $i++
    }

    return $login
}





# Fonction pour générer un mot de passe aléatoire
function Generate-Pwd {
    $charSet = $pwdChar.ToCharArray()
 
    # On utilise la méthode RNGCryptoServiceProvider pour avoir quelque chose de sécurisé
    $rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
    $bytes = New-Object byte[]($pwdLength)
  
    $rng.GetBytes($bytes)
  
     $newPwd = New-Object char[]($pwdLength)
    
     # On boucle sur la longueur désirée pour avoir un mot de passe qui correspond à $pwdLenght
    for ($i = 0 ; $i -lt $pwdLength ; $i++) {
        $newPwd[$i] = $charSet[$bytes[$i]%$charSet.Length]
    }

    # On retourne le nouveau mot de passe généré
    $pwd = -join $newPwd
    return $pwd
}





# Fonction de vérification de l'user
function Check-ADUser {
    param (
        [Parameter(Position=0, Mandatory)]
        [string]$User
    )
    # On envoie une requête pour savoir si l'user ayant le DisplayName $User existe
    $filter = "DisplayName -eq '$User'"
    $checkUser = Get-ADUser -Filter $filter -ErrorAction SilentlyContinue

    # Si la var $checkUser existe, alors que c'est que l'user existe
    # Dans ce cas on retourne le nom pour l'afficher
    if ($checkUser) {
        return $checkUser
    }

}





# Fonction ajout utilisateur
function Add-ADUser {
    param (
        [string]$user,
        [string]$pwd,
        [string]$login,
        [string]$service,
        [bool]$active,
        [bool]$change,
        [string]$description
    )

    $return = ""
    # On split la var du domain pour en extraire soit le nom, soit l'extension
    $domainSplit = $domain.Split('.')
    # Idem avec la var $name afin d'avoir soit le prénom, soit le nom
    $name = $user.Split(' ')
    # On incrémente le préfixe des groupes globaux au nom du service
    $globalGroup = $prefixGG + $service

    try {
        # On envoie notre requête de création d'user

        New-ADUser -Name $user `
                   -DisplayName $user `
                   -GivenName $name[0] `
                   -Surname $name[1] `
                   -SamAccountName $login `
                   -UserPrincipalName "$login@$domain" `
                   -EmailAddress "$login@$domain" `
                   -Path "OU=$service,OU=$globalOU,DC=$($domainSplit[0]),DC=$($domainSplit[1])" `
                   -Enabled $active `
                   -ChangePasswordAtLogon $change `
                   -AccountPassword (ConvertTo-SecureString -String $pwd -AsPlainText -Force) `
                   -Description $description 

        # On ajoute l'user au groupe global concerné
        Add-ADGroupMember -Identity $globalGroup -Members $login

        # On gère nos variables pour avoir un affichage plus compréhensible
        # Et on remercie powershell5 de ne pas avoir d'opérateur ternaire
        $change = @({Désactivé},{Activé})[$change]
        $active = @({Désactivé},{Activé})[$active]

        # On prépare un retour mis en page pour savoir ce qui a été fait et donner les détails à l'admin
        $return += "`nL'utilisateur $user a bien été ajouté à Active-Directory`n
        Résumé de la création :
        - Nom complet : $user
        - Nom d'affichage : $user
        - Prénom : $($name[0])
        - Nom : $($name[1])
        - Identifiant : $login
        - Adresse e-mail : $login@$domain
        - Service : $service
        - Groupe de sécurité global : $globalGroup
        - Mot de passe : $pwd
        - Changement de mot de passe à la connexion : $change
        - Compte activé : $active
        - Description : $description"


        try {

            # On défini les chemins
            $dir = "$sharedFolder$login$"

            # On créé le dossier
            $null = New-Item -Path $dir -ItemType Directory
            # On crée le partage
            New-SmbShare -Name "$login$" -Path $dir -FullAccess "$login@$domain" | Out-Null
            # On supprime les droits NTFS hérités
            $null = icacls $dir /inheritance:d /C /Q 2>&1
            # On supprime les droits NTFS du groupe "Utilisateurs"
            $null = icacls $dir /remove[:g] Utilisateurs 2>&1
            # On accorde les droits NTFS totaux à l'user
            $null = icacls $dir /grant "${login}:(OI)(CI)F" 2>&1
            # On ajoute le dossier mon.user$ comme répertoire de base de l'user 
            Set-ADUser -Identity $login -HomeDrive $driveLetter -HomeDirectory "\\$env:COMPUTERNAME\$login$"

        }

        # Capture des erreurs lors de la création du dossier personnel
        catch {
            $return += "`nUne erreur est survenue lors de la création du dossier personnel...`n$_"
        }
    }
    # Capture des erreurs lors de la création de l'user
    catch {
        $return += "`nUne erreur est survenue lors de la création de l'utilisateur...`n$_"
    }
    return $return
        
}





# Fonction de vérification du mot de passe via la PSO
function Check-Pwd {
    param(
        [Parameter(Position=0, Mandatory)]
        [string]$pwd
    )


    # Si la longueur est inférieure à celle donnée par la PSO, on refuse le passe
    if ($pwd.Length -lt $pwdLength) {
        return $false
    }

    # On défini les critères de complexité avec des classes Unicode
    $upperCase = "\p{Lu}"  # Lettres majuscules
    $lowerCase = "\p{Ll}"  # Lettres minuscules
    $digits = "\p{Nd}"     # Chiffres
    $specialChars = "\p{P}" # Caractères spéciaux

    # On incrémente un compteur à chaque fois que le mot de passe rempli une condition
    # De façon à savoir si le passe contient des majuscules ET des minuscules ET des chiffres ET des caractères spéciaux
    # Si le total est inférieur à trois, on refuse le passe car il ne respecte pas les critères de complexité basique d'une PSO
    $count = 0
    if ($pwd -match $upperCase) { $count++ }
    if ($pwd -match $lowerCase) { $count++ }
    if ($pwd -match $digits) { $count++ }
    if ($pwd -match $specialChars) { $count++ }

    # On compare donc notre valeur totale à celle requise
    if ($count -ge 3) {
        return $true
    }
    else {
        return $false
    }
}


<#

-- Activation du script en lançant la fonction du menu principal

#>
#Clear-Host
Get-MainMenu
