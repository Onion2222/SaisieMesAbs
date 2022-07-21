#!/usr/bin/python3

import re
import sys
from datetime import datetime

from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLayout, QLineEdit, QPushButton, QRadioButton,
                               QWidget)

import ressources

#~~Variables Globales~~#
PATH_RE="./"
Stations=["PAF","AMS","CRO","WEL"]
Azimuth_Repere="52.35840"   #A modifier selon station
IndexStation=0              #A modifier selon station
AutoIncAngle="123.----"     #A modifier selon station
AutoDecAngle="233.----"     #A modifier selon station
AutoCalAngleHaut="247.75--" #A modifier selon station
AutoCalAngleBas="47.75--"   #A modifier selon station
SecEntreMesures=45          #A modifier selon UTILISATEUR

DEBUG=False

heure_re = re.compile(r'^(([01]\d|2[0-3])([0-5]\d)|24:00)([0-5]\d)$')
angle_re = re.compile(r'^(?:[0-3]*[0-9]{1,2}|400)(?:\.[0-9]{4})$')
mesure_re= re.compile(r'^(?:-*[0-9]+)(?:\.[0-9]{1})$')
date_re  = re.compile(r'^\d{2}\/\d{2}\/\d{2}$') #Ne prend pas en compte les années bi, le nombre de jours du mois et les nombre de mois.

class MainWindow(QWidget):
    
    def __init__(self, arguments):
        """initialisation de la fenêtre principale

        Args:
            arguments (array): liste des arguments
        """
        
        #Verifie si l'argument date est entré
        try:
            indexDate=arguments.index("-d")+1
            if indexDate<len(arguments):
                if isADate( arguments[indexDate] ):
                    self.initdate=arguments[indexDate]
                else:
                    raise ValueError       
        except ValueError: #Pas de date specifié ou date incorrecte
            self.initdate=datetime.today().strftime('%d/%m-/%y')
            print("❌ - Pas de date specifié avec \"-d jj/mm/yy\"")
            print("📆 - Date actuelle choisie")

        super(MainWindow, self).__init__()

        #Titre
        self.setWindowTitle("Enregistrement des mesures magnétiques")
        self.setWindowIcon(QIcon(':/icon.png'))

        #Définition des 4 mesure (déclinaison 1&2, inclinaison 1&2)
        self.mesure=[] #Array comprennat les widget de mesure
        self.mesure.append(Mesure("Premières mesures de déclinaisons","declinaison premiere serie","declinaison"))
        self.mesure[0].ligne[0]['angle'].textChanged.connect(lambda:self.updateAngleOther(0)) #Trigger pour l'autocomplet
        self.mesure.append(Mesure("Premières mesures d'inclinaisons","inclinaison premiere serie","inclinaison"))
        self.mesure[1].ligne[0]['angle'].textChanged.connect(lambda:self.updateAngleOther(1))
        self.mesure.append(Mesure("Deuxiemes mesures de déclinaisons","declinaison deuxieme serie","declinaison"))
        self.mesure[2].ligne[0]['angle'].textChanged.connect(lambda:self.updateAngleOther(2))
        self.mesure.append(Mesure("Deuxiemes mesures d'inclinaisons","inclinaison deuxieme serie","inclinaison"))
        self.mesure[3].ligne[0]['angle'].textChanged.connect(lambda:self.updateAngleOther(3))

        #Définition des mesures d'angle des 2 visées de cible
        self.V1=CalibrationAzimuth(1)
        self.V1.angleVH.textChanged.connect(lambda:self.updateCalibration()) #Trigger pour l'autocomplet
        self.V2=CalibrationAzimuth(2)

        #Definition du groupe contextuel -> Date, Station et Azimuth repère
        self.contexte=QGroupBox("Contexte")
        #DATE
        self.indDate=QLabel("Date")
        self.date = SaisieDate()
        self.date.setText(self.initdate)
        #STATION
        self.layoutStation=QFormLayout()
        self.indStation=QLabel("Station")
        self.listStation=QComboBox()
        self.listStation.setFixedWidth(150)
        self.listStation.addItems(Stations)
        self.listStation.setItemText(IndexStation,Stations[IndexStation])
        #Azimuth repère
        self.indAR=QLabel("Azimuth repère")
        self.angleAR = SaisieAngle()
        self.angleAR.setText(Azimuth_Repere)
        #Arrangement dans un layout
        self.layoutCon=QFormLayout()
        self.layoutCon.addRow(self.indStation,self.listStation)
        self.layoutCon.addRow(self.indDate,self.date)
        self.layoutCon.addRow(self.indAR,self.angleAR)
        self.contexte.setLayout(self.layoutCon)

        #Déinition des logos
        self.logoGroup=QGroupBox("Programme IPEV-EOST n°139")
        self.logoGroup.setMaximumHeight(self.contexte.sizeHint().height())
        logoEOST=Logo(":/Logo_EOST.png",self.layoutCon.sizeHint().height())
        logoIPEV=Logo(":/Logo_IPEV.png",self.layoutCon.sizeHint().height())
        #Arrangement dans un layout
        self.layoutLogo=QHBoxLayout()
        self.layoutLogo.addWidget(logoEOST)
        self.layoutLogo.addWidget(logoIPEV)
        self.logoGroup.setLayout(self.layoutLogo)

        #Création du layout principale
        self.layoutPrincipale=QGridLayout()
        #Ajout des widgets
        self.layoutPrincipale.addWidget(self.contexte, 0, 0)
        self.layoutPrincipale.addWidget(self.logoGroup, 0, 1)
        self.layoutPrincipale.addWidget(self.V1, 1, 0)
        self.layoutPrincipale.addWidget(self.V2, 1, 1)
        self.layoutPrincipale.addWidget(self.mesure[0],2,0)
        self.layoutPrincipale.addWidget(self.mesure[1],2,1)
        self.layoutPrincipale.addWidget(self.mesure[2],3,0)
        self.layoutPrincipale.addWidget(self.mesure[3],3,1)
        #Définition du bouton d'édition des angles calculés
        self.modif_angle = QRadioButton("&Editer les angles calculés")
        self.modif_angle.toggled.connect(lambda:self.modif_angle_pressed(self.modif_angle)) #Quand cocher, activer la modification
        #Définition du bouton enregistrer et de son raccourci
        self.BtnEnregistrer = QPushButton("Enregistrer (Ctrl+S)")
        self.BtnEnregistrer.setShortcut("Ctrl+S")
        self.BtnEnregistrer.clicked.connect(lambda:self.enregistrer(DEBUG)) #Quand cliquer, enregistrer et quitter
        #Ajout des deux boutons au layout principale
        self.layoutPrincipale.addWidget(self.modif_angle)
        self.layoutPrincipale.addWidget(self.BtnEnregistrer)
        #Mise en place du layout principale
        self.setLayout(self.layoutPrincipale)
        
        #Autre:
        #Empèche la modification de la taille de la fenêtre à la main
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        #Focus la premiere ligne à editer, pour etre plus rapide
        self.V1.angleVH.setFocus()
        self.V1.angleVH.selectAll()

    def modif_angle_pressed(self,btn):
        """Fonction triggered quand la case de modification des angles calculés est cochée

        Args:
            btn (QRadioButton): Bouton appuyé
        """
        #Stopper l'autocompletion des 4 mesures
        for i in range(4):
            self.mesure[i].stopUpdate(btn.isChecked()) 
        return
            
    def updateAngleOther(self, num):
        """Ordonne la mise à jour des angles de mesure pour l'autocomplet

        Args:
            num (int): index du demandeur
            de mise à jour
        """
        if self.modif_angle.isChecked() : return #si les angles sont édité manuellement, on quitte la fonction
        if num==0 and self.mesure[0].ligne[0]['angle'].isValid(False): #Si l'utilisateur à entrer une valeur non vide dans la premiere mesure
            self.mesure[1].updateEst(float(self.mesure[0].ligne[0]['angle'].text())) #maj angle est magnetique de la mesure 2
            self.mesure[2].updateAngle(float(self.mesure[0].ligne[0]['angle'].text()), True) #maj angles de la mesure 3
            self.mesure[3].updateEst(float(self.mesure[0].ligne[0]['angle'].text())) #maj angle est magnetique de la mesure 4
            return
        #maj des angles de la 4e mesure à partir de ceux de la 2e
        if num==1 and self.mesure[1].ligne[0]['angle'].isValid(False):
            self.mesure[3].updateAngle(float(self.mesure[1].ligne[0]['angle'].text()), True)
            return
        #maj de l'angle de l'est magnetique de la 4e mesure à partir de ceux de la 3e
        if num==2 and self.mesure[2].ligne[0]['angle'].isValid(False):
            self.mesure[3].updateEst(float(self.mesure[2].ligne[0]['angle'].text()))
            return
        
    def updateCalibration(self):
        """Met à jour les angles de la deuxième visé à partir de la première pour autocomplet
        """
        if self.V2.updatable and self.V1.angleVH.isValid(False) : 
            self.V2.angleVH.setText(self.V1.angleVH.text())
        return
    
    def enregistrer(self, debug=False):
        """Enregistre les données dans un fichier re et quitte l'application

        Args:
            debug (bool, optional): Active le debug pour visu les données. Defaults to False.
        """
        
        #Ces deux lignes permettent de forcer un rewrite() sur les QLineEdit et ainsi reformater les nombres
        self.setFocus()
        self.update()
        
        if debug:
            print("SAVE")
            print("Contexte:")
            print(self.getContext())
            print("Azimuth Cible")
            print(self.getAziCible(self.V1))
            print(self.getAziCible(self.V2))
            for i in range(len(self.mesure)):
                print(self.getMesure(self.mesure[i]))
            
        if not self.validateAll(): #Valide la saisie avant enregistrement
            QApplication.beep() #si pas valide, beep
            if not debug : return #et ne sauvegarde pas

        #Ecriture dans fichier
        self.nom_du_fichier=self.generateFilename() #Génération du nom de fichier
        f = open(PATH_RE+self.nom_du_fichier, 'w') #Création du fichier
        f.writelines(self.getContext()[0].lower()+" "+self.getContext()[1].replace("/", " ")+" Methode des residus\n")
        f.writelines("visees balise\n")
        f.writelines(" "+self.getContext()[2]+"\n")
        f.writelines(self.getAziCible(self.V1)[0]+" "+self.getAziCible(self.V1)[1]+"\n")
        f.writelines(self.getAziCible(self.V2)[0]+" "+self.getAziCible(self.V2)[1]+"\n")
        f.writelines("\n")
        
        
        for i in range(len(self.mesure)):
            f.writelines(self.dicDataToString(self.getMesure(self.mesure[i]))+"\n")
        
        self.quitter() #Quitte la fenêtre

    def quitter(self):
        """Quitte l'application
        """
        self.close()
        
    def dicDataToString(self, dicData):
        """Convertit un dictionnaire de donnée en string pour l'enregistrement

        Args:
            dicData (dictionnaire): dictionnaire de donnée générer par Mesure

        Returns:
            str: string de donnée format re
        """
        text=""
        if dicData['est']!='null': text+=("est magnetique : "+dicData['est']+"\n")
        text+=dicData['nom']+"\n"
        for i in range(4):
            data=dicData['mesures'][i]
            print(data)
            text+=(data['heure']+"\t"+data['angle']+"\t"+data['mesure']+"\n")
        return text
    
    def validateAll(self):
        """Valide l'ensemble des données saisies et autocomplétés

        Returns:
            bool: True si ensemble données valide, False sinon
        """
        MesValide=True
        for i in range(4):
            MesValide=(MesValide & self.mesure[i].validate())
        return MesValide & self.V1.validate() & self.V2.validate()
        
    def generateFilename(self):
        """Génère un nom de fichier grâce aux paramètres contextuels entrés par l'utilisateur

        Returns:
            str: nom d'un fichier re de type re%m%d%h%y.$base
        """
        arrayDate=self.date.text().split("/")
        heure=self.mesure[0].ligne[0]['heure'].text()
        return "re"+arrayDate[1]+arrayDate[0]+heure[0:2]+arrayDate[2]+"."+self.getContext()[0].lower()
    
    def getContext(self):
        """Donne le contexte (staion, date et azimuth repère) en tupple

        Returns:
            tuple (str, str, str): (station, date, azimuth repère)
        """
        return self.listStation.currentText(), self.date.text(), self.angleAR.text()
    
    def getAziCible(self, vise):
        """recupère les angle de visée 
        
        Args:
            vise (CalibrationAzimuth): objet de visé

        Returns:
            tuple (str, str): angle visée cible 1
        """
        return vise.getAzi()
    
    def getMesure(self,mesure):
        """Récupère le dictionnaire de mesure

        Args:
            mesure (Mesure): Objet mesure à lire

        Returns:
            dictionnaire: dictionnaire comprennant les différentes données d'une mesure
        """
        return mesure.getData()


class Logo(QLabel):
    
    def __init__(self, path, maxHeight):
        """Génération d'un label pour afficher un logo

        Args:
            path (str): chemin du logo
            maxHeight (int): Hauteur maximale
        """
        super(Logo,self).__init__()
        self.setFixedHeight(maxHeight-20) #pourquoi ? bah parce que ça marche mieux avec -20
        logo=QPixmap(path).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(logo)
        self.setMask(logo.mask())


class SaisieDate(QLineEdit):
    
    def __init__(self):
        """QLineEdit pour la saisie d'une date
        """
        super(SaisieDate, self).__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(150)
        self.setInputMask("99/99/99")
        

class MyLineEdit(QLineEdit):
    
    def __init__(self, text):
        """QLineEdit à ma sauce pour l'inscription de l'heure/angle/mesure

        Args:
            text (str): Texte d'indication
        """
        self.editedByHand=False #Variable indiquant si la valeur a été modifiée par l'homme (pour l'autocomplet)
        super(MyLineEdit, self).__init__()
        self.initext=text
        self.setAlignment(Qt.AlignCenter)
        self.mousePressEvent = self.press #Action en cas de clique de souris
        self.setText(text)
        self.setFixedWidth(150)
        self.textEdited.connect(lambda:self.edited()) #lorsque due la valeur est editée
        self.editingFinished.connect(lambda:self.changed())
        self.regexValidator=re.compile(r'') 
        
    def validatepls(self):
        """Emet un son lorsqu'il y a une erreur d'input
        """
        if not self.hasAcceptableInput(): QApplication.beep() 
    
    def press(self, o):
        """Lors du clique de la souris, efface le text d'indication

        Args:
            o (?): ?
        """
        if self.text()==self.initext : self.setText("")
    
    def edited(self):
        """Appelé lors d'une edition d'origine humaine
        """
        self.editedByHand=True
        if self.text()!='-': self.validatepls()
    
    def setText(self,string, force=False):
        """Change le texte s'il n'a pas été modifié par l'homme

        Args:
            string (str): nouveau texte
            force (bool, optional): force l'edition. Defaults to False.
        """
        if (not self.editedByHand or force) : super().setText(string)
        
    def rewrite(self):
        """A overrider
        """
        pass
    
    def changed(self):
        """Executer si la saisie est modifié, verifie si la saisie est valide. Sinon emet un beep
        """
        self.rewrite()
        if not self.isValid() : QApplication.beep()
        
    def isStrange(self):
        """à overrider, determine si une saisie est anormale

        Returns:
            bool: False
        """
        return False
    
    def isValid(self, color=True):
        """Verifie si la saisie est valide à partir des regex

        Args:
            color (bool, optional): Colorie la case selon sa validation . Defaults to True.

        Returns:
            bool: Saisie valide ou non
        """
        if ( self.hasAcceptableInput() and self.regexValidator.match(self.text()) ):
            if (self.isStrange()):
                self.setStyleSheet("color: orange")
            else:
                self.setStyleSheet("color: green;")
            return True
        else: 
            if color : self.setStyleSheet("color: red;")
            return False
        

class SaisieHeure(MyLineEdit):
    
    def __init__(self, textInit="hhmmss"):
        """MyLineEdit pour saisir une heure
        """
        super(SaisieHeure, self).__init__(textInit)
        self.setMaxLength(6)
        self.regexValidator=heure_re


class SaisieAngle(MyLineEdit):
    
    def __init__(self, textInit="---.----"):
        """MyLineEdit pour la saisie d'angle gradiant
        """
        super(SaisieAngle, self).__init__(textInit)
        """"angleValidator=QDoubleValidator(0,400,4) #de 0 à 400, avec 4 decimale
        angleValidator.setLocale(QLocale.English) #permet d'avoir un '.' comme séparateur décimale
        self.setValidator(angleValidator)"""
        self.setMaxLength(8)
        self.regexValidator=angle_re
        self.selectionChanged.connect(lambda:self.changeSelection())
        
    def changeSelection(self):
        """Permet la saisie intelligente des données préremplie
        """
        if self.selectionLength() == len(self.text()): #si tout le text est selectionné
                self.setSelection(self.initext.find('-'),len(self.text())) #selection uniquement des "--" initialisé
        return
    
    def rewrite(self):
        """Permet de reecrire la celule dans le bon format (ex: ajout des 0 manquants pour avoir 4 decimals)
        """
        try:
            self.setText('%.4f' % ((float( self.text() ))), True) 
            self.update()
        except ValueError:
            return
    
               
class SaisieMesure(MyLineEdit):
    
    def __init__(self, textInit="--.-"):
        """MyLineEdit pour la saisir d'une mesure en nT
        """
        super(SaisieMesure, self).__init__(textInit)        
        self.regexValidator=mesure_re
    
    def rewrite(self):
        """rewrite() permet de reecrire la celule dans le bon format (ex: ajout des 0 manquants pour avoir 1 decimal)
        """
        try: 
            self.setText('%.1f' % (float( self.text() )), True)
            self.update()
        except ValueError:
            return
        return
    def isStrange(self):
        """Override de isStrange() du parent, fournit un detecteur de saisie anormale

        Returns:
            bool: True si valeur anormale 
        """
        return (float(self.text())>=10 or float(self.text())<=-10)
    

class CalibrationAzimuth(QGroupBox):
    
    def __init__(self, num):
        """Layout pour la saisie des angle de visé de la cible

        Args:
            num (int): Numéro de la visée (1 ou 2)
        """
        super(CalibrationAzimuth, self).__init__()
        #Titre
        self.setTitle("Visée d'ouverture "+str(num))
        
        #Définition du layout
        self.layoutCal=QFormLayout()
        #Définition des labels
        self.indVH=QLabel("V"+str(num)+" sonde en haut")
        self.indVB=QLabel("V"+str(num)+" sonde en bas")
        #Définition de la saisie des angles
        self.angleVH = SaisieAngle(AutoCalAngleHaut)
        self.angleVB = SaisieAngle(AutoCalAngleBas)
        #Création du layout
        self.layoutCal.addRow(self.indVH,self.angleVH)
        self.layoutCal.addRow(self.indVB,self.angleVB)
        self.setLayout(self.layoutCal)
        self.setFixedWidth(500)

        #Mise en place des triggers
        self.angleVH.textChanged.connect(lambda:self.updateAngle(self.angleVH.text()))
        self.angleVH.textEdited.connect(lambda:self.stopUpdate())

        self.updatable=True #Autcompletion activé

    def updateAngle(self,angle):
        """autocomplet le deuxieme angle de visée (sonde en bas)

        Args:
            angle (str): angle de visée sonde en haut
        """
        try: 
            if angle!='' and not self.angleVB.editedByHand: self.angleVB.setText('%.4f' % ((float(angle)+200)%400))
        except ValueError:
            pass
        
    def stopUpdate(self):
        """Désactive l'autocomplétion
        """
        self.updatable=False
        
    def getAzi(self):
        """Retourne les données saisis

        Returns:
            tuple (str, str): angles de visé
        """
        return self.angleVH.text(),self.angleVB.text()

    def validate(self):
        """Valide les angles saisies

        Returns:
            bool: Angles valides ou nom
        """
        return (self.angleVB.isValid() & self.angleVH.isValid())
    

class Mesure(QGroupBox):
    
    def __init__(self, titre, nomMesure, typeMesure):
        """Widget des mesure d'inclinaison et de declinaison

        Args:
            titre (str): Nom de la mesure
            nomMesure (str): Nom de la mesure pour transfert des datas
            typeMesure (str): inclinaison ou declinaison
        """
        super(Mesure, self).__init__()
        self.setTitle(titre) #titre
        self.typeMesure=typeMesure #recup type mesure
        self.nomMesure=nomMesure
        
        #définition du layout
        self.layoutMesurePr=QGridLayout()

        #si mesure d'inclinaison alors permettre la saisie de l'est magnétique
        if self.typeMesure=="inclinaison":
            self.indAngleEst=QLabel("Est magnétique")
            self.indAngleEst.setAlignment(Qt.AlignCenter)
            self.angleEst=SaisieAngle(AutoDecAngle)
            self.layoutMesurePr.addWidget(self.indAngleEst, 0, 1)
            self.layoutMesurePr.addWidget(self.angleEst, 1, 1)
        else: #sinon
            self.indSpace1=QLabel("")
            self.indSpace2=QLabel("") #je "créer" du vide pour la symmétrie esthetique
            self.layoutMesurePr.addWidget(self.indSpace1, 0, 1)
            self.layoutMesurePr.addWidget(self.indSpace2, 1, 1)

        #definition des indication et des cases de saisie
        self.indHeure=QLabel("HEURE")
        self.indHeure.setAlignment(Qt.AlignCenter)
        self.indAngle=QLabel("ANGLE")
        self.indAngle.setAlignment(Qt.AlignCenter)
        self.indMesure=QLabel("MESURE (nT)")
        self.indMesure.setAlignment(Qt.AlignCenter)
        self.layoutMesurePr.addWidget(self.indHeure,2,1)
        self.layoutMesurePr.addWidget(self.indAngle,2,2)
        self.layoutMesurePr.addWidget(self.indMesure,2,3)

        #definition de la liste des 4 ligne de mesures
        self.ligne=[]
        #création des lignes de mesure
        #self.ligne=[{'label':...,'heure':'hhmmss','angle':'--.----','mesure':'-x.x'},...]
        for i in range(4):
            heure = SaisieHeure()
            mesure = SaisieMesure()
            #angle = SaisieAngle()
            if i==0:
                if self.typeMesure=="inclinaison":
                    angle = SaisieAngle(AutoIncAngle)
                else:
                    angle = SaisieAngle(AutoDecAngle)
            else:
                angle = SaisieAngle()
            
            numero=QLabel(str(i+1))
            self.ligne.append({"label":numero,"heure":heure,"angle":angle,"mesure":mesure})
            self.layoutMesurePr.addWidget(self.ligne[i]['label'], 3+i, 0)
            self.layoutMesurePr.addWidget(self.ligne[i]['heure'], 3+i, 1)
            self.layoutMesurePr.addWidget(self.ligne[i]['angle'], 3+i, 2)
            self.layoutMesurePr.addWidget(self.ligne[i]['mesure'], 3+i, 3)
            """
            #cela ne marche pas et je ne sais pas pq
            if i <= 3:
                print(i)
                self.ligne[i]['heure'].editingFinished.connect(lambda:self.updateHeure(i))
                
            """
                
        self.ligne[0]['heure'].editingFinished.connect(lambda:self.updateHeure(0))
        self.ligne[1]['heure'].editingFinished.connect(lambda:self.updateHeure(1))
        self.ligne[2]['heure'].editingFinished.connect(lambda:self.updateHeure(2))

        #lors de la modification de la valeur de l'angle de la premiere ligne
        self.ligne[0]['angle'].textEdited.connect(lambda:self.updateAngle(float(self.ligne[0]['angle'].text()), False)) 
        

        #autocompletion permise
        self.stopUpdate(False)

        #Mise en place du layout
        self.setFixedWidth(500)
        self.setLayout(self.layoutMesurePr)

    def stopUpdate(self, etat):
        """Désactive/active l'autocompletion

        Args:
            state (bool): True pour desactiver l'autocompletion
        """
        #désactive/active les cases de saisie d'angle des 3 derniere lignes
        for i in range(1,4):
            self.ligne[i]['angle'].setDisabled(not etat) 
        #désactive/active la case de saisie d'est mag
        if self.typeMesure=="inclinaison" : self.angleEst.setDisabled(not etat)
        
    def updateHeure(self, indexLigne):
        """Autocomplete pour la datation de la prochaine ligne de mesure

        Args:
            indexLigne (int): index de la ligne où l'heure a été saisie
        """
        if self.ligne[indexLigne]['heure'].isValid(False):
            initHour = self.ligne[indexLigne]['heure'].text()
            calculedHour=dateAddSeconds(initHour, SecEntreMesures)
            self.ligne[indexLigne+1]['heure'].setText(calculedHour)
    
    def updateAngle(self, angle, all):
        """Autocomplete sur demande

        Args:
            angle (str): angle fournit
            all (bool): mise à jour de tous les angles ou juste des 3 derniers
        """
        if all: self.ligne[0]['angle'].setText('%.4f' % angle)
        if self.typeMesure=="declinaison":
            self.ligne[1]['angle'].setText('%.4f' % angle)
            self.ligne[2]['angle'].setText('%.4f' %((angle+200)%400))
            self.ligne[3]['angle'].setText('%.4f' %((angle+200)%400))
        else:
            self.ligne[1]['angle'].setText('%.4f' %((angle+200)%400))
            self.ligne[2]['angle'].setText('%.4f' %((400-angle)%400))
            self.ligne[3]['angle'].setText('%.4f' %((400-angle-200)%400))

    def updateEst(self, angle):
        """Autocomplet la saisie de l'est magnetique

        Args:
            angle (str): angle fournit
        """
        self.angleEst.setText('%.4f' % angle)

    def getData(self):
        """fournit TOUTES les données

        Returns:
            dictionnaire: Toutes les données sous forme d'un dico
        """
        collectionData={"est":"null","mesures":[]}
        for i in range(0,4):
            newCollec={}
            heure=self.ligne[i]['heure'].text()
            newCollec["heure"]=heure[0:2]+" "+heure[2:4]+" "+heure[4:6]
            newCollec["angle"]=self.ligne[i]['angle'].text()
            newCollec["mesure"]=self.ligne[i]['mesure'].text()
            collectionData['mesures'].append(newCollec)
        if self.typeMesure=="inclinaison": collectionData["est"]=self.angleEst.text()
        collectionData['nom']=self.nomMesure
        return collectionData
    
    def validate(self):
        LineIsValide=True
        for i in range(4):
            LineIsValide= self.ligne[i]['heure'].isValid() & self.ligne[i]['angle'].isValid() & self.ligne[i]['mesure'].isValid()
        if self.typeMesure=='inclinaison':
            return LineIsValide & self.angleEst.isValid()
        else:
            return LineIsValide


def dateAddSeconds(date,sec):
    """Additionne une horaire au format hhmmss à un nombre de second

    Args:
        date (str): Horaire format hhmmss
        sec (int): Nombre de secondes à ajouter à l'horaire

    Returns:
        str: horaire au format hhmmss
    """
    hour=int(date[0:2])
    minute=int(date[2:4])
    second=int(date[4:6])
    newSecond=second+sec
    newMinute=minute+int(newSecond/60)
    newHour=hour+int(newMinute/60)
    newSecond%=60
    newMinute%=60
    newHour%=24
    return str(newHour).zfill(2)+str(newMinute).zfill(2)+str(newSecond).zfill(2)

def isADate(date):
    """Renvoie True si la date jj/mm/aa est valide

    Args:
        date (str): Date a valider au format jj/mm/aa

    Returns:
        Bool: Date valide ou pas
    """
    
    return date_re.match(date)


if __name__ == '__main__':
    try:
        sys.argv.index("-nv")
    except ValueError:
        print("🧑 - Programme par \033[35mArthur Perrin - KER72\033[0m")
        print("💙 - Merci de reporter tous bugs à l'adresse suivante:")
        print("📬 - \033[31marthurperrin.22@gmail.com\033[0m")
        print("🔎 - Ajoutez l'argument -nv pour ignorer ce message")
    
    app = QApplication(sys.argv)
    window = MainWindow(sys.argv)
    window.show()
    app.exec()
