""" Widget customisé
"""

import re
from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap, Qt

# pylint: disable= invalid-name

heure_re = re.compile(r"^(([01]\d|2[0-3])([0-5]\d)|24:00)([0-5]\d)$")
angle_re = re.compile(r"^(?:[0-3]*[0-9]{1,2}|400)(?:\.[0-9]{4,})$")
mesure_re = re.compile(r"^(?:-*[0-9]+)(?:\.[0-9]{1})$")
date_re = re.compile(r"^\d{2}\/\d{2}\/\d{2}$")


def date_add_seconds(date: str, sec: int) -> str:
    """Additionne une horaire au format hhmmss à un nombre de seconde

    Args:
        date (str): Horaire format hhmmss
        sec (int): Nombre de secondes à ajouter à l'horaire

    Returns:
        str: horaire au format hhmmss
    """
    # Découpe du string d'entrée
    hour = int(date[0:2])
    minute = int(date[2:4])
    second = int(date[4:6])
    # Ajout des secondes
    newSecond = second + sec
    # Récupération des minutes supplémentaires
    newMinute = minute + int(newSecond / 60)
    # Récupération des heures supplémentaires
    newHour = hour + int(newMinute / 60)
    # Recalcule des secondes/minutes/heures
    newSecond %= 60
    newMinute %= 60
    newHour %= 24
    # Renvoie de l'horaire hhmmss
    return (str(newHour).zfill(2) +
            str(newMinute).zfill(2) +
            str(newSecond).zfill(2))


class Logo(QtWidgets.QLabel):
    """ Logo a taille fixe
    """
    def __init__(self, path: str, maxHeight: int) -> None:
        """Génération d'un label pour afficher un logo

        Args:
            path (str): Chemin du logo
            maxHeight (int): Hauteur maximale
        """
        super().__init__()
        # pourquoi ? Parce que ça marche mieux avec -20...
        self.setFixedHeight(
            maxHeight - 20
        )
        logo = QPixmap(path).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(logo)
        self.setMask(logo.mask())


class SaisieDate(QtWidgets.QLineEdit):
    """ Champs d'edition de la date
    """
    def __init__(self) -> None:
        """QtWidgets.QLineEdit pour la saisie d'une date"""
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(150)
        self.setInputMask("99/99/99")


class MyLineEdit(QtWidgets.QLineEdit):
    """ Champs d'édition abstraite
    """
    def __init__(self, text: str) -> None:
        """ QtWidgets.QLineEdit à ma sauce pour l'inscription de
            l'heure/angle/mesure

        Args:
            text (str): Texte initial
        """
        # Variable indiquant si la valeur a été modifiée par l'utilisateur
        self.editedByHand = False
        super().__init__()
        # Text initial
        self.initext = text
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
        # Action en cas de clique de souris
        self.mousePressEvent = self.press
        self.setFixedWidth(150)
        # Lorsque due la valeur est editée
        self.textEdited.connect(
            self.edited
        )
        # Action en cas de fin d'édition
        self.editingFinished.connect(self.changed)
        self.regexValidator = re.compile(r"")

    def validatepls(self) -> None:
        """ Emet un son lorsqu'il y a une erreur d'input
        """
        if not self.hasAcceptableInput():
            # Ne fonctionne pas sur toutes les plateformes
            QtWidgets.QApplication.beep()

    def press(self, o) -> None:
        """ Lors du clique de la souris, efface le text d'indication

        Args:
            o (?): Non utilisé
        """
        if self.text() == self.initext:
            self.setText("")

    def edited(self) -> None:
        """ Appelé lors d'une edition d'origine humaine
        """
        self.editedByHand = True
        if self.text() != '-':
            self.validatepls()

    def setText(self, text: str, force=False) -> None:
        """Change le texte s'il n'a pas été modifié par l'homme

        Args:
            text (str): nouveau texte
            force (bool, optional): force l'edition. Defaults to False.
        """
        if not self.editedByHand or force:
            super().setText(text)

    def changed(self) -> None:
        """ Si la saisie est modifié, verifie si la saisie est valide
            Sinon emet un beep"""
        self.rewrite()
        if not self.isValid():
            # Ne fonctionne pas sur toute les plateformes
            QtWidgets.QApplication.beep()

    def rewrite(self) -> None:
        """ Pour heritage
        """
        return

    def isStrange(self) -> None:
        """ Pour heritage

        Returns:
            bool: False
        """
        return False

    def isValid(self, color_notvalid: bool = True) -> bool:
        """ Verifie si la saisie est valide à partir d'un regex

        Returns:
            bool: Saisie valide ou non
        """
        # La valeur est elle acceptable ?
        if (self.hasAcceptableInput() and
                self.regexValidator.match(self.text())):
            # Oui
            # Est-elle hors tolérance ?
            if self.isStrange():
                # Oui -> Orange
                self.setStyleSheet("color: orange")
            else:
                # Non -> Vert
                self.setStyleSheet("color: green;")
            return True
        # La valeur n'est pas valide
        # Rouge
        if color_notvalid:
            self.setStyleSheet("color: red;")
        return False


class SaisieHeure(MyLineEdit):
    """ Champs de saisie heure hhmmss hérité de MyLineEdit
    """

    def __init__(self, textInit: str = "hhmmss") -> None:
        """ MyLineEdit pour saisir une heure

        Args:
            textInit (str, optional): Text initiale. Defaults to "hhmmss".
        """
        super().__init__(textInit)
        self.setMaxLength(6)
        # Regex de validation d'heure format hhmmss
        self.regexValidator = heure_re


class SaisieAngle(MyLineEdit):
    """ Champs de saisie d'angle hérité de MyLineEdit
    """
    def __init__(self, textInit: str = "---.----") -> None:
        """MyLineEdit pour la saisie d'angle gradiant"""
        super().__init__(textInit)
        self.setMaxLength(len(textInit))
        # Regex de validation d'angle
        self.regexValidator = angle_re
        # Action en cas d'édition
        self.selectionChanged.connect(self.changeSelection)

    def changeSelection(self) -> None:
        """ Permet la selection intelligente des données préremplies
        """
        # Si tout le text est selectionné
        if self.selectionLength() == len(self.text()):
            # Selection uniquement des "--" initialisé
            start = self.initext.find("-")
            stop = len(self.text())
            if start > stop:
                return
            self.setSelection(
                start, stop
            )

    def rewrite(self) -> None:
        """ Permet de reecrire la cellule dans le bon format
            (ex: ajout des 0 manquants pour avoir 4 decimals)
        """
        try:
            self.setText("%.4f" % ((float(self.text()))), True)
            self.update()
        except ValueError:
            pass


class SaisieMesure(MyLineEdit):
    """ Champs de saisie de mesure hérité de MyLineEdit
    """
    def __init__(self, textInit: str = "--.-") -> None:
        """ MyLineEdit pour la saisi d'une mesure en nT
        """
        super().__init__(textInit)
        # Regex de validation des mesure
        self.regexValidator = mesure_re

    def rewrite(self) -> None:
        """ rewrite() permet de reecrire la celule dans le bon format
            (ex: ajout des 0 manquants pour avoir 1 decimal)
        """
        try:
            self.setText("%.1f" % (float(self.text())), True)
            self.update()
        except ValueError:
            return
        return

    def isStrange(self) -> bool:
        """ Override de isStrange() du parent, fournit un detecteur de saisie
            anormale

        Returns:
            bool: True si valeur anormale
        """
        return abs(float(self.text())) >= 10


class CalibrationAzimuth(QtWidgets.QGroupBox):

    def __init__(self, numVisee: int, autoValue: dict) -> None:
        """ Layout pour la saisie des angle de visé de la cible

        Args:
            numVisee (int): Numéro de la visée (1 ou 2)
            autoValue (dict): Valeur d'angle pour l'autocompletion
        """
        super().__init__()
        # Titre
        self.setTitle("Visée d'ouverture " + str(numVisee))

        # Définition du layout
        self.layoutCal = QtWidgets.QFormLayout()
        # Définition des labels
        self.indVH = QtWidgets.QLabel("V" + str(numVisee) + " sonde en haut")
        self.indVB = QtWidgets.QLabel("V" + str(numVisee) + " sonde en bas")
        # Définition de la saisie des angles
        self.angleVH = SaisieAngle(autoValue["haut"])
        self.angleVB = SaisieAngle(autoValue["bas"])
        # Création du layout
        self.layoutCal.addRow(self.indVH, self.angleVH)
        self.layoutCal.addRow(self.indVB, self.angleVB)
        self.setLayout(self.layoutCal)
        self.setFixedWidth(500)

        # Mise en place des triggers
        self.angleVH.textChanged.connect(
            lambda: self.updateAngle(self.angleVH.text()))
        self.angleVH.textEdited.connect(self.stopUpdate)

        self.updatable = True  # Autcompletion activé

    def updateAngle(self, angle: str) -> None:
        """autocomplet le deuxieme angle de visée (sonde en bas)

        Args:
            angle (str): angle de visée sonde en haut
        """
        try:
            if angle != "" and not self.angleVB.editedByHand:
                self.angleVB.setText("%.4f" % ((float(angle) + 200) % 400))
        except ValueError:
            pass

    def stopUpdate(self) -> None:
        """Désactive l'autocomplétion"""
        self.updatable = False

    def getAzi(self) -> None:
        """Retourne les données saisis

        Returns:
            tuple (str, str): angles de visé
        """
        return self.angleVH.text(), self.angleVB.text()

    def validate(self) -> None:
        """Valide les angles saisies

        Returns:
            bool: Angles valides ou nom
        """
        return self.angleVB.isValid() & self.angleVH.isValid()


class Mesure(QtWidgets.QGroupBox):

    def __init__(self, titre: str, nomMesure: str, typeMesure: str,
                 autoValueAngle: dict, autoValueSec: int) -> None:
        """Widget des mesure d'inclinaison et de declinaison

        Args:
            titre (str): Nom de la mesure
            nomMesure (str): Nom de la mesure pour transfert des datas
            typeMesure (str): inclinaison ou declinaison
            autoValueAngle (dict): Valeur d'angle pour l'autocompletion
            autoValueSec (int): Temps estimé entre deux mesures pour
                                l'autocompletion
        """
        super().__init__()
        # Definition d'un titre
        self.setTitle(titre)
        # Définition du type de mesure
        self.typeMesure = typeMesure
        # Définition du nom de la mesure (pour la sauvegarde)
        self.nomMesure = nomMesure
        # Définition du lapse de temps auto entre les mesures
        self.autoValueSec = autoValueSec
        # Définition d'un' layout
        self.layoutMesurePr = QtWidgets.QGridLayout()
        # S'il s'agit d'une mesure d'inclinaison alors permettre la saisie de
        # l'est magnétique
        if self.typeMesure == "inclinaison":
            self.indAngleEst = QtWidgets.QLabel("Est magnétique")
            self.indAngleEst.setAlignment(Qt.AlignCenter)
            self.angleEst = SaisieAngle(autoValueAngle["dec"])
            self.layoutMesurePr.addWidget(self.indAngleEst, 0, 1)
            self.layoutMesurePr.addWidget(self.angleEst, 1, 1)
        else:
            # Création de vide pour la symmétrie esthetique
            self.indSpace1 = QtWidgets.QLabel("")
            self.indSpace2 = QtWidgets.QLabel("")
            self.layoutMesurePr.addWidget(self.indSpace1, 0, 1)
            self.layoutMesurePr.addWidget(self.indSpace2, 1, 1)
        # Definition des indication et des cases de saisie en haut des colonnes
        self.indHeure = QtWidgets.QLabel("HEURE")
        self.indHeure.setAlignment(Qt.AlignCenter)
        self.indAngle = QtWidgets.QLabel("ANGLE")
        self.indAngle.setAlignment(Qt.AlignCenter)
        self.indMesure = QtWidgets.QLabel("MESURE (nT)")
        self.indMesure.setAlignment(Qt.AlignCenter)
        self.layoutMesurePr.addWidget(self.indHeure, 2, 1)
        self.layoutMesurePr.addWidget(self.indAngle, 2, 2)
        self.layoutMesurePr.addWidget(self.indMesure, 2, 3)
        # Definition de la liste des 4 ligne de mesures
        self.ligne = []
        # Création des lignes de mesure
        # self.ligne=[{'label':...,'heure':'hhmmss','angle':'--.----','mesure':'-x.x'},...]
        for i in range(4):
            heure = SaisieHeure()
            mesure = SaisieMesure()
            # S'il s'agit de la premiere mesure d'angle
            if i == 0:
                # S'il s'agit d'une mesure d'inclinaison
                if self.typeMesure == "inclinaison":
                    angle = SaisieAngle(autoValueAngle["inc"])
                else:
                    angle = SaisieAngle(autoValueAngle["dec"])
            else:
                angle = SaisieAngle()

            numero = QtWidgets.QLabel(str(i + 1))
            self.ligne.append(
                {"label": numero,
                 "heure": heure,
                 "angle": angle,
                 "mesure": mesure}
            )
            self.layoutMesurePr.addWidget(self.ligne[i]["label"], 3 + i, 0)
            self.layoutMesurePr.addWidget(self.ligne[i]["heure"], 3 + i, 1)
            self.layoutMesurePr.addWidget(self.ligne[i]["angle"], 3 + i, 2)
            self.layoutMesurePr.addWidget(self.ligne[i]["mesure"], 3 + i, 3)
        # Fonctions pour autocomplete
        self.ligne[0]["heure"].editingFinished.connect(
            lambda: self.updateHeure(0))
        self.ligne[1]["heure"].editingFinished.connect(
            lambda: self.updateHeure(1))
        self.ligne[2]["heure"].editingFinished.connect(
            lambda: self.updateHeure(2))
        # lors de la modification de la valeur de l'angle de la premiere ligne
        self.ligne[0]["angle"].textEdited.connect(
            lambda: self.updateAngle(
                float(self.ligne[0]["angle"].text()), False)
        )
        # autocompletion permise
        self.stopUpdate(True)
        # Mise en place du layout
        self.setFixedWidth(500)
        self.setLayout(self.layoutMesurePr)

    def stopUpdate(self, disable: bool) -> None:
        """ Désactive/active l'autocompletion

        Args:
            disable (bool): True pour desactiver l'autocompletion
        """
        # désactive/active les cases de saisie d'angle des 3 derniere lignes
        for i in range(1, 4):
            self.ligne[i]["angle"].setDisabled(disable)
        # désactive/active la case de saisie d'est mag
        if self.typeMesure == "inclinaison":
            self.angleEst.setDisabled(disable)

    def updateHeure(self, indexLigne: int) -> None:
        """ Autocomplete pour la datation de la prochaine ligne de mesure

        Args:
            indexLigne (int): index de la ligne où l'heure a été saisie
        """
        # Si l'heure entré est valide
        if self.ligne[indexLigne]["heure"].isValid(False):
            # Récupération de l'heure entrée
            initHour = self.ligne[indexLigne]["heure"].text()
            # Calcul de l'heure de la prochaine mesure
            calculedHour = date_add_seconds(initHour, self.autoValueSec)
            # Affichage de l'heure de la prochaine mesure
            self.ligne[indexLigne + 1]["heure"].setText(calculedHour)
            # Raz des couleurs
            self.ligne[indexLigne+1]["heure"].setStyleSheet("")

    def updateAngle(self, angle: str, includeFirst: bool) -> None:
        """ Autocomplete des angles

        Args:
            angle (str): angle fourni
            includeFirst (bool): mise à jour de tous les angles ou juste des
                                 3 derniers
        """
        if includeFirst:
            self.ligne[0]["angle"].setText("%.4f" % angle)
        if self.typeMesure == "declinaison":
            self.ligne[1]["angle"].setText("%.4f" % angle)
            self.ligne[2]["angle"].setText("%.4f" % ((angle + 200) % 400))
            self.ligne[3]["angle"].setText("%.4f" % ((angle + 200) % 400))
        else:
            self.ligne[1]["angle"].setText("%.4f" % ((angle + 200) % 400))
            self.ligne[2]["angle"].setText("%.4f" % ((400 - angle) % 400))
            self.ligne[3]["angle"].setText("%.4f" % ((400 - angle - 200) % 400))
        # Raz des couleurs
        for ligne in self.ligne:
            ligne["angle"].setStyleSheet("")

    def updateEst(self, angle: str) -> None:
        """ Autocomplet la saisie de l'est magnetique

        Args:
            angle (str): angle fournit
        """
        self.angleEst.setText("%.4f" % angle)

    def getData(self) -> dict:
        """ Renvoi les mesures sous forme d'un dictionnaire

        Returns:
            dict: mesure au format:
            {
                "nom": nom de la mesure
                "est": angle (ou None),
                "mesure": {
                    [{
                        "heure": hh mm ss,
                        "angle": angle,
                        "mesure": mesure
                    },...]
                }
            }
        """
        collectionData = {"est": None, "mesures": []}
        for eLigne in self.ligne:
            newCollec = {}
            heure = eLigne["heure"].text()
            newCollec["heure"] = f"{heure[0:2]} {heure[2:4]} {heure[4:6]}"
            newCollec["angle"] = eLigne["angle"].text()
            newCollec["mesure"] = eLigne["mesure"].text()
            collectionData["mesures"].append(newCollec)
        if self.typeMesure == "inclinaison":
            collectionData["est"] = self.angleEst.text()
        collectionData["nom"] = self.nomMesure
        return collectionData

    def validate(self) -> bool:
        """ Valide l'ensemble des cases des lignes de la mesure

        Returns:
            bool: Mesures valide ou non
        """
        ligneIsValide = True
        for eLigne in self.ligne:
            ligneIsValide = (
                eLigne["heure"].isValid()
                & eLigne["angle"].isValid()
                & eLigne["mesure"].isValid()
            ) & ligneIsValide
        if self.typeMesure == "inclinaison":
            return ligneIsValide & self.angleEst.isValid()
        return ligneIsValide
