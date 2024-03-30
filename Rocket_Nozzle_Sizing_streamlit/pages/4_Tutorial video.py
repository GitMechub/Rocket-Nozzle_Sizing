import streamlit as st
from streamlit_player import st_player
for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os
path = os.path.dirname(__file__)
my_file = path+'/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='Tutorial - Rocket Nozzle Sizing',
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

st.header("Tutorial: Rocket Nozzle Sizing v1.0.0", divider="gray", anchor=False, help=" 1:24 - 2:12")
st_player("https://www.youtube.com/watch?v=Crxc9OeuSTg")

st.header("Tutorial: 3D CAD for the nozzle", divider="gray", anchor=False, help="How to use this code to design a free 3D CAD of the nozzle")
st_player("https://www.youtube.com/watch?v=XwzFDo7mbuQ")

