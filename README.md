# SaisieMesAbs
Outil de saisie des mesures du champs magnétique terrestre par la méthode des résidus.

# Prérequis
Pour Linux:
* `python3`
* `python3-env` (seulement dans le cas de l'utilisation d'un environnement virtuel)


# Installation
__Pour Linux:__

_Avec environnement virtuel:_
```
git clone https://github.com/Onion2222/SaisieMesAbs
cd ./SaisieMesabs
python3 -m venv env
source env/bin/activate
pip install pyside6
```
_Sans environnement virtuel:_
```
git clone https://github.com/Onion2222/SaisieMesAbs
cd ./SaisieMesabs
pip install pyside6
```

# Execution
__Selon votre path:__
```
./main.py [-nv] [-d jj/mm/aa]
```
```
python3 ./main.py [-nv] [-d jj/mm/aa]
```
* `-nv` désactive le mode verbose
* `-d` permet d'entrer une date au format dd/mm/aa

# Modification des ressources
Si vous souhaitez ajouter des ressources (images, text, etc.), notez leur chemin dans `./ressources/ressources.qrc` et executez `./ressources/updateRessources.sh`

Les fichiers se retrouveront alors dans le module `./ressources.py`

# Generation d'une release
__Pour Linux:__

Prérequis:
* `pyinstaller`

Depuis la racine du projet, executez `./create_release.sh`

Vous trouverez l'executable standalone dans `./dist/SaisieMesAbs`

---
Made in KER72@TAAF 🇹🇫

By Arthur Perrin