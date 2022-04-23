#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 17:15:19 2021

@author: maximejacoupy
"""

# #######################################################################################################################
#                                              # === LIBRAIRIES === #
# #######################################################################################################################
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import base64


# #######################################################################################################################
#                                              # === FUNCTIONS === #
# #######################################################################################################################


def side_bar():
    """..."""
    end = '<p style="font-family:Avenir; font-weight:bold; color:#FCBA28; font-size:12px; ">©2021 Positive Thinking Company et/ou ses affiliés. Tous droits réservés. Produit par le PTC Tech Lab.</p>'
    st.sidebar.markdown("""---""")
    st.sidebar.image(image1, width=50)
    st.sidebar.markdown(end, unsafe_allow_html=True)
# -------------------------------------------------------------------------- #


# -------------------------------------------------------------------------- #

# #######################################################################################################################
#                                              # === PROCESS NEW FILE === #
# #######################################################################################################################
st.title("Clarins")
st.markdown("""---""")

image1 = Image.open("app_logos/PTCtechLab.png")
image2 = Image.open("app_logos/PTC.png")
st.sidebar.image(image2, width=200)


analysis = st.sidebar.selectbox('', ['[1] Num_Lot_MP_Clarins Error'])
                                
    
if analysis == "[1] Num_Lot_MP_Clarins Error":
    st.header('Num_Lot_MP_Clarins Error')

    side_bar()   
    
    sheet = st.file_uploader("", type=["xls", "xlsx"])
    if sheet:
        try:
            df = pd.read_csv(sheet, sep=';', error_bad_lines=False)
        except:
            df = pd.read_excel(sheet)
    
        df2 = df[df.duplicated(subset=['Num_Lot_PF', 'Num_Lot_MP_Fournisseur','Num OA', 'Ligne OA', 'Sous Ligne OA'], keep=False)]
        
        lot_mpf = df2['Num_Lot_MP_Fournisseur'].unique()
        
        list_of_error = []
        for iVal in lot_mpf:
            t = df2[df2['Num_Lot_MP_Fournisseur'] == iVal]
            length_a = len(t)
            length_b = t['Num_Lot_MP_Clarins'].nunique()
            names = t['Num_Lot_MP_Clarins'].unique()  
            
            print(iVal, length_a, length_b, names)
            
            if len(names) > 1:
                list_of_error.append(names)
            l = np.concatenate(list_of_error)
            
        
        df_final = df2[df2['Num_Lot_MP_Clarins'].isin(l)][["Num_Lot_MP_Clarins", 'Num_Lot_MP_Fournisseur','Num OA', 'Ligne OA', 'Sous Ligne OA']]
        
        
        df_final = df_final.drop_duplicates()
        st.write(df_final)       
    
        @st.cache
        def convert_df(df):
            return df.to_csv().encode('utf-8')

        csv = convert_df(df_final)
        
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='error_export.csv',
            mime='text/csv')
        
        
