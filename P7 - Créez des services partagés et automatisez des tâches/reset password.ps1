<#
Script de réinitialisation de mot de passe pour AD-DS

Auteur : Mickael Faivre
Version 0.1a
Date de création : 01/10/2023
#>



<#

# Vous pouvez modifier les variables suivantes afin de personnaliser le fonctionnement du script

#>

# Nom du fichier de log
$logName = "reset password.log"

# Répertoire du fichier de log. Par défaut, il sera dans le même répertoire que le script
# La syntaxe du répertoire doit être sous la forme C:\my\dir
$logDir = ""

# Mot de passe généré par défaut de façon aléatoire
$randomPwd = $true

# Réactiver la session de l'utilisateur
$reactivateSession = $true

# L'utilisateur doit redéfinir un mot de passe quand il se reconnectera à sa session
$changeOnConnect = $true

# Longueur des mot de passe générés aléatoirement
# Attention, la longueur doit correspondre à la PSO du serveur 
$pwdLength = 14

# Chaîne de caractère utilisée pour la génération de mot de passe aléatoires
# (Dans le doute, ne changez rien)
$pwdChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+[]{}|;:'<>,.?/"






<#

A partir de là, on ne touche plus à rien !

#>

$admin = $env:USERNAME


# Si $logDir est vide (par défaut), on la définir comme étant le répertoire courant du script
if (-not $logDir) {
    $logDir = $PSScriptRoot
}


# Chemin complet du fichier de log
if ($logName -eq $null -or -not $logName) {
    $scriptName = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)
    $logName = "$scriptName.log"
}
$logPath = Join-Path -Path $logDir -ChildPath $logName



# Si le répertoire du $logDir n'existe pas, on le créé
# New-Item est attribué à une variable afin de ne pas afficher la création du dossier dans le script
if (-not (Test-Path $logDir -PathType Container)) {
   $createDir = New-Item -Path $logDir -ItemType Directory -Force
}


# Si le fichier de log n'existe pas, on le créé
if (-not (Test-Path $logPath)) {
    $createFile = New-Item -Path $logPath -ItemType File -Force
}






# Fonction d'écriture dans le fichier log
function Write-Log {

    # On vérifie et défini les paramètres
    param (
        [Parameter(Position=0, Mandatory)]
        [ValidateSet("INFO","WARNING","ERROR")]
        [string]$Level = "INFO",

        [Parameter(Position=1, Mandatory)]
        [string]$Value
    )
  
    $timeStamp = [System.DateTime]::Now.ToString("dd-MM-yyyy HH:mm:ss") #Timestamp 

    # On écrit dans le fichier log en fonction des paramètres donnés
    Add-Content -Path $logPath -Value "[$timeStamp] [$Level] $Value" 
}





# Fonction principale du script qui permet d'entrer un utilisateur
function Get-MainMenu {
    $user = Read-Host "Veuillez entrer l'identifiant ou le nom complet de l'utilisateur concerné"

    # Si la chaîne contient un espace au milieu, on considère que c'est un DisplayName
    if ($user -match '\S\s\S') {
        $fullName = Get-ADUser -Filter { DisplayName -eq $user }

        # On fait une recherche par DisplayName et on retourne le résultat
        if ($fullName -ne $null) {

        # Si le DisplayName retourne quelque chose, c'est qu'une correspondance a été trouvée, alors on envoie vers la fonction Set-Options et on enregistre le log
            Write-Host "`nUtilisateur trouvé via le DisplayName : $fullName"
            Write-Log -Level INFO -Value "Recherche d'un user via le DisplayName ($user). Résultat trouvé : $fullName"
            Set-Options -UserAD $fullName
        }
        else {

        # Si aucune correspondance n'a été trouvée, on affiche l'erreur, on log et on boucle sur la fonction
            Write-Host "`nAucun utilisateur n'a été trouvé avec le DisplayName $user ..."
            Write-Log -Level ERROR -Value "Recherche d'un user via le DisplayName ($user). Aucun résultat."
            Get-MainMenu
        }
    }

    # Si le chaîne ne contient pas d'espace mais contient des lettres, un point, puis des lettres et/ou des numéros, alors on considère que c'est un ident
    elseif ($user -match '^[a-zA-Z]+\.[a-zA-Z0-9]+$') {
        $ident = Get-ADUser -Filter {SAMAccountName -eq $user -or userPrincipalName -eq $user}

        # On fait une recherche par ident, et on retourne le résultat
        if ($ident -ne $null) {

        # Si une correspondance est trouvée, on la retourne puis on envoie vers la fonction Set-Options et on log
            Write-Host "`nUtilisateur trouvé via l'ident : $ident"
            Write-Log -Level INFO -Value "Recherche d'un user via l'ident ($user). Résutat trouvé : $ident"
            Set-Options -UserAD $ident
        }
        else {

        # Si aucune correspondance, on boucle sur la fonction Get-MainMenu et on log
            Write-Host "`nAucun utilisateur n'a été trouvé avec l'identifiant $user ..."
            Write-Log -Level ERROR -Value "Recherche d'un user via l'ident ($user). Aucun résultat."
            Get-MainMenu
        }
    }

    # Si la chaîne donnée ne correspond à rien d'utilisable pour AD, on boucle sur Get-MainMenu et on log
    else {
        Write-Host "Le format ne correspond pas à celui attendu."
        Write-Host "L'identidiant doit avoir le format 'un.login' ou 'Prénom Nom'"
        Write-Log -Level ERROR -Value "Format d'utilisateur incorrect. Réinitialisation du script..."
        Get-MainMenu
    }
}






<# 
 Fonction qui permet à l'utilisateur du script de définir les paramètres manuellement ou d'utiliser la configuration du script
 Les options sont :
 - Mot de passe aléatoire ou saisi manuellement ?
 - L'utilisateur sur lequel on modifie le mot de passe doit-il en changer lorsqu'il se reconnectera à sa session ?
 - Doit-on réactiver le compte (si le compte a été bloqué suite à de trop nombreux mot de passe erronés) ? 
#>
function Set-Options {

    # La fonction doit être appelée avec le paramètre -UserAD $value qui corrrespond au retour que l'AD a fait lors de la fonction Get-MainMenu
    param (
        [Parameter(Position=0, Mandatory)]
        [string]$UserAD
    )

    # On fait une petite réécriture des variables personnalisables pour les rendre plus lisibles ($true devient Activé, $false devient Désactivé)
    $VrandomPwd = @({Désactivé},{Activé})[$randomPwd]
    $VchangeOnConnect = @({Désactivé},{Activé})[$changeOnConnect]
    $VreactivateSession = @({Désactivé},{Activé})[$reactivateSession]

    #On boucle tant que l'user n'a pas fait un choix qui rentre dans les valeurs attendues
    do {

        # Si l'user a fait un choix incorrect, on le précise
        if ($choixParam -ne $null -and $choixParam -notin (1,2)) {
            Write-Host "`nSeules les options 1 et 2 sont disponibles. Veuillez réessayer ...`n"
        }

        # On affiche les options disponibles et leurs états
        Write-Host "`nLes paramètres du script ont les valeurs suivantes :"
        Write-Host "- Mot de passe défini aléatoirement : $VrandomPwd"
        Write-Host "- Session de l'utilisateur réactivée : $VreactivateSession"
        Write-Host "- Doit changer de mot de passe lors de la prochaine connexion à sa session : $VchangeOnConnect"
        $choixParam = Read-Host "`nVoulez-vous poursuivre avec les paramètres actuels [1] ou modifier ces paramètres [2]"
    }

    # La boucle pour être sûr que les valeurs sont 1 ou 2
    while ($choixParam -notin (1,2))

    # Si aucun motif n'est défini, on en demande un (pour le log)
    do {
        $motif = Read-Host "`nVeuillez préciser le motif justifiant le changement de mot de passe"
    }
    while (-not $motif)


    # Si l'user choisi 1, alors on lance la procédure automatique
    if ($choixParam -eq 1) {

        # On appelle les différentes fonctions
        $newPwd = Reset-Pwd -Mode $randomPwd
        $session = Set-Session $UserAD -Mode $reactivateSession
        $change = Change-OnConnect -UserAD $UserAD -Mode $changeOnConnect

        # On appelle la fonction qui se charge de tenter les modifications

        Try-Change -pwd $newPwd -session $session -change $change -UserAD $UserAD -Motif $motif

    }
    # Si l'user choisi 2, alors on lui demande les valeurs qu'il souhaite utiliser
    else {

        # Gestion de l'option Reset-Pwd
        do {
            if ($choixPwd -and $choixPwd -notin (1,2)) {
                Write-Host "Seules les options 1 et 2 sont disponibles. Veuillez réessayer..."
            }
            $choixPwd = Read-Host "`nSouhaitez-vous définir le nouveau mot de passe manuellement [1] ou le générer aléatoirement [2] ?"
        }
        while ($choixPwd -notin (1,2))
        if ($choixPwd -eq 1) {
            $newPwd = Reset-Pwd -Mode $false
        }
        elseif ($choixPwd -eq 2) {
            $newPwd = Reset-Pwd -Mode $true
        }
        
        # Gestion de l'option Set-Session
        do {
            if ($choixSessionUp -and $choixSessionUp -notin ("O","N")) {
                Write-Host "Seules les options O et N sont disponibles. Veuillez réessayer..."
            }
            $choixSession = Read-Host "`nSouhaitez-vous dévérouiller la session de l'utilisateur ? [O/N]"
            $choixSessionUp = $choixSession.ToUpper()
        }

        while ($choixSessionUp -notin ("N","O"))
        if ($choixSessionUp -eq "N") {
            $session = Set-Session -UserAD $UserAD -Mode $false
        }
        if ($choixSessionUp -eq "O") {
            $session = Set-Session -UserAD $UserAD -Mode $true
        }

        # Gestion de l'option Change-OnConnect
        do {
            if ($choixChangeUp -and $choixChangeUp -notin ("N","O")) {
                Write-Host "Seules les options O et N sont disponibles. Veuillez réessayer..."
            }
            $choixChange = Read-Host "`nSouhaitez-vous que l'utilisateur change de mot passe à sa prochaine connexion ? [O/N]"
            $choixChangeUp = $choixChange.ToUpper()
        }
        while ($choixChangeUp -notin ("N","O"))
        if ($choixChangeUp -eq "N") {
            $change = Change-OnConnect -UserAD $UserAD -Mode $false
        }
        if ($choixChangeUp -eq "O") {
            $change = Change-OnConnect -UserAD $UserAD -Mode $true
        }

        # On appelle la fonction qui tente les modifications
        Try-Change -pwd $newPwd -session $session -change $change -UserAD $UserAD -Motif $motif

    }
}




<#
Fonction de réinitialisation du mot de passe.
L'appel de la fonction se fait ainsi : Reset-Pwd -Mode $true/false
#>
function Reset-Pwd {

    param (
        [Parameter(Position=0, Mandatory)]
        [bool]$Mode
    )

    # Si la var randomPwd est sur true, alors on génère un passe aléatoire 
    if ($Mode) {
        
        # On récupère les caractères utilisés qu'on met sous forme de tableau
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
        return [PSCustomObject]@{
            Pwd = $pwd
            Info = "Nouveau mot de passe généré aléatoirement : $pwd"
            Log = "Nouveau mot de passe généré aléatoirement."
        }
    }

    # Sinon on demande à l'user de définir un nouveau mot de passe
    else {
        Write-Host "`nVous devez définir un nouveau mot de passe pour $UserAD.`nCe mot de passe doit faire plus de $pwdLength caractères de long."

        # On boucle sur la demande de mot de passe tant que les deux entrées ne correspondent pas
        do {
            if ($plainNewPwd -ne $plainConfPwd) {
                Write-Host "Les mots de passe ne correspondent pas. Veuillez réessayer..."
            }
            if ($plainNewPwd -and $plainNewPwd.Length -lt $pwdLength) {
                Write-Host "Le mot de passe doit faire plus de $pwdLength caractères de long..."
            }
            # On ouvre un popup sécurisé pour la demande de passe
            $newPwd = Read-Host "Nouveau mot de passe" -AsSecureString
            $confirmPwd = Read-Host "Confirmer le nouveau mot de passe" -AsSecureString

            # On remet les pass en texte pour pouvoir les comparer
            $credNewPwd = New-Object System.Management.Automation.PSCredential("Username", $newPwd)
            $plainNewPwd = $credNewPwd.GetNetworkCredential().Password
            $credConfPwd = New-Object System.Management.Automation.PSCredential("Username", $confirmPwd)
            $plainConfPwd = $credConfPwd.GetNetworkCredential().Password

        }
        while (-not $plainNewPwd -or $plainNewPwd.Length -lt $pwdLength)

        # On retourne le mot de passe
        return [PSCustomObject]@{
            Pwd = $plainNewPwd
            Info = "Nouveau mot de passe généré manuellement."
            Log = "Nouveau mot de passe généré manuellement."
        }
    }
}





# Fonction qui gère l'option du dévérouillage de compte
function Set-Session {

    param (
        [Parameter(Position=0, Mandatory)]
        [string]$UserAD,

        [Parameter(Position=1, Mandatory)]
        [bool]$Mode

    )

    # Si, dans les paramètres du script, l'user a mis le déblocage de session par défaut, alors on regarde si la session est verouillée
    if ($Mode) {
        $userProp = Get-ADUser -Filter {SamAccountName -eq $UserAD} -Properties *
        if ($userProp | Get-ADUser | Select-Object -ExpandProperty "LockedOut") {

            $cmd = "Unlock-ADAccount -Identity `"$UserAD`""
            $info = "Le compte Active Directory a été dévérouillé."
        }

        # Si le compte n'était pas verouillé, on le précise
        else {
            $cmd = $null
            $info = "Le compte Actice Directory n'était pas vérouillé."
        }
    }

    # Si le compte ne devait pas être deverouillé, on le précise aussi
    else {
        $cmd = $null
        $info = "Le compte Active Directory n'a pas été dévérouillé."
    }
    return [PSCustomObject]@{
        Command = $cmd
        Info = $info
    }
}






# Fonction pour la gestion du nouveau mot de passe
# Si l'user du script le souhaite, il peut forcer l'user AD à changer de mot de passe quand il se reconnectera à sa session
function Change-OnConnect {
    
    param (
        [Parameter(Position=0, Mandatory)]
        [string]$UserAD,

        [Parameter(Position=1, Mandatory)]
        [bool]$Mode
    )
    # Si $changeOnConnect est sur true, alors on save la cmd dans  un tableau. 
    # De la même façon que la fonction précédente
    if ($Mode) {
        $cmd = "Set-ADUser -Identity `"$UserAD`" -ChangePasswordAtLogon"+' $true'
        $info = "L'utilisateur devra modifier son mot de passe à la prochaine connexion."
    }
    # Si on ne l'user AD ne doit pas changer le pass, alors on le précise
    else {
        $cmd = $null
        $info = "Le mot de passe ne sera pas modifié à la prochaine connexion de l'utilisateur."
    }
    return [PSCustomObject]@{
        Command = $cmd
        Info = $info
    }
}




# Fonction appelée pour envoyer les commandes AD
# Il faut que l'ensemble des requêtes ne rencontrent pas d'erreur pour que les modifications soient prises en compte
function Try-Change {

    param (
        [Parameter(Position=0, Mandatory)]
        [PsCustomObject]$pwd,

        [Parameter(Position=1, Mandatory)]
        [PSCustomObject]$session,

        [Parameter(Position=2, Mandatory)]
        [PSCustomObject]$change,

        [Parameter(Position=3, Mandatory)]
        [string]$UserAD,

        [Parameter(Position=4, Mandatory)]
        [string]$Motif
    )

    try {
        # On sécurise les données pour la commande AD
        $newPwd = $pwd.Pwd 
        $secPwd = ConvertTo-SecureString -String $newPwd -AsPlainText -Force
        Set-ADAccountPassword -Identity $UserAD -NewPassword $secPwd -Reset

        # Si le passe a pu être modifié, on passe au dévérouillage de la session
        try {
            if ($session.Command) {
                iex $session.Command
            }
            # Si la session a été gérée, on passe à la gestion du mot de passe à la reconnexion de la session
            try {
                if ($change.Command) {
                    iex $change.Command
                }
            }

            # Puis on gère les eventuelles erreurs...
            # Ici, la gestion du passe à la reconnexion de session
            catch {
                Write-Host "Une erreur s'est présentée lors de la configuration du changement de mot de passe à la reconnexion."
                Write-Host $_
                Write-Log -Level ERROR -Value "Le script a rencontré une erreur lors de la configuration du changement de mot de passe à la connexion..."
                Write-Log -Level ERROR -Value $_
                Write-Log -Level INFO -Value "Réinitialisation du script..."
                Get-MainMenu
            }
        }
        # Puis le dévérouillage du compte
        catch {
            Write-Host "Une erreur s'est présentée lors du dévérouillage du compte..."
            Write-Host $_
            Write-Log -Level ERROR -Value "Le script a rencontré une erreur lors du dévérouillage du compte..."
            Write-Log -Level ERROR -Value $_
            Write-Log -Level INFO -Value "Réinitialisation du script..."
            Get-MainMenu
        }    
    }
    # Puis au changement de mot de passe
    catch {
        Write-Host "Une erreur s'est présentée lors du changement de mot de passe..."
        Write-Host $_
        Write-Log -Level ERROR -Value "Active Directory a rencontré une erreur..."
        Write-Log -Level ERROR -Value $_
        Write-Log -Level INFO -Value "Réinitialisation du script..."
        Get-MainMenu
    }

    # Le retour prompt pour savoir ce qu'à fait le script
    Write-Host "`nRésumé des actions effectuées pour le compte $user :`n"
    Write-Host $pwd.Info
    Write-Host $session.Info
    Write-Host $change.Info

    # Et les logs 
    Write-Log -Level INFO -Value "$admin vient d'effectuer les actions suivantes pour le compte $user :"
    Write-Log -Level INFO -Value "Motif donné : $Motif"
    Write-Log -Level INFO -Value $pwd.Log
    Write-Log -Level INFO -Value $session.Info
    Write-Log -Level INFO -Value $change.Info

    # On renvoie vers Get-MainMenu
    Get-MainMenu
}

# Ici, on retrouve l'appel à la fonction qui sera executée au lancement du script
# Et le log qui va avec



# On enregistre, dans les logs, l'éxucution du script
Write-Log -Level INFO -Value "Exécution de $script par $admin"

# On lance la fonction du menu principal
Get-MainMenu
