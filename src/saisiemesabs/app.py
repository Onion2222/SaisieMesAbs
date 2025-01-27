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

from PySide6 import QtWidgets
from PySide6.QtGui import QIcon, Qt, QAction

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
log.setLevel(logging.DEBUG)
log_stream_handler = logging.StreamHandler(sys.stdout)
log_stream_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)8s] %(lineno)4d : %(message)s")
)
log.addHandler(log_stream_handler)

DEBUG = False

class SaisieMesAbs(QtWidgets.QMainWindow):
    """ Fenêtre principale
    """
    def __init__(self, date, metadata, configuration) -> None:
        super().__init__()
        # Récupération de la date de la mesure
        self.initdate = date
        # Récupération des metadata
        self.metadata = metadata
        # Récupération du fichier de configuration
        self.configuration = configuration
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
        self.mesure.append(
            Mesure(
                "Premières mesures de déclinaisons",
                "declinaison premiere serie",
                "declinaison",
                self.configuration["Angle"],
                self.configuration['Delai']["Etape"],
            )
        )
        self.mesure[0].ligne[0]["angle"].textChanged.connect(
            lambda: self.updateAngleOther(0)
        )  # Trigger pour l'autocomplet
        self.mesure.append(
            Mesure(
                "Premières mesures d'inclinaisons",
                "inclinaison premiere serie",
                "inclinaison",
                self.configuration["Angle"],
                self.configuration['Delai']["Etape"],
            )
        )
        self.mesure[1].ligne[0]["angle"].textChanged.connect(
            lambda: self.updateAngleOther(1)
        )
        self.mesure.append(
            Mesure(
                "Deuxiemes mesures de déclinaisons",
                "declinaison deuxieme serie",
                "declinaison",
                self.configuration["Angle"],
                self.configuration['Delai']["Etape"],
            )
        )
        self.mesure[2].ligne[0]["angle"].textChanged.connect(
            lambda: self.updateAngleOther(2)
        )
        self.mesure.append(
            Mesure(
                "Deuxiemes mesures d'inclinaisons",
                "inclinaison deuxieme serie",
                "inclinaison",
                self.configuration["Angle"],
                self.configuration['Delai']["Etape"],
            )
        )
        self.mesure[3].ligne[0]["angle"].textChanged.connect(
            lambda: self.updateAngleOther(3)
        )
        # Définition des mesures d'angle des 2 visées de cible
        self.vise1 = CalibrationAzimuth(1, self.configuration["Calibration"])
        self.vise1.angleVH.textChanged.connect(
            self.updateCalibration
        )  # Trigger pour l'autocomplete
        self.vise2 = CalibrationAzimuth(2, self.configuration["Calibration"])
        # Definition du groupe contextuel -> Date, Station et Azimuth repère
        self.contexte = QtWidgets.QGroupBox("Contexte")
        # DATE
        self.indDate = QtWidgets.QLabel("Date")
        self.date = SaisieDate()
        self.date.setText(self.initdate)
        # STATION
        self.layoutStation = QtWidgets.QFormLayout()
        self.indStation = QtWidgets.QLabel("Station")
        self.station = QtWidgets.QLineEdit(self.configuration["Station"].upper())
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
        # Déinition des logos
        self.logoGroup = QtWidgets.QGroupBox("Programme IPEV-EOST n°139")
        self.logoGroup.setMaximumHeight(self.contexte.sizeHint().height())
        logoEOST=Logo(":/Logo_EOST.png",self.layoutCon.sizeHint().height())
        logoIPEV=Logo(":/Logo_IPEV.png",self.layoutCon.sizeHint().height())
        # Arrangement dans un layout
        self.layoutLogo = QtWidgets.QHBoxLayout()
        self.layoutLogo.addWidget(logoEOST)
        self.layoutLogo.addWidget(logoIPEV)
        self.logoGroup.setLayout(self.layoutLogo)
        # Création du layout principale
        self.layoutPrincipale = QtWidgets.QGridLayout()
        # Ajout des widgets
        self.layoutPrincipale.addWidget(self.contexte, 0, 0)
        self.layoutPrincipale.addWidget(self.logoGroup, 0, 1)
        self.layoutPrincipale.addWidget(self.vise1, 1, 0)
        self.layoutPrincipale.addWidget(self.vise2, 1, 1)
        self.layoutPrincipale.addWidget(self.mesure[0], 2, 0)
        self.layoutPrincipale.addWidget(self.mesure[1], 2, 1)
        self.layoutPrincipale.addWidget(self.mesure[2], 3, 0)
        self.layoutPrincipale.addWidget(self.mesure[3], 3, 1)
        # Définition du bouton d'édition des angles calculés
        self.modifAngle = QtWidgets.QRadioButton("&Editer les angles calculés")
        # Quand cocher, activer la modification
        self.modifAngle.toggled.connect(
            lambda: self.modifAnglePressed(self.modifAngle)
        )
        # Définition du bouton enregistrer et de son raccourci
        self.btnEnregistrer = QtWidgets.QPushButton("Enregistrer (Ctrl+S)")
        self.btnEnregistrer.setShortcut("Ctrl+S")
        # Quand cliquer, enregistrer et quitter
        self.btnEnregistrer.clicked.connect(
            self.enregistrer
        )
        # Ajout des deux boutons au layout principale
        self.layoutPrincipale.addWidget(self.modifAngle)
        self.layoutPrincipale.addWidget(self.btnEnregistrer)
        # Mise en place du layout principale
        self.setLayout(self.layoutPrincipale)
        # Contenairisation du layout pour affichage
        container = QtWidgets.QWidget()
        container.setLayout(self.layoutPrincipale)
        self.setCentralWidget(container)
        # Empèche la modification de la taille de la fenêtre à la main
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        # Focus la premiere ligne à editer, pour etre plus rapide
        self.vise1.angleVH.setFocus()
        self.vise1.angleVH.selectAll()
        
        # Menu barre
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
        # - Aide | Lien
        aide.addAction(self.actionHelp)
        aide.addAction(self.actionSos)
        self.setMenuBar(self.menuBar)

        self.show()

    def openHelp(self):
        log.debug("Documentation")
        webbrowser.open(self.metadata["Home-page"])

    def sendSOS(self):
        log.debug("SOS")
        webbrowser.open(self.metadata["Author-email"])

    def editConf(self):
        log.debug("editConf")
        subprocess.Popen(['/usr/bin/xdg-open',self.configuration["Chemin_conf"]])

    def modifAnglePressed(self, btn) -> None:
        """ Fonction triggered quand la case de modification des angles
            calculés est cochée

        Args:
            btn (QtWidgets.QRadioButton): Bouton appuyé
        """
        # Stopper l'autocompletion des 4 mesures
        for i in range(4):
            self.mesure[i].stopUpdate(not btn.isChecked())

    def updateAngleOther(self, numMesure) -> None:
        """ Ordonne la mise à jour des angles de mesure pour l'autocomplet

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

    def enregistrer(self) -> None:
        """ Enregistre les données dans un fichier re et quitte l'application
        """
        log.debug("Enregistrement... (DEBUG %s)",DEBUG)
        # Ces deux lignes permettent de forcer un rewrite()
        # sur les QtWidgets.QLineEdit et ainsi reformater les nombres
        self.setFocus()
        self.update()
        # Valide la saisie avant enregistrement
        if not self.validateAll():
            # si mesure pas valide, beep
            QtWidgets.QApplication.beep()
            # Si pas DEBUG, ne rien faire (la mesure n'est pas valide)
            if not DEBUG:
                return
            # Si debug, avertir et passer à l'enregistrement
            log.debug(
                "La mesure n'est pas valide, mais DEBUG=True"
            )

        saveMesure = (
            f'{self.station.text().lower()} {self.date.text().replace("/", " ")}'
            ' Methode des residus\n'
            f'visees balise\n'
            f' {self.angleAR.text()}\n'
            f'{self.getAziCible(self.vise1)[0]} {self.getAziCible(self.vise1)[1]}\n'
            f'{self.getAziCible(self.vise2)[0]} {self.getAziCible(self.vise2)[1]}\n')
        for eMesure in self.mesure:
            saveMesure += (
                f"{self.dicDataToString( self.getMesure(eMesure) )}\n"
            )
        log.debug(saveMesure)

        # Enregistrement
        saveFilename = self.generateFileName()
        saveFile = self.generatePath() / saveFilename
        try:
            with open(saveFile, "w", encoding='utf-8') as saveFile:
                saveFile.write(saveMesure)
        except FileNotFoundError:
            log.critical(
                "❌ - Erreur, le chemin configuré n'existe pas ! (%s)",
                saveFile
            )
            log.critical(
                "❌ - Ecriture des données dans le repertoire courant ./%s car %s n'existe pas",
                saveFilename,
                saveFile
            )
            with open(saveFilename, "w", encoding='utf-8') as saveFile:
                saveFile.write(saveMesure)
        # Quittr la fenêtre
        self.close()

    def dicDataToString(self, dicData) -> str:
        """ Convertit un dictionnaire de donnée en string pour l'enregistrement

        Args:
            dicData (dictionnaire): dictionnaire de donnée générer par Mesure

        Returns:
            str: string de donnée format re
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
        for eMesure in self.mesure:
            mesValide &= eMesure.validate()
        return mesValide & self.vise1.validate() & self.vise2.validate()

    def generatePath(self) -> pathlib.Path:
        """ Génère un dossier d'enregistrement correspondant 
        à la mesure

        Returns:
            pathlib.Path: path définit dans le fichier conf
        """
        return pathlib.Path(
            self.contexteConf["PATH_RE"]
            .replace("%$YY", self.date.text()[6:8])
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

    def getAziCible(self, vise: CalibrationAzimuth) -> tuple:
        """recupère les angle de visée

        Args:
            vise (CalibrationAzimuth): objet de visé

        Returns:
            tuple (str, str): angle visée cible 1
        """
        return vise.getAzi()

    def getMesure(self, mesure) -> dict:
        """Récupère le dictionnaire de mesure

        Args:
            mesure (Mesure): Objet mesure à lire

        Returns:
            dict: dictionnaire comprennant les différentes données d'une mesure
        """
        return mesure.getData()

def is_a_date(date) -> bool:
    """Renvoie True si la date jj/mm/aa est valide

    Args:
        date (str): Date a valider au format jj/mm/aa

    Returns:
        bool: Date valide ou pas
    """
    return date_re.match(date)

def analyse_conf(chemin_fichier: pathlib.Path) -> dict:
    try:
        log.info("Analyse du fichier %s", chemin_fichier)
        contentConfig = configparser.ConfigParser()
        contentConfig.read(chemin_fichier)
        configuration:dict = {}
        configuration["Chemin_conf"]=chemin_fichier
        configuration["Station"]=contentConfig["STATION"]["NOM_STATION"]
        configuration["Azimuth_Rep"]=contentConfig["STATION"]["AZIMUTH_REPERE"]
        configuration["Chemin_Sauvegarde"]=contentConfig["STATION"]["PATH_RE"]
        configuration['Angle'] = {
            "inc": contentConfig["AUTOCOMPLETE"]["AUTO_INC_ANGLE"],
            "dec": contentConfig["AUTOCOMPLETE"]["AUTO_DEC_ANGLE"]
        }
        configuration['Calibration'] = {
            "haut": contentConfig["AUTOCOMPLETE"]["AUTO_CAL_ANGLE_HAUT"],
            "bas": contentConfig["AUTOCOMPLETE"]["AUTO_CAL_ANGLE_BAS"]
        }
        configuration['Delai']={
            "Etape" : int(contentConfig["AUTOCOMPLETE"]["SEC_ENTRE_MESURES"]),
            "Mesure" : int(contentConfig["AUTOCOMPLETE"]["SEC_ENTRE_ETAPES"])
        }
        return configuration
    except ValueError:
        log.critical("❌ - Le fichier de configuration n'est pas valide")

def get_dataDir(app_name) -> pathlib.Path:
    """
    """

    home = pathlib.Path.home()

    if sys.platform == "linux":
        dataDir = home / ".local/share"
    else:
        log.critical("Plateforme inconnue ! %s", sys.platform)
        raise SystemError

    myDataDir = dataDir / app_name

    try:
        myDataDir.mkdir(parents=True)
        log.debug("Le dossier data local n'existait pas et a été créé")
    except FileExistsError:
        log.debug("Le dossier data local existe bien")
    return myDataDir


def get_conf(app_name: str, conf_path: pathlib.Path = None) -> pathlib.Path:
    """ Obtenir le chemin du fichier de configuration
        Si l'application n'a pas de fichier de configuration par défaut, en créer un
        Si un chemin est donné, verifier sa validité
        Sinon utiliser le chemin par défaut de l'application

    Args:
        app_name (str): Nom de l'application
        conf_path (pathlib.Path, optional): Chemin vers le fichier conf. Defaults to None.

    Returns:
        pathlib.Path: Le chemin du fichier de configuration
    """
    if not conf_path:
        log.debug("Pas de conf donné")
        conf_path = get_dataDir(app_name) / "configuration.json"
        if not conf_path.is_file():
            log.warning("Le fichier de configuration %s n'existe pas -> création", conf_path)
            # Création du fichier conf
            with open(conf_path, "w", encoding='utf-8') as conf_file:
                conf_file.write(create_conf())
        try:
            return analyse_conf(conf_path)
        except (KeyError, ValueError):
            with open(conf_path, "w", encoding='utf-8') as conf_file:
                conf_file.write(create_conf())
            return analyse_conf(conf_path)

    # Verifier que le fichier fonctionne
    config_tocheck = configparser.ConfigParser()
    log.info("Verification du fichier de configuration")
    try:
        log.debug(conf_path.absolute())
        config_tocheck.read(conf_path.absolute())
        return analyse_conf(conf_path)

    except (ValueError, KeyError):
        log.warning("Le fichier de configuration %s est invalide", conf_path)
        return get_conf(app_name, None)



def create_conf() -> str:
    """ Créer un string de configuration

    Returns:
        str: configuration
    """
    return (
        "[STATION]\n\n"
        "# Nom de la station en minuscule\n"
        "NOM_STATION     = NA\n\n"
        "#PATH du chemin où enregistrer les mesures\n"
        "# - $YY sera remplacé par les deux derniers chiffres de l'année de la mesure\n"
        "# - $STATION par le nom de la station en minuscule\n"
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


def main():
    """ Main
    """

    # Find the name of the module that was used to start the app
    app_module = sys.modules["__main__"].__package__
    # Retrieve the app's metadata
    metadata = importlib.metadata.metadata(app_module)

    # Parsing des arguments cli
    parser = argparse.ArgumentParser()
    # Date
    parser.add_argument(
        "--date",
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help="Execute le script pour une date donnée (format YYYY-mm-dd)"
    )
    # Configuration
    parser.add_argument("--conf", type=pathlib.Path,
                        help="Utilise un fichier de configuration défini")
    # Verbosité
    parser.add_argument('-v', "--verbosite",
                        type=int, default=1, required=False,
                        help="Verbosité [0:CRITICAL,1:INFO,2:DEBUG] (defaut: 1)")
    # Debug
    parser.add_argument('--debug',
                        action='store_true',
                        help="Mode DEBUG (dev seulement !)")

    args = parser.parse_args()

    # Debug
    if args.debug:
        global DEBUG
        DEBUG = True
        args.verbosite=1000

    # Réglage de la verbosité
    if args.verbosite <= 0:
        log.setLevel(logging.CRITICAL)
    elif args.verbosite <= 1:
        log.setLevel(logging.INFO)
    elif args.verbosite > 1:
        log.setLevel(logging.DEBUG)

    log.debug("Arguments: %s",args)
    log.debug("DEBUG: %s",DEBUG)


    log.info("🧑 - Programme par \033[35m%s\033[0m",metadata["author"])
    log.info("💙 - Merci de reporter tous bugs à l'adresse suivante:")
    log.info("📬 - \033[31mmailto:%s\033[0m",metadata["Author-email"])
    log.info("📝 - Ou sur le repo suivant:")
    log.info("🌍 - \033[31m%s\033[0m",metadata["Home-page"])

    # Recupération du fichier de configuration
    if args.conf:
        conf = get_conf(metadata["Formal-Name"], args.conf)
    else:
        conf = get_conf(metadata["Formal-Name"],None)
    log.info(conf)
    log.info("🎛️ - Configuration: %s", conf['Chemin_conf'])

    # Verifie si l'argument date est entré
    if not args.date:
        dateMes = datetime.today().strftime("%d/%m-/%y")
        log.info("📆 - Date actuelle choisie")
    else:
        dateMes = args.date.strftime("%d/%m-/%y")
        log.info("📆 - %s choisie", dateMes)

    QtWidgets.QApplication.setApplicationName(metadata["Formal-Name"])

    app = QtWidgets.QApplication(sys.argv)
    log.debug("Démarrage de l'application")
    main_window = SaisieMesAbs(dateMes, metadata, conf)
    sys.exit(app.exec())
