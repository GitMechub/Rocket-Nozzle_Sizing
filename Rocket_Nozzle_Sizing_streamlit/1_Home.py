import streamlit as st
st.session_state.update(st.session_state)
for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os
path = os.path.dirname(__file__)
my_file = path+'/pages/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='Setup - Rocket Nozzle Sizing',
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

from rocketcea.cea_obj import add_new_fuel, add_new_oxidizer

from rocketcea.cea_obj_w_units import CEA_Obj

from pylab import *

import numpy as np

import pandas as pd

import math

from math import sin

import matplotlib.pyplot as plt

import plotly.graph_objects as go

st.title("Rocket Nozzle Sizing v1.0.0", anchor=False)
st.subheader("Setup", divider="gray", anchor=False)

#SETUP

if 'active_page' not in st.session_state:
    st.session_state.active_page = '1_Home'
    st.session_state.p_3 = 101325.0
    st.session_state.p_1 = 3000000.0
    st.session_state.f = 1750.0
    st.session_state.method = 1
    st.session_state.spike_detail = 0
    st.session_state.f_name = 'Paraffin'
    st.session_state.o_name = 'N2O'
    st.session_state.of = 7.6

P_3 = st.number_input(
    label='Ambient pressure',
    format="%f",
    step=1.,
    key='p_3',
    help="Ambient pressure in N/m²"
)

P_1 = st.number_input(
    label='Chamber pressure',
    min_value=P_3,
    format="%f",
    step=1.,
    key='p_1',
    help="Chamber pressure in N/m²"
)

F = st.number_input(
    label='Desired thrust',
    min_value=0.,
    format="%f",
    step=100.,
    key='f',
    help="Thrust in Newtons"
)

Method = st.radio('Spike nozzle contour method', [1,2], help='1: [6][7] Method  |  2: [8][9] Method', key='method')

spike_detail = st.checkbox('For a more refined spike nozzle contour curve', key='spike_detail')

F_name = st.selectbox('Fuel', ['A50', 'Acetylene', 'AL', 'AP', 'B2H6', 'C2H2', 'C2H5OH', 'C2H6', 'C2H6_167', 'C3H8', 'CFx', 'CH3OH', 'CH4', 'CINCH', 'DMAZ', 'ECP_dimer', 'Ethanol', 'Gasoline', 'GCH4', 'GH2', 'GH2_160', 'H2', 'H2O', 'HTPB', 'Isopropanol', 'JetA', 'JP10', 'JP4', 'JPX', 'Kerosene', 'Kerosene90_H2O10', 'LCH4_NASA', 'LH2', 'M20', 'M20_NH3', 'Methanol', 'MHF3', 'MMH', 'N2H4', 'NH3', 'NITROMETHANE', 'Propane', 'Propylene', 'RP1', 'UDMH', 'Paraffin'],
                      key='f_name',
                      help='Select the fuel for the bipropellant system'
)

O_name = st.selectbox(
    'Oxidizer', ['90_H2O2', '98_H2O2', 'AIR', 'AIRSIMP', 'CLF3', 'CLF5', 'F2', 'GO2', 'H2O', 'H202', 'HAN315', 'HNO3', 'IRFNA', 'LO2', 'MON15', 'MON25', 'MON3', 'N2F4', 'N2H4', 'N2O', 'N2O3', 'N2O4', 'N2O_nbp', 'O2', 'OF2', 'Peroxide90', 'Peroxide98'],
    key='o_name',
    help="Select the oxidizer for the bipropellant system"
)

OF = st.number_input(
    label='Mixture ratio',
    min_value=0.,
    format="%f",
    step=1.,
    key='of',
    help="Oxidizer-to-fuel mass ratio in the combustion chamber"
)
prop_num = 2

st.session_state['OF'] = OF
st.session_state['P_1'] = P_1
st.session_state['P_3'] = P_3

run_button = st.button("Run")

if run_button:

    # Adding new propellants (CEA NASA):

    ##  Adicionando Parafina e N2O no CEA:

    custom_options = []

    card_str = """
    fuel C20H42(S)  C 20.0   H 42.0    wt%=100.00
    h,cal=-142242.1     t(k)=298.15   rho=788.6
    """
    p_name = 'Paraffin'
    add_new_fuel(p_name, card_str)
    custom_options.append(p_name)

    card_str = """
    oxid NitrousOxide  N 2.0 O 1.0  wt%=100.00
    h,cal= 19467.0 t(k)=298.15
    """
    p_name = 'N2O_custom'
    add_new_oxidizer(p_name, card_str)
    custom_options.append(p_name)


    ###

    def calculate_initial_parameters(Prop, P_1, OF, P_3, F):

        # Calculated Parameters:

        eps = Prop.get_eps_at_PcOvPe(Pc=P_1, MR=OF, PcOvPe=P_1/101325, frozen=1, frozenAtThroat=1)  # Nozzle Expansion Area Ratio
        c_star = Prop.get_Cstar(Pc=P_1, MR=OF)  # Initial C* (m/s)
        c_f, _, __ = Prop.getFrozen_PambCf(Pamb=P_3, Pc=P_1, MR=OF, eps=eps, frozenAtThroat=1)  # Initial thrust coefficient
        mw, gamma = Prop.get_Chamber_MolWt_gamma(Pc=P_1, MR=OF, eps=eps)  # Molar mass (g/mol) and gamma: specific heat ratio
        R = 8314 / mw  # Gas constant for the propellant: Ru/MM
        T_1 = Prop.get_Tcomb(Pc=P_1, MR=OF)  # Adiabatic flame temperature - Combustion temperature (K)
        mach = Prop.get_MachNumber(Pc=P_1, MR=OF, eps=eps, frozen=0, frozenAtThroat=0) # Return nozzle exit mach number

        #


        # Calculation of mass flow rates:

        A_t = (F) / (P_1 * c_f)  # Throat area of the nozzle (m²)
        m_total = (F) / (c_star * c_f)  # Initial total propellant mass flow rate (kg/s)
        m_f = m_total / (OF + 1)  # Initial fuel mass flow rate (kg/s)
        m_ox = m_total - m_f  # Initial oxidizer mass flow rate (kg/s)
        A_2 = A_t*eps   # Exit area of the nozzle (m²)

        R_2 = (A_2/math.pi)**0.5    # Exit radius (m)
        R_t = (A_t/math.pi)**0.5    # Throat radius (m)

        #


        initial_parameters = {
            "eps": eps,
            "c_star": c_star,
            "c_f": c_f,
            "mw": mw,
            "gamma": gamma,
            "R": R,
            "T_1": T_1,
            "A_t": A_t,
            "R_t": R_t,
            "R_2": R_2,
            "A_2": A_2,
            "m_total": m_total,
            "m_f": m_f,
            "m_ox": m_ox,
            "mach_2": mach
        }

        return initial_parameters

    from rocketcea.cea_obj_w_units import CEA_Obj

    Prop = CEA_Obj(oxName=O_name, fuelName=F_name, pressure_units='Pa', cstar_units='m/s', density_units='g/cc', temperature_units='K')

    from rocketcea.cea_obj import CEA_Obj
    ispObj = CEA_Obj(oxName=O_name, fuelName=F_name)
    st.session_state['IsoObj'] = ispObj

    initial_params = calculate_initial_parameters(Prop, P_1, OF, P_3, F)
    st.session_state['initial_params'] = initial_params

