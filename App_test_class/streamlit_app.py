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
import streamlit as st
from PIL import Image
from geopy.distance import geodesic
import Carbon_Footprint_Calculator as cfc


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

# #######################################################################################################################
#                                              # === CONSTANTS === #
# #######################################################################################################################
# True if BRAND, False if not
BRAND = False

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

    df_base, df_poids, df_ef, df_fretin_rwm, df_fretin_com = cfc.import_df(xls)

    st.markdown("""---""")

# #######################################################################################################################
#                                              # === USER INPUT === #
# #######################################################################################################################

    list_of_product = [None] + list(df_base['Nom simulation'].unique())


    product_name = st.selectbox('Product', list_of_product)
    
    if product_name is not None:
        product_number = df_base.loc[df_base["Nom simulation"] == product_name, 'Référence Composée (PSPRNO)'].values[0]
        sub_df_base = df_base[df_base['Nom simulation'] == product_name]
    
        sub_df_base_rwm = sub_df_base[sub_df_base["PSITTY"] == "RWM"]
        sub_df_base_com = sub_df_base[sub_df_base["PSITTY"] == "COM"]
    
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
            continent = cfc.translation(pays)
            if (continent in ['OC', 'NA', 'SA', 'Unknown'] and transport == "Camion") or (pays in ['Japon', 'Singapour', 'Indonésie', 'Islande'] and transport == 'Camion'):
                st.error("Il n'est pas possible d'aller en Camion à "+str(ville).title())
                st.stop()

    
# #######################################################################################################################
#                                              # === CALCULATE  === #
# #######################################################################################################################
        if transport and ville and pays:

            # 0 - Process city location
  
            try:
                lat, lon = cfc.find_lat_lon(ville, pays)

            except TypeError:
                try:
                    lat, lon = cfc.find_lat_lon(ville2, pays2)
                except TypeError:
                    st.error('Ville ou Pays non reconnu')
                    st.stop()
            except TypeError:
                st.error('Ville ou Pays non reconnu')
                st.stop()


            dist_lh_ville = int(geodesic((cfc.LAT_LEHAVRE, cfc.LON_LEHAVRE), (lat, lon)).kilometers)
            dist_orly_ville = int(geodesic((cfc.LAT_ORLY, cfc.LON_ORLY), (lat, lon)).kilometers)
            dist_amiens_ville = int(geodesic((cfc.LAT_AMIENS, cfc.LON_AMIENS), (lat, lon)).kilometers)
            
    
            all_lat = [cfc.LAT_AMIENS]
            all_lon = [cfc.LON_AMIENS]
            if transport == 'Bateau':
                all_lat.append(cfc.LAT_LEHAVRE)
                all_lon.append(cfc.LON_LEHAVRE)
            elif transport == 'Avion':
                all_lat.append(cfc.LAT_ORLY)
                all_lon.append(cfc.LON_ORLY)
            all_lat.append(lat)
            all_lon.append(lon)
                
            data = {'lat': all_lat, 'lon': all_lon}
            df = pd.DataFrame(data)
    
            with st.expander("Affiche la carte"):
                if transport == 'Camion':
                    try:
                        med_lat, med_lon, df_map, timestamps, distance = cfc.get_coordinates_truck(ville)
                        st.pydeck_chart(cfc.create_layer(med_lat, med_lon, df_map, dist_amiens_ville, timestamps))
                        dist_amiens_ville = distance
                    except IndexError:
                        st.warning('Calcul du trajet non disponible')
                        st.stop()
                elif transport == 'Avion':
                    med_lat, med_lon, df_map, timestamps = cfc.get_coordinates(df, dist_amiens_ville)
                    st.pydeck_chart(cfc.create_layer(med_lat, med_lon, df_map, dist_amiens_ville, timestamps))
                    
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
            rwm_prod, com_prod, rwm_weight, com_weight = cfc.prod_emm(sub_df_base_rwm, sub_df_base_com, df_poids, df_ef)

            # 2 -- Calcul de l'emmission pour la fin de vie du contenant
            com_fin_vie, rwm_fin_vie = cfc.fin_vie(sub_df_base_com, com_weight, rwm_weight)
    
            # 3 -- Calculs de l'emmission pour l'import des matières premières et des composants
            rwm_fretin, com_fretin, km_route_rwm, km_route_com = cfc.emmission_com_rwm(sub_df_base_rwm, df_fretin_rwm, sub_df_base_com, df_fretin_com, rwm_weight, com_weight)
    
            # 4 -- Calcul de la production à Pontoise (divisé par le nombre d'item)
            rwm_prod_pont, com_prod_pont, nb_item = cfc.pontoise(rwm_weight, com_weight)
    
            # 5 -- Calcul de l'emmission pour le transport en France
            rwm_fretinter, com_fretinter = cfc.emm_fret_in(rwm_weight, com_weight)
    
            # 6 -- Calculs de l'emmission pour l'export (par bateau, camion ou avion)
            rwm_fretout, com_fretout, total_distance = cfc.export(dist_lh_ville, dist_orly_ville, dist_amiens_ville, transport, rwm_weight, com_weight, nb_item)

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
                camembert = cfc.camembert(sub_df_base_rwm_name, rwm_weight)
                st.pyplot(camembert)

            # 8.2 Répartition des emmission en fonction des étapes

            with col_2:
                barplot_1 = cfc.barplot_step(rwm_prod, rwm_fin_vie, rwm_fretin, com_prod, com_fin_vie, com_fretin, rwm_prod_pont, com_prod_pont, rwm_fretinter, com_fretinter, rwm_fretout, com_fretout, product_name)
                st.pyplot(barplot_1)
    
            st.markdown("""---""")
            st.subheader('Répartition des émissions totales pour un produit fini')
            col1, col2 = st.columns(2)

            # 8.3 Répartition des émmission dues aux matières premières pour un produit fini
            with col1:
                barplot_2 = cfc.barplot_rwm(sub_df_base_rwm_name, RWM, product_name)
                st.pyplot(barplot_2)
    
            # 8.4 Répartition des émmission dus aux composants pour un produit fini
            with col2:
                barplot_3 = cfc.barplot_com(sub_df_base_com_name, COM, product_name)
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
                barplot_4 = cfc.barplot_one_rwm(prod_rwm, rwm_prod, rwm_fin_vie, rwm_fretin, rwm_prod_pont, rwm_fretinter, rwm_fretout, sub_df_base_rwm_name)
                st.pyplot(barplot_4)

            # 8.5 Répartition des émmissions pour un élement du contenant choisi
            with col2:
                barplot_5 = cfc.barplot_one_com(prod_com, com_prod, com_fin_vie, com_fretin, com_prod_pont, com_fretinter, com_fretout, sub_df_base_com_name)
                st.pyplot(barplot_5)


# #######################################################################################################################
#                                              # === ENF OF FILE === #
# #######################################################################################################################
