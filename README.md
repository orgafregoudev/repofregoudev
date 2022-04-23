# Carbon_Footprint_Calculator

## Définition
L'application a pour objectif de mesurer l'Impact Carbone d'un produit
Sont pris en compte : 
- La production des matières premières et des éléments du contenant
- La fin de vie des éléments du contenant
- L'import des matières premières et des éléments du contenant
- Le coût de production et d'assemblage en France
- Le transport en France du produit fini
- L'export du produit fini 
 
## Description

### Drag and Drop du fichier de données
Dans un souci de protection des données, les données ne sont pas stockées sur le *repository*. Il faut donc dans un premier temps importer le fichier contenant les données sous format .xls ou .xlsx.

### Choix du produit
L'étape suivante est de sélectionner le produit d'intérêt.

### Choix de la ville pour l'export
L'étape suivante est de sélectionner la ville et le pays ou seront livrés le produit d'intérêt/

### Choix du type d'export
Trois possibilités implémentées :
- Par avion
- Par bateau (actuellement indisponible pour des raisons de clé d'identification).
  > Les données de distance proviennent de l'API SeaRoute
- Par camion
  > Les données de distance proviennent de l'API Google Map
  >
  > Il n'est pas possible d'aller sur une ile ou de traverser les océans.
  >
  > A l'heure actuelle, l'Amérique du Nord, l'Amérique du Sud, l'Océanie, le Japon, Singapour, l'Indonésie et l'Islande ne sont pas disponibles.

S'affichent alors une carte de la route utilisée la plus probable
> Les calculs de distances précis sont générés en arrière-plan
  
### Calcul du Bilan Carbone pour un échantillon
Deux mesures apparaissent :
- Le Bilan Carbone (score d'équivalent CO2 émis en kg)
- La Distance Totale en km comprenant :
  - L'import de chaque matière première et de chaque élément du contenant 
  - le transport en France
  - L'export 
> les flèches vertes représenteront à terme la différence entre le produit étudié/tracé et la moyenne annuelle/biannuelle de l'ensemble de ces produits. 

### Origines des données
Pour les matières premières et les éléments du contenant seront affichés :
- M si les données proviennent de données moyennes
- T si les données proviennent des données de traçabilité

### Poids des matières premières
Le camembert affiche la proportion du poids des matières première dans le produit fini sélectionné 

### Répartition des émissions par étape pour un produit fini
Le diagramme en barre représente l'impact carbone des différentes étapes de sa création pour un produit fini.
Sont respectivement représentés les matières premières en vert et les elements du contenant en violet pour les étapes 1 à 3. 
A partir de la production en France, les calculs sont faits à l'échelle du produit et sont représentés en turquoise. 

### Répartition des émissions totales pour un produit fini
Les deux graphiques suivants représentent la proportion des émissions due à chaque matière première (panel de gauche) et à chaque élément du contenant (panel de droite).
> Les données de consommation proviennent de l'ADEME, de la SEPPIC ou d'Ecoinvent
>
> A l'heure actuelle, l'eau purifiée est considérée comme un produit chimique et est souvent la matière la plus émettrice car la plus présente en termes de poids.

### Répartition des émissions d'un composant par étape pour une pièce
Il est possible de regarder la répartition des émissions par étape pour chaque matière première ou pour chaque élément du contenant. 

## Contenu du Git

### Le Git doit absolument contenir les éléments suivants :
- le dossier App contenant :
  - le fichier Carbon_Footprint_Calculator.py (l'application).
- un fichier requirements.txt contenant :
  ```ruby
  openpyxl==3.0.9
  matplotlib==3.3.2
  seaborn==0.11.0
  geocoder==1.37
  geopy==2.2.0
  deep-translator==1.5.4
  pycountry-convert==0.7.2
  googlemaps==4.5.3
  ```
  
### Il peut également contenir :
 - Le dossier app_logos à la racine contenant les logos à afficher 
 - Un dossier .streamlit contenant un fichier .config.toml avec le contenu suivant :  
    ```ruby

    [theme]

    # The preset Streamlit theme that your custom theme inherits from. One of "light" or "dark".
    base = "light"

    # Primary accent color for interactive elements.
    primaryColor = "#******"

    # Background color for the main content area.
    #backgroundColor =

    # Background color used for the sidebar and most interactive widgets.
    secondaryBackgroundColor = "#******"

    # Color used for almost all text.
    textColor = "#******"

    # Font family for all text in the app, except code blocks. One of "sans serif", "serif", or "monospace".
    #font =
    ```
    > "#******" --> A compléter avec les couleurs choisies 

## Déploiement sur Streamlit

### 1. Création d'un compte
Tout d'abord il faut créer un compte sur <https://share.streamlit.io/>
  > la version "*Community*" autorise 3 applications mais qui doivent se trouver sur un *repository* Git publique.
  >
  > La version "*Teams*" coute 250$ mensuel et permet le déploiement de 10 applications privées. 


### 2. Ajout d'une nouvelle App
- Cliquer sur *New app*
- Sélectionner le *repository* git 
- Sélectionner la branche
- Sélectionner l'application à déployer 
- Cliquer sur *deploy*

### 3. Une fois l'application déployée
- Revenir sur <https://share.streamlit.io/> et se connecter
- Cliquer sur les ... verticaux à droite du nom de l'app 
- Cliquer sur *settings*
- Cliquer sur *secrets*
- Remplir les champs suivants :
    - gcp_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    - searoute_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

## Spécificité
Dans le fichier .py si BRAND = *False* alors les noms des produits seront modifiés, si BRAND = *True*, les noms des produits seront réels

# Duplicates_Identificator.py

## Définition
L'application a pour objectif d'identifier les duplicates mais avec des numero de lot MP différents

## Description

### Drag and drop
Il faut importer le fichier M3

### Export
Possitibilité d'exporter le dataframe sous format .csv

## Contenu du Git

### Le Git doit absolument contenir les éléments suivants :
- le dossier App contenant :
  - le fichier Duplicates_Identificator.py (l'application).
  
### Il peut également contenir :
 - Le dossier app_logos à la racine contenant les logos à afficher 
 - Un dossier .streamlit contenant un fichier .config.toml avec le contenu suivant :  
    ```ruby

    [theme]

    # The preset Streamlit theme that your custom theme inherits from. One of "light" or "dark".
    base = "light"

    # Primary accent color for interactive elements.
    primaryColor = "#******"

    # Background color for the main content area.
    #backgroundColor =

    # Background color used for the sidebar and most interactive widgets.
    secondaryBackgroundColor = "#******"

    # Color used for almost all text.
    textColor = "#******"

    # Font family for all text in the app, except code blocks. One of "sans serif", "serif", or "monospace".
    #font =
    ```
    > "#******" --> A compléter avec les couleurs choisies 
