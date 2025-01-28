# SaisieMesAbs

Outil de saisie des mesures du champs magnétique terrestre par la méthode des résidus.

![Alt text](./Screen.png?raw=true "Captrue d'écran de l'application")

**⚠ Ce script est approuvé ni par l'IPEV, ni par l'EOST, leur logo sont utilisés pour exemple.**

## Fonctionnalités

- **Autocomplétion intelligente des angles et des horaires** : Les heures de mesure et les angles sont automatiquements calculé 💡
- **Configuration rapide** : Le nom de station et les ordre de grandeur des angles sont configurable pour aller encore plus vite 🚀
- **Compatible cli** : Vous pouvez le lancer avec des paramètres specifiques (date, configuration...) 💻

## Installation

SaisieMesabs utilise `briefcase` de BeeWare qui permet de compilé facilement un script python avec interface.

Afin de garantir la compatibilité sur votre systeme, vous allez devoir vous même compiler le script. (mais ce n'est pas compliqué !)

> Un package `.deb` est disponible uniquement pour **ubuntu noble (amd64)**.

1. **Cloner le projet**:
    ```bash
    git clone https://github.com/Onion2222/SaisieMesAbs
    cd SaisieMesAbs
    ```
2. **Installer un environnement virtuel**
    ```bash
    python -m venv venv
    source ./venv/bin/activate
    ```
3. **Installer briefcase**
    ```bash
    pip install briefcase
    ```
4. **Construire l'application**
    ```bash
    briefcase build
    ```
    L'application se trouvera dans `./build/saisiemesabs/<distribution>/<version>/saisiemesabs-x.y.z/usr/bin/saisiemesabs`

> Si vous souhaitez une version .deb plus simple à installer:
> ```bash
> briefcase package
> ```
> Le package se trouvera dans `./dist`


## Configuration

Lors de votre premiere utilisation il faut configurer la station. Pour cela il faut cliquer dans la barre de menu dans la partie supérieure gauche `Configuration` -> `Editer`.

> C'est l'editeur de fichier `.txt` par défaut de votre système qui est utilisé. Pensez à le configurer pour correspondre à vos besoins !

> Si vous n'arrivez pas à obtenir un editeur correct, vous pouvez entrer votre configuration ici: `~/.local/share/SaisieMesAbs/configuration.txt`

### Exemple de configuration

```ini
[STATION]

# Nom de la station en minuscule
NOM_STATION     = PAF

#PATH du chemin où enregistrer les mesures
# - $YY sera remplacé par les deux derniers chiffres de l'année de la mesure
# - $STATION par le nom de la station en minuscule
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
La prise en main est triviale. Pour être plus rapide il faut naviguer avec la touche `TAB` 🚀.

Vous pouvez lancer l'application avec différents paramètre de démarrage, n'hesitez pas à appeler l'application avec l'argument `-h` pour en savoir plus !

---

Made in **KER72@TAAF** 🇹🇫

By **Arthur Perrin** 🐧

### TODO
[ ] Arg pour choisir editeur