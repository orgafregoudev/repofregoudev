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
import streamlit as st
from PIL import Image
import matplotlib.patches as mpatches
from matplotlib import cm
import geocoder
from geopy.distance import geodesic
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from deep_translator import GoogleTranslator
import textwrap
import pydeck as pdk
import googlemaps
from datetime import datetime
import requests


# #######################################################################################################################
#                                              # === FUNCTIONS === #
# #######################################################################################################################
def side_bar():
    """Display a side bar for streamlit.
    """
    end = '<p style="font-family:Avenir; font-weight:bold; color:#FCBA28; font-size:12px; ">©2021 Positive Thinking Company et/ou ses affiliés. Tous droits réservés. Produit par le PTC Tech Lab.</p>'
    st.sidebar.markdown("""---""")
    try:
        st.sidebar.image(image1, width=50)
    except Exception as e:
        pass

    st.sidebar.markdown(end, unsafe_allow_html=True)


def get_continent(pays):
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


def get_coordinates(df, dist_amiens_ville):
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


def get_coordinates_truck(ville):
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
    gmaps = googlemaps.Client(key=KEY_GCP)
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


def get_coordinates_boat(coords, dist_amiens_ville):
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


def create_layer(med_lat, med_lon, df_map, dist_amiens_ville, timestamps):
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

# #######################################################################################################################
#                                              # === CONSTANTS === #
# #######################################################################################################################
# True if BRAND, False if not
BRAND = True

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

KEY_GCP = st.secrets["gcp_key"]
KEY_SEAROUTE = st.secrets["searoute_key"]

# #######################################################################################################################
#                                              # === IMPORT DATA === #
# #######################################################################################################################
st.title("Analyse CO2")
st.markdown("""---""")

image1 = Image.open("app_logos/PTCtechLab.png")
image2 = Image.open("app_logos/Brand-Logo.png")
image3 = Image.open("app_logos/PTC.png")

if BRAND:
    st.sidebar.image(image2)
else:
    st.sidebar.image(image3, width=200)

analysis = st.sidebar.selectbox('', ['CO2'])

side_bar()

xls = st.file_uploader("", type=["xls", "xlsx"])


if xls:

    df_base = pd.read_excel(xls, 'BASE')
    df_base = df_base[df_base["Code facteur d'émission"].notna()]
    df_poids = pd.read_excel(xls, 'POIDS AC')
    df_ef = pd.read_excel(xls, 'Emission factors')
    df_fretin_rwm = pd.read_excel(xls, 'FRET IN MP')
    df_fretin_com = pd.read_excel(xls, 'FRET IN AC', header=1)

    st.markdown("""---""")

# #######################################################################################################################
#                                              # === USER INPUT === #
# #######################################################################################################################

    if BRAND:
        list_of_product = [None] + list(df_base['Product'].unique())
    else:
        list_of_product = [None] + list(df_base['Nom simulation'].unique())


    product_name = st.selectbox('Product', list_of_product)
    
    if product_name is not None:
        if BRAND:
            product_number = df_base.loc[df_base["Product"] == product_name, 'Référence Composée (PSPRNO)'].values[0]
            sub_df_base = df_base[df_base['Product'] == product_name]
        else:
            product_number = df_base.loc[df_base["Nom simulation"] == product_name, 'Référence Composée (PSPRNO)'].values[0]
            sub_df_base = df_base[df_base['Nom simulation'] == product_name]
    
        sub_df_base_rwm = sub_df_base[sub_df_base["PSITTY"] == "RWM"]
        sub_df_base_com = sub_df_base[sub_df_base["PSITTY"] == "COM"]
    
        try:
            if BRAND:
                sub_df_base_rwm_name = sub_df_base_rwm['Désignation']
            else:
                sub_df_base_rwm_name = sub_df_base_rwm['Nom simulation2']

        except:
            sub_df_base_rwm_name = sub_df_base_rwm['Désignation']
        
        sub_df_base_com_name = sub_df_base_com['Désignation']
    
        col1, col2, col3 = st.columns(3)
        with col1:
            pays = st.text_input("Quel pays pour l'export", value="Allemagne")
            pays2 = pays
        with col2:
            ville = st.text_input("Quelle ville pour l'export", value="Berlin")
            ville2 = ville
        with col3:
            transport = st.radio('Export type', ['Avion', 'Camion', 'Bateau'])
       
            
            
        if pays and transport:
            translated = GoogleTranslator(source='auto', target='en').translate(pays).title()
            continent = get_continent(translated)
            if (continent in ['OC', 'NA', 'SA', 'Unknown'] and transport == "Camion") or (pays in ['Japon', 'Singapour', 'Indonésie', 'Islande'] and transport == 'Camion'):
                st.error("Il n'est pas possible d'aller en Camion à "+str(ville).title())
                st.stop()

    
# #######################################################################################################################
#                                              # === CALCULATE  === #
# #######################################################################################################################
        if transport and ville and pays:

            # 0 - Process city location
  
            try:
                txt = ville+', '+pays

                g = None
                g = geocoder.osm(txt)
                lat = g.json['lat']
                lon = g.json['lng']
            except TypeError:
                try:
                    txt = ville2+', '+pays2
    
                    g = None
                    g = geocoder.osm(txt)
                    lat = g.json['lat']
                    lon = g.json['lng']
                except TypeError:
                    st.error('Ville ou Pays non reconnu')
                    st.stop()
            except TypeError:
                st.error('Ville ou Pays non reconnu')
                st.stop()


            dist_lh_ville = int(geodesic((LAT_LEHAVRE, LON_LEHAVRE), (lat, lon)).kilometers)
            dist_orly_ville = int(geodesic((LAT_ORLY, LON_ORLY), (lat, lon)).kilometers)
            dist_amiens_ville = int(geodesic((LAT_AMIENS, LON_AMIENS), (lat, lon)).kilometers)
            
    
            all_lat = [LAT_AMIENS]
            all_lon = [LON_AMIENS]
            if transport == 'Bateau':
                all_lat.append(LAT_LEHAVRE)
                all_lon.append(LON_LEHAVRE)
            elif transport == 'Avion':
                all_lat.append(LAT_ORLY)
                all_lon.append(LON_ORLY)
            all_lat.append(lat)
            all_lon.append(lon)
                
            data = {'lat': all_lat, 'lon': all_lon}
            df = pd.DataFrame(data)
    
            with st.expander("Affiche la carte"):
                if transport == 'Camion':
                    try:
                        med_lat, med_lon, df_map, timestamps, distance = get_coordinates_truck(ville)
                        st.pydeck_chart(create_layer(med_lat, med_lon, df_map, dist_amiens_ville, timestamps))
                        dist_amiens_ville = distance
                    except IndexError:
                        st.warning('Calcul du trajet non disponible')
                        st.stop()
                elif transport == 'Avion':
                    med_lat, med_lon, df_map, timestamps = get_coordinates(df, dist_amiens_ville)
                    st.pydeck_chart(create_layer(med_lat, med_lon, df_map, dist_amiens_ville, timestamps))
                    
                elif transport == 'Bateau':
                    st.error("En attente de clé d'activation Sea Route")
                    st.stop()
                    # url = "https://api.searoutes.com/route/v2/sea/0.107929%2C49.49437%3B"+str(lon)+"%2C"+str(lat)+"?continuousCoordinates=true&allowIceAreas=false&avoidHRA=false&avoidSeca=false"
                    # headers = {
                    #     "Accept": "application/json",
                    #     "x-api-key": KEY_SEAROUTE
                    # }
                    
                    # request_sr = requests.request("GET", url, headers=headers)
                    
                    # coords = request_sr.json()['features'][0]['geometry']['coordinates']
                    # coords.insert(0, [LON_AMIENS, LAT_AMIENS])
                    # med_lat, med_lon, df_map, timestamps = get_coordinates_boat(coords, dist_amiens_ville)
                    # st.pydeck_chart(create_layer(med_lat, med_lon, df_map, dist_amiens_ville, timestamps))
                    # dist_lh_ville = request_sr.json()['features'][0]['properties']['distance'] / 1000
                    
            st.markdown("""---""")
            st.subheader("Calcul du Bilan Carbone pour un échantillon")

    
            # 1 -- Calculs de l'emmission pour les production des matières premières et des composants
    
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
    
    
            # 2 -- Calcul de l'emmission pour la fin de vie du contenant
    
            com_emm_fin_vie = []
            for iType in sub_df_base_com["Code facteur d'émission"]:
                if iType == 'CARTON PCR':
                    com_emm_fin_vie.append(CARTON_FIN_DE_VIE_MOYENNE / 1000)
    
                elif iType in ['RPET25', 'PE', 'PP', 'PLA', 'PET', 'POMPE']:
                    com_emm_fin_vie.append(PLASTIQUE_FIN_DE_VIE_MOYENNE / 1000)
    
            com_fin_vie = com_weight * com_emm_fin_vie
            rwm_fin_vie = rwm_weight * 0
    
    
            # 3 -- Calculs de l'emmission pour l'import des matières premières et des composants
    
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
    
    
            # 4 -- Calcul de la production à Pontoise (divisé par le nombre d'item)
    
            nb_item = (len(rwm_weight)+len(com_weight))
    
            rwm_prod_pont = [PRODUCTION_PONTOISE / nb_item] * len(rwm_weight)
            com_prod_pont = [PRODUCTION_PONTOISE / nb_item] * len(com_weight)
    
    
            # 5 -- Calcul de l'emmission pour le transport en France
    
            rwm_fretinter = rwm_weight * DIST_PONTOISE_AMIENS * EMM_ROUTE / 1000
            com_fretinter = com_weight * DIST_PONTOISE_AMIENS * EMM_ROUTE / 1000
    
    
            # 6 -- Calculs de l'emmission pour l'export (par bateau, camion ou avion)
    
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
            
    
# #######################################################################################################################
#                                              # === BILAN CARBONE === #
# #######################################################################################################################

    
            RWM = rwm_prod + rwm_fin_vie + rwm_fretin + rwm_prod_pont + rwm_fretinter + rwm_fretout
            COM = com_prod + com_fin_vie + com_fretin + com_prod_pont + com_fretinter + com_fretout
            
    
            total_score = round((np.sum(RWM) + np.sum(COM)) / 1000, 2)

            if transport == 'Bateau':
                st.markdown("Le bilan carbone d'un flacon/tube de **"+str(product_name)+"** transporté par **"+str(transport)+"** entre **Amiens** et **"+str(ville).title()+"** en passant par **Le Havre** est de :")
            elif transport == 'Avion':
                st.markdown("Le bilan carbone d'un flacon/tube de **"+str(product_name)+"** transporté par **"+str(transport)+"** entre **Amiens** et **"+str(ville).title()+"** en passant par **Orly** est de :")
            elif transport == 'Camion':
                st.markdown("Le bilan carbone d'un flacon/tube de **"+str(product_name)+"** transporté par **"+str(transport)+"** entre **Amiens** et **"+str(ville).title()+"** est de :")

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Bilan Carbone", value=str(total_score)+" kgCO2e", delta=0)
            with col2:
                st.metric(label="Distance totale (import, trajets en France et export)", value=str(total_distance+km_route_rwm.sum()+km_route_com.sum())+" km", delta=0)
            
            st.markdown("""---""")
            st.subheader("Origine des données")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("Matières premières")
                df = pd.DataFrame(sub_df_base_rwm_name)
                df['Origine'] = "M"
                st.dataframe(df)
            with col2:
                st.markdown("Composants du contenant")
                df = pd.DataFrame(sub_df_base_com_name)
                df['Origine'] = "M"
                st.dataframe(df)
            
            st.markdown("""---""")
            
# #######################################################################################################################
#                                              # === PLOTS === #
# #######################################################################################################################
    
            st.subheader('Poids et Répartition des émissions par étape pour un produit fini')
    
            col_1, col_2 = st.columns(2)

            # 8.1 Plot d'un camembert représentant la répartition des matières premières par poids
    
            with col_1:
    
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

                st.pyplot(camembert)

            # 8.2 Répartition des emmission en fonction des étapes

            with col_2:
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
                st.pyplot(barplot_1)
    
            st.markdown("""---""")
            st.subheader('Répartition des émissions totales pour un produit fini')
            col1, col2 = st.columns(2)

            # 8.3 Répartition des émmission dues aux matières premières pour un produit fini
            with col1:
                barplot_2 = plt.figure()
                val = [x / 1000 for x in RWM.values]
                ax = sns.barplot(sub_df_base_rwm_name, val, palette='viridis')

                ax.set_title(product_name+" - Matières Premières")
                ax.set(xlabel=None)
                ax.set_ylabel('KgCO2e')
                ax.set_xticklabels(labels=[textwrap.fill(iLabel, 25) for iLabel in sub_df_base_rwm_name],
                                   rotation=60, fontsize=10, horizontalalignment="right")
                st.pyplot(barplot_2)
    
            # 8.4 Répartition des émmission dus aux composants pour un produit fini
            with col2:
                barplot_3 = plt.figure()
                val = [x / 1000 for x in COM.values]
                ax = sns.barplot(sub_df_base_com_name, val, palette='viridis')
                ax.set_title(product_name+" - Contenant")
                ax.set(xlabel=None)
                ax.set_ylabel('KgCO2e')
                ax.set_xticklabels(labels=[textwrap.fill(iLabel, 25) for iLabel in sub_df_base_com_name],
                                   rotation=60, fontsize=10, horizontalalignment="right")

                st.pyplot(barplot_3)
                

            st.markdown("""---""")
            st.subheader("Répartition des émissions d'un composant par étape pour une pièce")
    
            col1, col2 = st.columns(2)

            with col1:
                rwm = st.radio("Matières premières", list(sub_df_base_rwm_name))
                prod_rwm = list(sub_df_base_rwm_name).index(rwm)
    
            with col2:
                com = st.radio("Composants du contenant", list(sub_df_base_com_name))
                prod_com = list(sub_df_base_com_name).index(com)
    
            col1, col2 = st.columns(2)
    
            # 8.5 Répartition des émmissions pour une matière première
            with col1:
    
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
                st.pyplot(barplot_4)

            # 8.5 Répartition des émmissions pour un élement du contenant choisi
            with col2:
    
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
                st.pyplot(barplot_5)


# #######################################################################################################################
#                                              # === ENF OF FILE === #
# #######################################################################################################################
