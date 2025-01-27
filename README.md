# SaisieMesAbs

Outil de saisie des mesures du champs magnétique terrestre par la méthode des résidus.

![Alt text](./Screen.png?raw=true "Captrue d'écran de l'application")

**⚠ Ce script est approuvé ni par l'IPEV, ni par l'EOST, leur logo sont utilisés pour exemple.**


# Configuration d'une station de mesure

```
[STATION]
#Nom de la station en minuscule
NOM_STATION     = test
#PATH du chemin où enregistrer les mesures,$YY sera remplacé par les deux derniers chiffres de l'année de la mesure et $STATION par le nom de la station en minuscule 
PATH_RE         = /home/$STATION/$STATION$YY/mes-abs/mes-jour  
AZIMUTH_REPERE  = 52.35840

[AUTOCOMPLETE]
AUTO_INC_ANGLE      = 123.----
AUTO_DEC_ANGLE      = 233.----
AUTO_CAL_ANGLE_HAUT = 247.75--
AUTO_CAL_ANGLE_BAS  = 47.75--
SEC_ENTRE_MESURES   = 45
```

---

Made in KER72@TAAF 🇹🇫

By Arthur Perrin
