"""
Appication de saisie de la mesure absolue du champs magnétique
pour les îles subantarctiques
"""
# pylint: disable= invalid-name

import importlib.metadata
import configparser
from datetime import datetime
import sys
import logging
import pathlib
import argparse
import webbrowser
import subprocess
import traceback
from shutil import which

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QIcon, Qt, QAction, QShortcut, QFont

from .resources import ressources_rc
from .customwidgets import (
    Logo,
    Mesure,
    SaisieDate,
    SaisieAngle,
    CalibrationAzimuth,
    date_re
)

# Définition du logger
log = logging.getLogger(__name__)
# Niveau de log par défaut (DEBUG pour tout afficher)
log.setLevel(logging.DEBUG)
# Création d'un handler pour afficher les logs sur la sortie standard (stdout)
log_stream_handler = logging.StreamHandler(sys.stdout)
# Définition du format de sortie pour les logs
log_stream_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)8s] %(lineno)4d : %(message)s")
)
# Ajout du handler au logger
log.addHandler(log_stream_handler)
# Ajout d'un gestionnaire des erreurs innatendues
def exc_handler(exctype, value, tb):
    log.exception(''.join(traceback.format_exception(exctype, value, tb)))
sys.excepthook = exc_handler

# Variable globale de débogage, initialisée à False
DEBUG = False



class SaisieMesAbs(QtWidgets.QMainWindow):
    """ Fenêtre principale
    """

    def __init__(self, date: str,
                 metadata: dict,
                 configuration: dict,
                 pathEditor: str = None) -> None:
        super().__init__()
        # Récupération de la date de la mesure
        self.initdate = date
        # Récupération des metadata
        self.metadata = metadata
        # Récupération du fichier de configuration
        self.configuration = configuration
        # Récupération de l'editeur
        self.editeur = pathEditor
        # Initialisation de l'interface
        log.debug("Debut initialisation UI")
        self.initUi()
        log.debug("Fin initialisation UI")
        self.show()

    def initUi(self) -> None:
        """initialisation de la fenêtre principale
        """
        # Titre & Icone
        self.setWindowTitle("Enregistrement des mesures magnétiques")
        self.setWindowIcon(QIcon(':/icon.png'))
        # Définition des 4 mesure (déclinaison 1&2, inclinaison 1&2)
        # Array comprennant les 4 widgets de mesure
        self.mesure = []
        # Définition du cadre 0 sup-gauche: déclinaison 1
        self.mesure.append(
            Mesure(
                "Premières mesures de déclinaisons",
                "declinaison premiere serie",
                "declinaison",
                self.configuration["Angle"],
                self.configuration['Delai']["Etape"],
            )
        )
        # Trigger pour l'autocompletion
        # Quand l'angle de la premiere ligne est rentré:
        # Mise à jour de l'angle EST des cadres 1 et 3 (inc 1 & 2)
        # Mise à jour des angles du cadre 2 (déc 2)
        self.mesure[0].ligne[0]["angle"].textChanged.connect(
            lambda: self.updateAngleOther(0)
        )
        # Définition du cadre 1 sup-droit: inclinaison 1
        self.mesure.append(
            Mesure(
                "Premières mesures d'inclinaisons",
                "inclinaison premiere serie",
                "inclinaison",
                self.configuration["Angle"],
                self.configuration['Delai']["Etape"],
            )
        )
        # Trigger pour l'autocompletion
        # Quand l'angle de la premiere ligne est rentré:
        # Mise à jour des angles du cadre 3 (inc 2)
        self.mesure[1].ligne[0]["angle"].textChanged.connect(
            lambda: self.updateAngleOther(1)
        )
        # Définition du cadre 2 inf-gauche: déclinaison 2
        self.mesure.append(
            Mesure(
                "Deuxiemes mesures de déclinaisons",
                "declinaison deuxieme serie",
                "declinaison",
                self.configuration["Angle"],
                self.configuration['Delai']["Etape"],
            )
        )
        # Trigger pour l'autocompletion
        # Quand l'angle de la premiere ligne est rentré:
        # Mise à jour de l'angle EST de cadre 3 (inc 2)
        self.mesure[2].ligne[0]["angle"].textChanged.connect(
            lambda: self.updateAngleOther(2)
        )
        # Définition du cadre 3 inf-droit: inclinaison 2
        self.mesure.append(
            Mesure(
                "Deuxiemes mesures d'inclinaisons",
                "inclinaison deuxieme serie",
                "inclinaison",
                self.configuration["Angle"],
                self.configuration['Delai']["Etape"],
            )
        )

        # Définition des mesures d'angle des 2 visées de cible
        # Visée 1
        self.vise1 = CalibrationAzimuth(1, self.configuration["Calibration"])
        # Quand l'angle haut de la visée 1 est entré
        # MaJ de l'angle haut de la visée 2
        self.vise1.angleVH.textChanged.connect(
            self.updateCalibration
        )
        # Visée 2
        self.vise2 = CalibrationAzimuth(2, self.configuration["Calibration"])
        # GROUPE CONTEXTUEL
        # Date, Station et Azimuth repère
        self.contexte = QtWidgets.QGroupBox("Contexte")
        # Date
        self.indDate = QtWidgets.QLabel("Date")
        self.date = SaisieDate()
        self.date.setText(self.initdate)
        # Station
        self.layoutStation = QtWidgets.QFormLayout()
        self.indStation = QtWidgets.QLabel("Station")
        self.station = QtWidgets.QLineEdit(
            self.configuration["Station"].upper())
        self.station.setAlignment(Qt.AlignCenter)
        self.station.setFixedWidth(150)
        # Azimuth repère
        self.indAR = QtWidgets.QLabel("Azimuth repère")
        self.angleAR = SaisieAngle()
        self.angleAR.setText(self.configuration["Azimuth_Rep"])
        # Arrangement dans un layout
        self.layoutCon = QtWidgets.QFormLayout()
        self.layoutCon.addRow(self.indStation, self.station)
        self.layoutCon.addRow(self.indDate, self.date)
        self.layoutCon.addRow(self.indAR, self.angleAR)
        self.contexte.setLayout(self.layoutCon)
        # LOGO
        # Définition des logos
        self.logoGroup = QtWidgets.QGroupBox("Programme IPEV-EOST n°139")
        self.logoGroup.setMaximumHeight(self.contexte.sizeHint().height())
        logoEOST = Logo(":/Logo_EOST.png", self.layoutCon.sizeHint().height())
        logoIPEV = Logo(":/Logo_IPEV.png", self.layoutCon.sizeHint().height())
        # Arrangement dans un layout
        self.layoutLogo = QtWidgets.QHBoxLayout()
        self.layoutLogo.addWidget(logoEOST)
        self.layoutLogo.addWidget(logoIPEV)
        self.logoGroup.setLayout(self.layoutLogo)
        # Définition du bouton d'édition des angles calculés
        self.modifAngle = QtWidgets.QRadioButton("&Editer les angles calculés")
        # Quand cocher: activer la modification des angles
        self.modifAngle.toggled.connect(
            lambda: self.modifAngleEtatChanged(self.modifAngle)
        )
        # Définition du bouton enregistrer et de son raccourci [ctrl+s]
        self.btnEnregistrer = QtWidgets.QPushButton("Enregistrer (Ctrl+S)")
        self.btnEnregistrer.setShortcut("Ctrl+S")
        # Quand cliquer: enregistrer et quitter
        self.btnEnregistrer.clicked.connect(self.enregistrer)
        # Ctrl+Q pour quitter
        self.shortcut = QShortcut("Ctrl+Q", self)
        self.shortcut.activated.connect(self.close)
        # Création du layout principale
        self.layoutPrincipale = QtWidgets.QGridLayout()
        # Ajout des widgets dans ce layout
        self.layoutPrincipale.addWidget(self.contexte, 0, 0)
        self.layoutPrincipale.addWidget(self.logoGroup, 0, 1)
        self.layoutPrincipale.addWidget(self.vise1, 1, 0)
        self.layoutPrincipale.addWidget(self.vise2, 1, 1)
        self.layoutPrincipale.addWidget(self.mesure[0], 2, 0)
        self.layoutPrincipale.addWidget(self.mesure[1], 2, 1)
        self.layoutPrincipale.addWidget(self.mesure[2], 3, 0)
        self.layoutPrincipale.addWidget(self.mesure[3], 3, 1)
        # Ajout des deux boutons au layout principale
        self.layoutPrincipale.addWidget(self.modifAngle)
        self.layoutPrincipale.addWidget(self.btnEnregistrer)
        # Mise en place du layout principale
        self.setLayout(self.layoutPrincipale)
        # Empèche la modification de la taille de la fenêtre à la main
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        # Contenairisation du layout pour affichage dans la fenêtre
        container = QtWidgets.QWidget()
        container.setLayout(self.layoutPrincipale)
        self.setCentralWidget(container)
        # BARRE DE MENU
        self.menuBar = QtWidgets.QMenuBar()
        # - Configuration
        configuration_menu = self.menuBar.addMenu('Configuration')
        # - Configuration - Edition
        self.actionEdit = QAction(self)
        self.actionEdit.setText("Editer")
        self.actionEdit.triggered.connect(self.editConf)
        # - Configuration | Lien
        configuration_menu.addAction(self.actionEdit)
        # - Aide
        aide = self.menuBar.addMenu('Aide')
        # - Aide - Documentation
        self.actionHelp = QAction(self)
        self.actionHelp.setText("Documentation")
        self.actionHelp.triggered.connect(self.openHelp)
        # - Aide - Envoie mail
        self.actionSos = QAction(self)
        self.actionSos.setText("Mail aux devs")
        self.actionSos.triggered.connect(self.sendSOS)
        # - Aide - Information
        self.actionSos = QAction(self)
        self.actionSos.setText("Informations")
        self.actionSos.triggered.connect(self.openInformation)
        # - Aide | Lien
        aide.addAction(self.actionHelp)
        aide.addAction(self.actionSos)
        self.setMenuBar(self.menuBar)
        # Focus la premiere ligne à editer, pour etre plus rapide
        self.vise1.angleVH.setFocus()
        self.vise1.angleVH.selectAll()
        # Affichage de la fenêtre
        self.show()

    def openHelp(self) -> None:
        """ Ouvre le lien vers la documentation
        """
        log.debug("Documentation")
        webbrowser.open(self.metadata["Home-page"])

    def sendSOS(self) -> None:
        """ Ouvre une page pour ecrire un mail au dev
        """
        log.debug("SOS")
        webbrowser.open(f"mailto:{self.metadata['Author-email']}")
        
    def openInformation(self) -> None:
        PopUpCredit()

    def editConf(self) -> None:
        """ Permet d'éditer la configuration
            Si un editeur est donné en argument, l'utilise
            Sinon utilise celui pas défaut (xdg-open)
        """
        log.debug("editConf")
        if not self.editeur:
            self.editeur = '/usr/bin/xdg-open'
        subprocess.Popen([self.editeur, self.configuration["Chemin_conf"]])

    def modifAngleEtatChanged(self, btn: QtWidgets.QRadioButton) -> None:
        """ Fonction interpretée quand la case de modification des angles
            calculés est cochée

        Args:
            btn (QtWidgets.QRadioButton): Case de modification des angles
        """
        # Stopper l'autocompletion des 4 mesures
        for i in range(4):
            self.mesure[i].stopUpdate(not btn.isChecked())

    def updateAngleOther(self, numMesure: int) -> None:
        """ Ordonne la mise à jour des angles de mesure pour l'autocompletion

        Args:
            numMesure (int): index du demandeur de mise à jour
        """
        # Si les angles sont édités manuellement, on quitte la fonction
        if self.modifAngle.isChecked():
            return
        # Si l'utilisateur a entré une valeur non vide dans la mesure 1
        if numMesure == 0 and self.mesure[0].ligne[0]["angle"].isValid(False):
            # maj angle est magnetique de la mesure 2
            self.mesure[1].updateEst(
                float(self.mesure[0].ligne[0]["angle"].text())
            )
            # maj angles de la mesure 3
            self.mesure[2].updateAngle(
                float(self.mesure[0].ligne[0]["angle"].text()), True
            )
            # maj angle est magnetique de la mesure 4
            self.mesure[3].updateEst(
                float(self.mesure[0].ligne[0]["angle"].text())
            )
            return
        # maj des angles de la mesure 4 à partir de ceux de la mesure 2
        if numMesure == 1 and self.mesure[1].ligne[0]["angle"].isValid(False):
            self.mesure[3].updateAngle(
                float(self.mesure[1].ligne[0]["angle"].text()), True
            )
            return
        # maj de l'angle de l'est magnetique de la mesure 4
        # à partir de ceux de la mesure 3
        if numMesure == 2 and self.mesure[2].ligne[0]["angle"].isValid(False):
            self.mesure[3].updateEst(
                float(self.mesure[2].ligne[0]["angle"].text())
            )

    def updateCalibration(self) -> None:
        """ Met à jour les angles de la deuxième visé
            à partir de la première pour autocomplet
        """
        if self.vise2.updatable and self.vise1.angleVH.isValid(False):
            self.vise2.angleVH.setText(self.vise1.angleVH.text())

    def formatSaveData(self) -> str:
        """ Génère une sauvegarde des mesures au fromat re

        Returns:
            str: Sauvegarde formattée
        """
        tempSave = (
            f'{self.station.text().lower()} '
            f'{self.date.text().replace("/", " ")}'
            ' Methode des residus\n'
            f'visees balise\n'
            f' {self.angleAR.text()}\n'
            f'{self.vise1.getAzi()[0]} {self.vise1.getAzi()[1]}\n'
            f'{self.vise2.getAzi()[0]} {self.vise2.getAzi()[1]}\n'
        )
        for eMesure in self.mesure:
            tempSave += (f"{self.dicDataToString(eMesure.getData())}\n")
        return tempSave

    def enregistrer(self) -> None:
        """ Enregistre les données dans un fichier re et quitte l'application
        """
        # Force un reflow des widgets pour garantir un bon affichage
        self.setFocus()
        self.update()
        # Valide la saisie avant enregistrement
        if not self.validateAll():
            # Si mesure pas valide, beep
            # Ne fonctionne pas sur toutes les plateformes
            QtWidgets.QApplication.beep()
            log.warning("La mesure n'est pas valide")
            # Si pas DEBUG, ne rien faire (la mesure n'est pas valide)
            if not DEBUG:
                return
            # Si debug, avertir et passer à l'enregistrement
            log.debug("Mesure invalide, mais DEBUG activé")

        # Génération de la sauvegarde
        saveMesure = self.formatSaveData()
        log.debug(saveMesure)

        # Sauvegarde dans le fichier
        saveFilename = self.generateFileName()
        saveFile = self.generatePath() / saveFilename
        try:
            with open(saveFile, "w", encoding='utf-8') as file:
                file.write(saveMesure)
            log.info("✅ - Mesure sauvegardée sous %s", saveFile)
        except (FileNotFoundError, PermissionError) as exc:
            log.critical(
                "Erreur lors de l'enregistrement de %s: %s",
                saveFile, exc
            )
            # Tentative de sauvegarde dans le répertoire courant
            log.critical(
                "Ecriture des données dans le repertoire courant ./%s",
                saveFilename
            )
            saveFile = pathlib.Path(f"./{saveFilename}")
            with open(saveFile, "w", encoding='utf-8') as file:
                file.write(saveMesure)
            log.warning("Mesure sauvegardée sous %s", saveFile)
        # Ferme l'application après l'enregistrement
        self.close()

    def dicDataToString(self, dicData: dict) -> str:
        """ Convertit un dictionnaire de donnée en string pour l'enregistrement

        Args:
            dicData (dict): dictionnaire de donnée générer par Mesure

        Returns:
            str: string de donnée format EOST
        """
        text = ""
        if dicData['est']:
            text += f"est magnetique : {dicData['est']}\n"
        text += f"{dicData['nom']}\n"
        for dicDataMes in dicData['mesures']:
            text += (
                f"{dicDataMes['heure']}\t"
                f"{dicDataMes['angle'].rjust(8)}\t"
                f"{dicDataMes['mesure']}\n"
            )
        return text

    def validateAll(self) -> bool:
        """ Valide l'ensemble des données saisies et autocomplétés

        Returns:
            bool: True si ensemble données valide, False sinon
        """
        mesValide = self.angleAR.isValid()
        mesValide = all(eMesure.validate() for eMesure in self.mesure)
        return mesValide & self.vise1.validate() & self.vise2.validate()

    def generatePath(self) -> pathlib.Path:
        """ Génère un dossier d'enregistrement correspondant
        à la mesure

        Returns:
            pathlib.Path: path définit dans le fichier conf
        """
        return pathlib.Path(
            self.configuration["Chemin_Sauvegarde"]
            .replace("$YY", self.date.text()[6:8])
            .replace("$STATION", self.station.text().lower())
        )

    def generateFileName(self) -> str:
        """ Génère un nom de fichier correspondant à la mesure

        Returns:
            str: Nom du fichier: MMDDhhYY.STATION
        """
        arrayDate = self.date.text().split("/")
        heure = self.mesure[0].ligne[0]["heure"].text()
        return (
            f"re{arrayDate[1]}{arrayDate[0]}{heure[0:2]}{arrayDate[2]}."
            f"{self.station.text().lower()}"
        )


def is_a_date(date) -> bool:
    """Renvoie True si la date jj/mm/aa est valide

    Args:
        date (str): Date a valider au format jj/mm/aa

    Returns:
        bool: Date valide ou pas
    """
    return date_re.match(date)


def analyse_conf(chemin_fichier: pathlib.Path) -> dict:
    """ Analyse de la configuration

    Args:
        chemin_fichier (pathlib.Path): Chemin du fichier de configuration

    Raises:
        ValueError: La configuration est mauvaise

    Returns:
        dict: Renvoi les valeurs de configuration
    """
    try:
        log.info("🔍 - Analyse du fichier %s", chemin_fichier)

        # Initialisation du parser de configuration
        contentConfig = configparser.ConfigParser()
        contentConfig.read(chemin_fichier)

        # Vérification si la section "STATION" et "AUTOCOMPLETE" sont présentes
        if not contentConfig.has_section("STATION"):
            raise ValueError("La section 'STATION' est manquante dans le fichier de configuration")
        if not contentConfig.has_section("AUTOCOMPLETE"):
            raise ValueError("La section 'AUTOCOMPLETE' est manquante dans le fichier de configuration")

        # Extraction des valeurs de configuration
        configuration = {
            "Chemin_conf": chemin_fichier,
            "Station": contentConfig.get("STATION", "NOM_STATION", fallback="NA"),  # Valeur par défaut si manquante
            "Azimuth_Rep": contentConfig.get("STATION", "AZIMUTH_REPERE", fallback="---.----"),
            "Chemin_Sauvegarde": contentConfig.get("STATION", "PATH_RE", fallback="./"),
            'Angle': {
                "inc": contentConfig.get("AUTOCOMPLETE", "AUTO_INC_ANGLE", fallback="---.----"),
                "dec": contentConfig.get("AUTOCOMPLETE", "AUTO_DEC_ANGLE", fallback="---.----")
            },
            'Calibration': {
                "haut": contentConfig.get("AUTOCOMPLETE", "AUTO_CAL_ANGLE_HAUT", fallback="---.----"),
                "bas": contentConfig.get("AUTOCOMPLETE", "AUTO_CAL_ANGLE_BAS", fallback="---.----")
            },
            'Delai': {
                "Etape": contentConfig.getint("AUTOCOMPLETE", "SEC_ENTRE_MESURES", fallback=45),
                "Mesure": contentConfig.getint("AUTOCOMPLETE", "SEC_ENTRE_ETAPES", fallback=70)
            }
        }

        # Retourner la configuration sous forme de dictionnaire
        return configuration

    except (ValueError, configparser.MissingSectionHeaderError, configparser.NoOptionError) as exc:
        log.error("Le fichier de configuration %s n'est pas valide. "
                  "Erreur: %s", chemin_fichier, exc)
        raise ValueError(f"Le fichier de configuration '{chemin_fichier}' "
                         "n'est pas valide") from exc


def get_dataDir(app_name: str) -> pathlib.Path:
    """ Renvoi le dossier où stocker la configuration
        Le créé s'il n'existe pas

    Args:
        app_name (str): Nom de l'application

    Raises:
        SystemError: L'OS n'est pas compatible

    Returns:
        pathlib.Path: Dossier où stocker la configuration
    """

    home = pathlib.Path.home()

    if sys.platform == "linux":
        dataDir = home / ".local/share"
    else:
        log.critical("Plateforme inconnue ! %s", sys.platform)
        raise SystemError

    myDataDir = dataDir / app_name

    try:
        myDataDir.mkdir(parents=True, exist_ok=True)
        log.debug("Le dossier data local n'existait pas et a été créé")
    except Exception as exc:
        log.debug("Erreur lors de la création du dossier: %s", exc)
        raise
    return myDataDir


def create_default_conf(path: pathlib.Path):
    """ Créé un fichier de configuration au chemin donnée

    Args:
        path (pathlib.Path): Chemin du fichier de configuration
    """
    # Contenu par défaut pour la configuration de la station
    default_conf = (
        "[STATION]\n\n"
        "# Nom de la station en minuscules\n"
        "NOM_STATION     = NA\n\n"
        "# Chemin où enregistrer les mesures\n"
        "# - $YY sera remplacé par les deux derniers chiffres de l'année de la mesure\n"
        "# - $STATION par le nom de la station en minuscules\n"
        "PATH_RE         = /home/$STATION/$STATION$YY/mes-abs/mes-jour\n\n"
        "# Azimuth de la cible\n"
        "AZIMUTH_REPERE  = 52.35840\n\n"
        "[AUTOCOMPLETE]\n"
        "AUTO_INC_ANGLE      = 123.----\n"
        "AUTO_DEC_ANGLE      = 233.----\n"
        "AUTO_CAL_ANGLE_HAUT = 247.75--\n"
        "AUTO_CAL_ANGLE_BAS  = 47.75--\n"
        "SEC_ENTRE_MESURES   = 45\n"
        "SEC_ENTRE_ETAPES    = 70\n\n\n"
        "# N'oubliez pas de relancer l'application !\n"
    )
    with open(path, "w", encoding='utf-8') as file:
        file.write(default_conf)


def get_conf(app_name: str, conf_path: pathlib.Path = None) -> pathlib.Path:
    """ Obtenir le chemin du fichier de configuration
        Si l'application n'a pas de fichier de conf par défaut, en créer un
        Si un chemin est donné, verifier sa validité
        Sinon utiliser le chemin par défaut de l'application

    Args:
        app_name (str): Nom de l'application
        conf_path (pathlib.Path, optional): Chemin vers le fichier conf.
                                            Defaults to None.

    Returns:
        pathlib.Path: Le chemin du fichier de configuration
    """
    if not conf_path:
        log.debug("Pas de conf donné")
        conf_path = get_dataDir(app_name) / "configuration.txt"
        if not conf_path.is_file():
            log.warning(
                "Le fichier de configuration %s n'existe pas -> création",
                conf_path)
            # Création du fichier conf
            create_default_conf(conf_path)
        try:
            return analyse_conf(conf_path)
        except (KeyError, ValueError):
            log.critical("Il semble que votre configuration par "
                         "défaut soit incompatible ou corrompue.")
            log.warning("Création d'une nouvelle config")
            create_default_conf(conf_path)
            return analyse_conf(conf_path)

    # Verifier que le fichier fonctionne
    config_tocheck = configparser.ConfigParser()
    log.info("Verification du fichier de configuration")
    try:
        log.debug(conf_path.absolute())
        config_tocheck.read(conf_path.absolute())
        return analyse_conf(conf_path)

    except (ValueError, KeyError):
        log.warning("Utilisation du fichier conf par défaut")
        return get_conf(app_name, None)


class PopUpLogger(logging.Handler, QtWidgets.QDialog):

    def __init__(self):
        logging.Handler.__init__(self)
        QtWidgets.QDialog.__init__(self)
        self.setLevel(logging.WARNING)
        self.setWindowTitle("LOGGER")
        self.header = QtWidgets.QLabel("Un evenement vient de se produire")
        self.message = QtWidgets.QTextEdit()
        self.message.setMinimumWidth(600)
        self.message.setMaximumHeight(80)
        #self.message.setWordWrap(True)
        #self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.message.setFrameStyle(1)
        self.message.setFont(QFont('Monospace',10))
        #self.message.setReadOnly(True)
        self.button = QtWidgets.QPushButton("OK")
        self.button.setFixedWidth(80)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.header)
        layout.addWidget(self.message)
        layout.addWidget(self.button, alignment=QtCore.Qt.AlignRight)
        self.button.clicked.connect(lambda : QtWidgets.QDialog.close(self))

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        msg = msg.replace(":", ":\n")
        self.message.setText(msg)
        #print(f"#{type(record)}#{record}")
        self.setWindowTitle("Attention")
        self.button.setFocus()
        self.exec()
        self.activateWindow()
        
class PopUpCredit(QtWidgets.QDialog):

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle("Informations")
        self.message = QtWidgets.QLabel(
            "Créé par Arthur Perrin\n"
            "Lors de la mission KER72\n\n"
            "Merci de reporter tous bugs à l'adresse mail suivante:"
        )
        self.message2 = QtWidgets.QLabel(
            "<a href='mailto:arthur.perrin01@protonmail.com'>arthur.perrin01@protonmail.com</a>"
        )
        self.message3 = QtWidgets.QLabel("N'hesitez pas à contribuer au developpement sur:")
        self.message4 = QtWidgets.QLabel(
            "<a href='https://github.com/Onion2222/SaisieMesAbs'>GitHub</a>"
        )

        self.message2.setOpenExternalLinks(True)
        self.message4.setOpenExternalLinks(True)
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.message2.setAlignment(QtCore.Qt.AlignCenter)
        self.message3.setAlignment(QtCore.Qt.AlignCenter)
        self.message4.setAlignment(QtCore.Qt.AlignCenter)
        self.message.setMinimumWidth(400)
        self.button = QtWidgets.QPushButton("OK")
        self.button.setFixedWidth(80)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.message)
        layout.addWidget(self.message2)
        layout.addWidget(self.message3)
        layout.addWidget(self.message4)
        layout.addWidget(self.button, alignment=QtCore.Qt.AlignRight)
        self.button.clicked.connect(lambda : QtWidgets.QDialog.close(self))
        self.button.setFocus()
        self.exec()
        self.activateWindow()



def main() -> None:
    """Fonction principale du programme."""

    # Trouver le nom du module qui a été utilisé pour démarrer l'application
    app_module = sys.modules["__main__"].__package__

    # Récupérer les métadonnées de l'application
    metadata = importlib.metadata.metadata(app_module)
    
    QtWidgets.QApplication.setApplicationName(metadata["Formal-Name"])

    app = QtWidgets.QApplication(sys.argv)
    log.debug("Démarrage de l'application")
    
    # Création d'une fenetre POPUP pour afficher les erreurs
    popupLog = PopUpLogger()
    log.addHandler(popupLog)

    # Parser les arguments CLI
    parser = argparse.ArgumentParser()
    # Date
    parser.add_argument(
        "--date",
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help="Exécute le script pour une date donnée (format YYYY-mm-dd)"
    )
    # Configuration
    parser.add_argument("--conf", type=pathlib.Path,
                        help="Utilise un fichier de configuration défini")
    # Verbosité
    parser.add_argument('-v', "--verbosity",
                        type=int, default=1, required=False,
                        help="Niveau de verbosité [0:CRITICAL,1:INFO,2:DEBUG] "
                        "(par défaut: 1)")
    # Mode debug
    parser.add_argument('--debug',
                        action='store_true',
                        help="Mode DEBUG (développement uniquement !)")
    # Éditeur
    parser.add_argument('--editor',
                        type=str,
                        help="Permet de choisir un éditeur GUI "
                        "(gedit, gvim, etc.)")

    args = parser.parse_args()

    # Mode debug
    if args.debug:
        global DEBUG
        DEBUG = True
        args.verbosity = 1000  # Réglage de la verbosité pour le mode debug

    # Réglage de la verbosité
    if args.verbosity <= 0:
        log.setLevel(logging.CRITICAL)
    elif args.verbosity == 1:
        log.setLevel(logging.INFO)
    elif args.verbosity > 1:
        log.setLevel(logging.DEBUG)

    log.info("🧑 - Programme par \033[35m%s\033[0m", metadata["author"])
    log.info("📬 - Merci de reporter tous bugs à l'adresse mail suivante: "
             "\033[31mmailto:%s\033[0m", metadata["Author-email"])
    log.info("🌍 - Ou sur le repo suivant: \033[31m%s\033[0m", metadata["Home-page"])
    log.info("👁️  - Niveau de verbosité: %s", logging.getLevelName(log.level))

    log.debug("Arguments: %s", args)
    log.debug("Mode: DEBUG=%s", DEBUG)
    log.debug("Métadonnées: %s", metadata)

    # Récupération du fichier de configuration
    if args.conf:
        conf = get_conf(metadata["Formal-Name"], args.conf)
    else:
        conf = get_conf(metadata["Formal-Name"], None)

    log.info("🎛️  - Configuration: %s", conf['Chemin_conf'])

    # Vérifier si l'argument 'date' est fourni
    if not args.date:
        dateMes = datetime.today().strftime("%d/%m/%y")
        log.info("📆 - Date actuelle choisie")
    else:
        dateMes = args.date.strftime("%d/%m/%y")
        log.info("📆 - Date choisie : %s", dateMes)

    pathEditor: Optional[str] = None
    if args.editor:
        pathEditor = which(args.editor)
        if not pathEditor:
            log.warning("L'éditeur %s n'existe pas !", args.editor)
            sys.exit(1)
        log.info("🖋️  - Éditeur %s sélectionné", pathEditor)

    main_window = SaisieMesAbs(dateMes, metadata, conf, pathEditor)
    sys.exit(app.exec())
