import streamlit as st
for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os
path = os.path.dirname(__file__)
my_file = path+'/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='CEA NASA Results - Rocket Nozzle Sizing',
    page_icon=img
                   )

st.sidebar.image(img)
st.sidebar.markdown("[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@Mechub?sub_confirmation=1) [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/GitMechub)")

hide_menu = '''
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        '''
st.markdown(hide_menu, unsafe_allow_html=True)

import pandas as pd

from rocketcea.cea_obj import add_new_fuel, add_new_oxidizer

from rocketcea.cea_obj import CEA_Obj

try:
    st.header("CEA Results", anchor=False, divider='gray')
    initial_params = st.session_state['initial_params']
    ispObj = st.session_state['IsoObj']
    OF = st.session_state['OF']
    P_1 = st.session_state['P_1']
    P_3 = st.session_state['P_3']

    dadosCEA = ispObj.get_full_cea_output( Pc=P_1*1e-5, MR=OF, eps=initial_params['eps'], PcOvPe=P_1/P_3, frozen=1, frozenAtThroat=1, pc_units='bar')
    st.download_button("Download NASA's CEA Full Output", str(dadosCEA))

except:
    st.markdown("Click on 'Run'")
    pass