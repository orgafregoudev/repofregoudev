#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Oct 13 11:15:33 2021

@author: maximejacoupy
"""

# #######################################################################################################################
#                                              # === LIBRAIRIES === #
# #######################################################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
from matplotlib import cm
import geocoder
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import textwrap
import pydeck as pdk
import googlemaps
from datetime import datetime
from deep_translator import GoogleTranslator


# #######################################################################################################################
#                                              # === FUNCTIONS === #
# #######################################################################################################################
def get_continent(self, pays):
    """Retrieve continent acronyme

    :param pays: country name
    :type pays: str
    :returns cn_continent: continent acronyme or Unknown
    :rtype cn_continent: str
    """
    try:
        cn_a2_code = country_name_to_country_alpha2(pays)
    except:
        cn_a2_code = 'Unknown'
    try:
        cn_continent = country_alpha2_to_continent_code(cn_a2_code)
    except:
        cn_continent = 'Unknown'
    return (cn_continent)


def get_coordinates(self, df, dist_amiens_ville):
    """Extract and prepare data for map creation (for flight)
    :param df: coordinates of beginning and and of the trip
    :type df: dataframe
    :param dist_amiens_ville: direct distance between Amiens and the selected city
    :type dist_amiens_ville: int
    :returns med_lat: latitude of the middle of the distance between Amiens and the selected city
    :rtype med_lat: float
    :returns med_lon: longitude of the middle of the distance between Amiens and the selected city
    :rtype med_lon: float
    :returns df_map: prepared data for map creation
    :rtype df_map: dataframe
    :returns timestamps: each timestamps of the journey
    :rtype timestamps: list of float
    """
    coordinates = []
    timestamps = []
    for iCpt, iVal in enumerate(df.iterrows()):
        lat = iVal[1][0]
        lon = iVal[1][1]
        coordinates.append([lon, lat])
        timestamps.append(iCpt)

    med_lon = np.mean([coordinates[0][0], coordinates[-1][0]])
    med_lat = np.mean([coordinates[0][1], coordinates[-1][1]])
    column_names = ["coordinates", "timestamps"]
    df_map = pd.DataFrame(columns=column_names)
    df_map.loc[0, 'coordinates'] = coordinates
    df_map.loc[0, 'timestamps'] = timestamps
    
    return med_lat, med_lon, df_map, timestamps


def get_coordinates_truck(self, ville, key_gcp):
    """Extract and prepare data for map creation (for truck)
    :param ville: name of the city
    :type ville: str
    :returns med_lat: latitude of the middle of the distance between Amiens and the selected city
    :rtype med_lat: float
    :returns med_lon: longitude of the middle of the distance between Amiens and the selected city
    :rtype med_lon: float
    :returns df_map: prepared data for map creation
    :rtype df_map: dataframe
    :returns timestamps: each timestamps of the journey
    :rtype timestamps: list of float
    """
    gmaps = googlemaps.Client(key=key_gcp)
    now = datetime.now()
    directions_result = gmaps.directions("Amiens",
                                     ville,
                                     mode="driving",
                                     departure_time=now)

    distance = directions_result[0]['legs'][0]['distance']['value'] / 1000
        
    coordinates = []
    timestamps = []
    dic = directions_result[0]['legs'][0]['steps']
    for iLoc in range(len(dic)):
        lat = dic[iLoc]['end_location']['lat']
        lon = dic[iLoc]['end_location']['lng']
        coordinates.append([lon, lat])
        timestamps.append(iLoc)

    med_lon = np.mean([coordinates[0][0], coordinates[-1][0]])
    med_lat = np.mean([coordinates[0][1], coordinates[-1][1]])
    column_names = ["coordinates", "timestamps"]
    df_map = pd.DataFrame(columns=column_names)
    df_map.loc[0, 'coordinates'] = coordinates
    df_map.loc[0, 'timestamps'] = timestamps
    
    return med_lat, med_lon, df_map, timestamps, distance


def get_coordinates_boat(self, coords, dist_amiens_ville):
    """..."""
    coordinates = []
    timestamps = []
    for iCpt, iCoord in enumerate(coords):
        lon = iCoord[0]
        lat = iCoord[1]
        coordinates.append([lon, lat])
        timestamps.append(iCpt)
        
    med_lon = np.mean([coordinates[0][0], coordinates[-1][0]])
    med_lat = np.mean([coordinates[0][1], coordinates[-1][1]])
    column_names = ["coordinates", "timestamps"]
    df_map = pd.DataFrame(columns=column_names)
    df_map.loc[0, 'coordinates'] = coordinates
    df_map.loc[0, 'timestamps'] = timestamps
    
    return med_lat, med_lon, df_map, timestamps


def create_layer(self, med_lat, med_lon, df_map, dist_amiens_ville, timestamps):
    """..."""
    layer = pdk.Layer(
        "TripsLayer",
        df_map,
        get_path="coordinates",
        get_timestamps="timestamps",
        get_color=[253, 128, 93],
        opacity=0.8,
        width_min_pixels=5,
        rounded=True,
        trail_length=dist_amiens_ville,
        current_time=timestamps[-1])
    view_state = pdk.ViewState(latitude=med_lat, longitude=med_lon, zoom=2, bearing=0, pitch=45)

    r = pdk.Deck(layers=[layer],
                 map_style="mapbox://styles/mapbox/light-v10",
                 initial_view_state=view_state)
    
    return r


def translation(self, pays):
    """..."""
    translated = GoogleTranslator(source='auto', target='en').translate(pays).title()
    continent = get_continent(translated)
    return continent


def find_lat_lon(self, ville, pays):
    """..."""
    txt = ville+', '+pays

    g = None
    g = geocoder.osm(txt)
    lat = g.json['lat']
    lon = g.json['lng']
    return lat, lon
# #######################################################################################################################
#                                              # === CONSTANTS === #
# #######################################################################################################################
# True if BRAND, False if not
BRAND = False

POIDS_FLACON_200_ML = 26
CARTON_FIN_DE_VIE_MOYENNE = 37.9
PLASTIQUE_FIN_DE_VIE_MOYENNE = 877

EMM_ROUTE = 0.0956
EMM_AIR = 2.23
EMM_MER = 0.0204

PRODUCTION_PONTOISE = 158

DIST_PONTOISE_AMIENS = 173
DIST_AMIENS_LEHAVRE = 184
DIST_AMIENS_ORLY = 166

LAT_LEHAVRE = 49.4938975
LON_LEHAVRE = 0.1079732

LAT_AMIENS = 49.8941708
LON_AMIENS = 2.2956951

LAT_ORLY = 48.7431683
LON_ORLY = 2.402391


# #######################################################################################################################
#                                              # === IMPORT DATA === #
# #######################################################################################################################
def import_df(self, xls):
    """..."""
    df_base = pd.read_excel(xls, 'BASE')
    df_base = df_base[df_base["Code facteur d'émission"].notna()]
    df_poids = pd.read_excel(xls, 'POIDS AC')
    df_ef = pd.read_excel(xls, 'Emission factors')
    df_fretin_rwm = pd.read_excel(xls, 'FRET IN MP')
    df_fretin_com = pd.read_excel(xls, 'FRET IN AC', header=1)
    return df_base, df_poids, df_ef, df_fretin_rwm, df_fretin_com

# #######################################################################################################################
#                                              # === USER INPUT === #
# #######################################################################################################################


# #######################################################################################################################
#                                              # === CALCULATE  === #
# #######################################################################################################################

# 1 -- Calculs de l'emmission pour les production des matières premières et des composants

def prod_emm(self, sub_df_base_rwm, sub_df_base_com, df_poids, df_ef):
    """..."""
    rwm_weight = pd.to_numeric(sub_df_base_rwm['Quantité (PSCNQT) en Kg'] * 1000, errors='coerce')

    df = sub_df_base_com[['Composant (PSMTNO)', 'Quantité (PSCNQT) en Kg']]
    list_poids_net_unitaires = []
    for iComposant in df['Composant (PSMTNO)']:
        try:
            val = df_poids.loc[df_poids['code AC'] == iComposant, 'poids net unitaire (Kg)'].values[0]
            list_poids_net_unitaires.append(val)
        except IndexError:
            list_poids_net_unitaires.append(POIDS_FLACON_200_ML / 1000)

    df['poids net unitaire (Kg)'] = list_poids_net_unitaires
    df = df.dropna()

    com_weight = pd.to_numeric(df['Quantité (PSCNQT) en Kg'] * df['poids net unitaire (Kg)'] * 1000, errors='coerce')

    rwm_emm_prod = []
    for iType in sub_df_base_rwm["Code facteur d'émission"]:
        try:
            val = df_ef.loc[df_ef["Code facteur d'émission"] == iType, 'Value 2020'].values[0]
            rwm_emm_prod.append(val / 1000)
        except IndexError:
            pass

    com_emm_prod = []
    for iType in sub_df_base_com["Code facteur d'émission"]:
        try:
            val = df_ef.loc[df_ef["Code facteur d'émission"] == iType, 'Value 2020'].values[0]
            com_emm_prod.append(val / 1000)
        except IndexError:
            pass

    rwm_prod = rwm_weight * rwm_emm_prod
    com_prod = com_weight * com_emm_prod

    return rwm_prod, com_prod, rwm_weight, com_weight


# 2 -- Calcul de l'emmission pour la fin de vie du contenant

def fin_vie(self, sub_df_base_com, com_weight, rwm_weight):
    """..."""
    com_emm_fin_vie = []
    for iType in sub_df_base_com["Code facteur d'émission"]:
        if iType == 'CARTON PCR':
            com_emm_fin_vie.append(CARTON_FIN_DE_VIE_MOYENNE / 1000)

        elif iType in ['RPET25', 'PE', 'PP', 'PLA', 'PET', 'POMPE']:
            com_emm_fin_vie.append(PLASTIQUE_FIN_DE_VIE_MOYENNE / 1000)

    com_fin_vie = com_weight * com_emm_fin_vie
    rwm_fin_vie = rwm_weight * 0

    return com_fin_vie, rwm_fin_vie


# 3 -- Calculs de l'emmission pour l'import des matières premières et des composants
def emmission_com_rwm(self, sub_df_base_rwm, df_fretin_rwm, sub_df_base_com, df_fretin_com, rwm_weight, com_weight):
    """..."""
    km_mer_rwm = []
    for iComposant in sub_df_base_rwm['Composant (PSMTNO)']:
        try:
            val = df_fretin_rwm.loc[df_fretin_rwm["Code MP"] == iComposant, 'Distance KM SEA'].values[0]
            km_mer_rwm.append(val)
        except IndexError:
            km_mer_rwm.append(0)
    km_mer_rwm = pd.to_numeric(km_mer_rwm, errors='coerce')

    km_air_rwm = []
    for iComposant in sub_df_base_rwm['Composant (PSMTNO)']:
        try:
            val = df_fretin_rwm.loc[df_fretin_rwm["Code MP"] == iComposant, 'Distance KM  AIR'].values[0]
            km_air_rwm.append(val)
        except IndexError:
            km_air_rwm.append(0)
    km_air_rwm = pd.to_numeric(km_air_rwm, errors='coerce')

    km_route_rwm = []
    for iComposant in sub_df_base_rwm['Composant (PSMTNO)']:
        try:
            val1 = df_fretin_rwm.loc[df_fretin_rwm["Code MP"] == iComposant, 'PRE CARRIAGE Road KM'].values[0]
            val2 = df_fretin_rwm.loc[df_fretin_rwm["Code MP"] == iComposant, 'POST CARRIAGE Road KM'].values[0]
            val3 = df_fretin_rwm.loc[df_fretin_rwm["Code MP"] == iComposant, 'Delivery KM - 180'].values[0]
            km_route_rwm.append(val1+val2+val3)
        except IndexError:
            km_route_rwm.append(0)

    km_route_rwm = pd.to_numeric(km_route_rwm, errors='coerce')

    km_route_com = []
    for iCode in sub_df_base_com['Fournisseur principal']:
        try:
            val = df_fretin_com.loc[df_fretin_com["Code fournisseur"] == iCode, 'Distances KM en France du fournisseur vers Pontoise'].values[0]
            km_route_com.append(val)
        except IndexError:
            pass
    km_route_com = pd.to_numeric(km_route_com, errors='coerce')

    rwm_fretin = rwm_weight * (km_route_rwm * EMM_ROUTE + km_air_rwm * EMM_AIR + km_mer_rwm * EMM_MER) / 1000
    com_fretin = com_weight * (km_route_com * EMM_ROUTE) / 1000

    return rwm_fretin, com_fretin, km_route_rwm, km_route_com


# 4 -- Calcul de la production à Pontoise (divisé par le nombre d'item)
def pontoise(self, rwm_weight, com_weight):
    """..."""
    nb_item = (len(rwm_weight)+len(com_weight))

    rwm_prod_pont = [PRODUCTION_PONTOISE / nb_item] * len(rwm_weight)
    com_prod_pont = [PRODUCTION_PONTOISE / nb_item] * len(com_weight)
    return rwm_prod_pont, com_prod_pont, nb_item


# 5 -- Calcul de l'emmission pour le transport en France
def emm_fret_in(self, rwm_weight, com_weight):
    """..."""
    rwm_fretinter = rwm_weight * DIST_PONTOISE_AMIENS * EMM_ROUTE / 1000
    com_fretinter = com_weight * DIST_PONTOISE_AMIENS * EMM_ROUTE / 1000
    return rwm_fretinter, com_fretinter


# 6 -- Calculs de l'emmission pour l'export (par bateau, camion ou avion)
def export(dist_lh_ville, dist_orly_ville, dist_amiens_ville, transport, rwm_weight, com_weight, nb_item):
    """..."""
    fo_route_1 = DIST_AMIENS_LEHAVRE * EMM_ROUTE / 1000
    fo_route_2 = DIST_AMIENS_ORLY * EMM_ROUTE / 1000
    fo_mer = dist_lh_ville * EMM_MER / 1000
    fo_air = dist_orly_ville * EMM_AIR / 1000
    fo_route_3 = dist_amiens_ville * EMM_ROUTE / 1000

    if transport == "Bateau":
        prod_fretout = (np.sum(rwm_weight) + np.sum(com_weight)) * (fo_route_1 + fo_mer)
        total_distance = int(DIST_AMIENS_LEHAVRE + dist_lh_ville)
    elif transport == "Avion":
        prod_fretout = (np.sum(rwm_weight) + np.sum(com_weight)) * (fo_route_2 + fo_air)
        total_distance = int(DIST_AMIENS_ORLY + dist_orly_ville)
    elif transport == "Camion":
        prod_fretout = (np.sum(rwm_weight) + np.sum(com_weight)) * (fo_route_3)
        total_distance = int(dist_amiens_ville)

    rwm_fretout = [prod_fretout / nb_item] * len(rwm_weight)
    com_fretout = [prod_fretout / nb_item] * len(com_weight)
    return rwm_fretout, com_fretout, total_distance


# #######################################################################################################################
#                                              # === PLOTS === #
# #######################################################################################################################


# 8.1 Plot d'un camembert représentant la répartition des matières premières par poids

def camembert(self, sub_df_base_rwm_name, rwm_weight):
    """..."""
    camembert = plt.figure(figsize=(8, 8))
    labels = list(sub_df_base_rwm_name)
    sizes = rwm_weight.values
    color_pal = cm.viridis(np.arange(len(sizes))/(len(sizes)))

    patches, texts = plt.pie(sizes, startangle=90, colors=color_pal)
    plt.legend(patches, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05),
        fancybox=True, shadow=False, ncol=3)
    plt.axis('equal')
    plt.tight_layout()
    plt.title("Proportion du poids des matières premières", fontsize=20)
    plt.show()

    return camembert


# 8.2 Répartition des emmission en fonction des étapes
def barplot_step(self, rwm_prod, rwm_fin_vie, rwm_fretin, com_prod, com_fin_vie, com_fretin, rwm_prod_pont, com_prod_pont, rwm_fretinter, com_fretinter, rwm_fretout, com_fretout, product_name):
    """..."""
    list_of_em_rwm = [np.sum(rwm_prod), np.sum(rwm_fin_vie), np.sum(rwm_fretin), 0, 0, 0]
    list_of_em_rwm = [x / 1000 for x in list_of_em_rwm]
    list_of_em_com = [np.sum(com_prod), np.sum(com_fin_vie), np.sum(com_fretin), 0, 0, 0]
    list_of_em_com = [x / 1000 for x in list_of_em_com]
    list_of_final_product = [0, 0, 0, (np.sum(rwm_prod_pont)+np.sum(com_prod_pont)), (np.sum(rwm_fretinter)+np.sum(com_fretinter)), (np.sum(rwm_fretout)+np.sum(com_fretout))]
    list_of_final_product = [x / 1000 for x in list_of_final_product]


    names = ['PRODUCTION', 'FIN DE VIE', 'FRET IN', 'PRODUCTION PONTOISE', 'FRET INTER', 'FRET OUT']
    barplot_1 = plt.figure()
    ax0 = sns.barplot(names, list_of_final_product, color=[0.172549, 0.454901, 0.549019, 1])
    ax1 = sns.barplot(names, list_of_em_rwm, color=[0.783315, 0.879285, 0.125405, 1])
    ax2 = sns.barplot(names, list_of_em_com, color=[0.267004, 0.004874, 0.329415, 1])
    ax2.set_xticklabels(labels=[textwrap.fill(iLabel, 25) for iLabel in names],
                       rotation=60, fontsize=10, horizontalalignment="right")
    ax2.set_title(product_name)
    ax2.set_ylabel('KgCO2e')

    top_bar = mpatches.Patch(color=[0.783315, 0.879285, 0.125405, 1], label='Matières premières')
    middle_bar = mpatches.Patch(color=[0.267004, 0.004874, 0.329415, 1], label='Contenant')
    bottom_bar = mpatches.Patch(color=[0.172549, 0.454901, 0.549019, 1], label='Produit fini')
    barplot_1.legend(handles=[top_bar, middle_bar, bottom_bar], loc='upper center', bbox_to_anchor=(0.5, -0.30),
      fancybox=True, shadow=False, ncol=3)

    return barplot_1


# 8.3 Répartition des émmission dues aux matières premières pour un produit fini
def barplot_rwm(self, sub_df_base_rwm_name, RWM, product_name):
    """..."""
    barplot_2 = plt.figure()
    val = [x / 1000 for x in RWM.values]
    ax = sns.barplot(sub_df_base_rwm_name, val, palette='viridis')

    ax.set_title(product_name+" - Matières Premières")
    ax.set(xlabel=None)
    ax.set_ylabel('KgCO2e')
    ax.set_xticklabels(labels=[textwrap.fill(iLabel, 25) for iLabel in sub_df_base_rwm_name],
                       rotation=60, fontsize=10, horizontalalignment="right")
    return barplot_2


    # 8.4 Répartition des émmission dus aux composants pour un produit fini
def barplot_com(self, sub_df_base_com_name, COM, product_name):
    """..."""
    barplot_3 = plt.figure()
    val = [x / 1000 for x in COM.values]
    ax = sns.barplot(sub_df_base_com_name, val, palette='viridis')
    ax.set_title(product_name+" - Contenant")
    ax.set(xlabel=None)
    ax.set_ylabel('KgCO2e')
    ax.set_xticklabels(labels=[textwrap.fill(iLabel, 25) for iLabel in sub_df_base_com_name],
                       rotation=60, fontsize=10, horizontalalignment="right")
    return barplot_3


# 8.5 Répartition des émmissions pour une matière première
def barplot_one_rwm(self, prod_rwm, rwm_prod, rwm_fin_vie, rwm_fretin, rwm_prod_pont, rwm_fretinter, rwm_fretout, sub_df_base_rwm_name):
    """..."""
    values = [rwm_prod.iloc[prod_rwm], rwm_fin_vie.iloc[prod_rwm],
              rwm_fretin.iloc[prod_rwm], rwm_prod_pont[prod_rwm],
              rwm_fretinter.iloc[prod_rwm], rwm_fretout[prod_rwm]]
    values = [x / 1000 for x in values]
    names = ['PRODUCTION', 'FIN DE VIE', 'FRET IN', 'PRODUCTION PONTOISE', 'FRET INTER', 'FRET OUT']

    barplot_4 = plt.figure(figsize=(6, 3.5))
    ax = sns.barplot(names, values, palette='viridis')
    ax.set_xticklabels(labels=[textwrap.fill(iLabel, 25) for iLabel in names],
                       rotation=60, fontsize=10, horizontalalignment="right")
    ax.set_title(sub_df_base_rwm_name.iloc[prod_rwm])
    ax.set(xlabel=None)
    ax.set_ylabel('KgCO2e')
    return barplot_4


# 8.5 Répartition des émmissions pour un élement du contenant choisi
def barplot_one_com(self, prod_com, com_prod, com_fin_vie, com_fretin, com_prod_pont, com_fretinter, com_fretout, sub_df_base_com_name):
    """..."""
    values = [com_prod.iloc[prod_com], com_fin_vie.iloc[prod_com],
              com_fretin.iloc[prod_com], com_prod_pont[prod_com],
              com_fretinter.iloc[prod_com], com_fretout[prod_com]]
    values = [x / 1000 for x in values]
    names = ['PRODUCTION', 'FIN DE VIE', 'FRET IN', 'PRODUCTION PONTOISE', 'FRET INTER', 'FRET OUT']

    barplot_5 = plt.figure(figsize=(6, 3.5))
    ax = sns.barplot(names, values, palette='viridis')
    ax.set_xticklabels(labels=[textwrap.fill(iLabel, 25) for iLabel in names],
                       rotation=60, fontsize=10, horizontalalignment="right")
    ax.set_title(sub_df_base_com_name.iloc[prod_com])
    ax.set(xlabel=None)
    ax.set_ylabel('KgCO2e')
    return barplot_5


# #######################################################################################################################
#                                              # === ENF OF FILE === #
# #######################################################################################################################
