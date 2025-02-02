![Logo](./icons/icon-128.png?raw=true "Logo de l'application")

# SaisieMesAbs

Outil de saisie des mesures du champ magnétique terrestre par la méthode des résidus.

![Capture d'écran de l'application](./Screen.png?raw=true "Capture d'écran de l'application")

**⚠ Ce script n'est ni approuvé par l'IPEV, ni par l'EOST. Leurs logos sont utilisés à titre d'exemple.**

## Fonctionnalités

- **Autocomplétion intelligente des angles et des horaires** : Les heures de mesure et les angles sont automatiquement calculés 💡
- **Configuration rapide** : Le nom de la station et les ordres de grandeur des angles sont configurables pour une prise en main encore plus rapide 🚀
- **Compatible CLI** : Vous pouvez le lancer avec des paramètres spécifiques (date, configuration, etc.) 💻

## Installation

SaisieMesAbs utilise `briefcase` de BeeWare, ce qui permet de compiler facilement un script Python avec interface.

Afin de garantir la compatibilité avec votre système, vous devrez compiler le script vous-même (mais ce n'est pas compliqué !).

> Un package `.deb` est disponible uniquement pour **ubuntu noble (amd64)**.

1. **Cloner le projet** :

    ```bash
    git clone https://github.com/Onion2222/SaisieMesAbs
    cd SaisieMesAbs
    ```

2. **Créer un environnement virtuel** :

    ```bash
    python -m venv venv
    source ./venv/bin/activate
    ```

3. **Installer briefcase** :

    ```bash
    pip install briefcase
    ```

4. **Construire l'application** :

    ```bash
    briefcase build --update
    ```

    L'application sera disponible dans `./build/saisiemesabs/<distribution>/<version>/saisiemesabs-x.y.z/usr/bin/saisiemesabs`

5. **Distribuer l'application** :

    Si vous souhaitez une version `.deb` plus simple à installer :
    ```bash
    briefcase package
    ```
    Le package sera disponible dans `./dist` et sera uniquement compatible avec la version de votre OS

## Configuration

Lors de votre première utilisation, vous devez configurer la station. Pour cela, cliquez sur `Configuration` dans la barre de menu en haut à gauche, puis sélectionnez `Éditer`.

> L'éditeur de fichier `.txt` par défaut de votre système sera utilisé. Si cela ne vous convient pas, vous pouvez spécifier un éditeur avec l'argument `--editeur=gedit` (exemple pour `gedit`).
>
> Si vous n'arrivez pas à utiliser un éditeur adéquat, vous pouvez entrer votre configuration directement dans ce fichier : `~/.local/share/SaisieMesAbs/configuration.txt`

### Exemple de configuration

```ini
[STATION]

# Nom de la station en minuscules
NOM_STATION     = PAF

# Chemin où enregistrer les mesures
# - $YY sera remplacé par les deux derniers chiffres de l'année de la mesure
# - $STATION par le nom de la station en minuscules
PATH_RE         = /home/$STATION/$STATION$YY/mes-abs/mes-jour

# Azimuth de la cible
AZIMUTH_REPERE  = 52.35840

[AUTOCOMPLETE]
AUTO_INC_ANGLE      = 123.----
AUTO_DEC_ANGLE      = 233.----
AUTO_CAL_ANGLE_HAUT = 247.75--
AUTO_CAL_ANGLE_BAS  = 47.75--
SEC_ENTRE_MESURES   = 45
SEC_ENTRE_ETAPES    = 70

# N'oubliez pas de relancer l'application !
```

## Utilisation

La prise en main est très simple. Pour gagner du temps, vous pouvez naviguer avec la touche `TAB` 🚀.

Vous pouvez lancer l'application avec différents paramètres de démarrage. N'hésitez pas à utiliser l'argument `-h` pour en savoir plus !

---

Made in **KER72@TAAF** 🇹🇫

By **Arthur Perrin** 🐧
