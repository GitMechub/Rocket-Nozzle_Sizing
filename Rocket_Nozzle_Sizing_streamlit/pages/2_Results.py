import streamlit as st
for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os
path = os.path.dirname(__file__)
my_file = path+'/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='Results - Rocket Nozzle Sizing',
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

import io

from rocketcea.cea_obj import add_new_fuel, add_new_oxidizer

from rocketcea.cea_obj_w_units import CEA_Obj

from pylab import *

import numpy as np

import pandas as pd

import math

from math import sin

import matplotlib.pyplot as plt

import plotly.graph_objects as go

# Last not null/empty list value
def last_valid(lst):
    return next((x for x in reversed(lst) if x and not isnan(x)), None) # or 'null'
#

#try:
st.header("Rocket Nozzle Dimensions", anchor=False, divider='gray')
with st.spinner('Loading...'):
    initial_params = st.session_state['initial_params']
    Method = st.session_state['method']
    spike_detail = st.session_state['spike_detail']

    if 'active_page' not in st.session_state:
        st.session_state.active_page = '2_Results'
        st.session_state.nozzle_type = 'Conical'

    nozzle_choice = st.selectbox(
        'Type of nozzle',
        ['Conical', 'Bell', 'Spike'],
        key='nozzle_type'
    )

    if nozzle_choice == "Conical":

        conical = {}
        conical['Throat radius (mm)'] = initial_params["R_t"]*1000
        conical['Exit radius (mm)'] = initial_params["R_2"]*1000
        conical['Divergent Length (mm)'] = 0
        conical['Curve 1 Radius (mm)'] = 0
        conical['Curve 2 Radius (mm)'] = 0


        # Throat circular arc

        ## Entrance throat circular arc (Curve 1) [3][1]
        theta1 = np.linspace(-135, -90, num=100)  # Values of theta from -135 to -90
        x1c = 1.5 * conical['Throat radius (mm)'] * np.cos(np.radians(theta1))
        y1c = 1.5 * conical['Throat radius (mm)'] * np.sin(np.radians(theta1)) + 1.5 * conical['Throat radius (mm)'] + conical['Throat radius (mm)']
        initial_params['L_c'] = x1c[-1] # Convergent length (mm)
        conical['Curve 1 Radius (mm)'] = 1.5*conical['Throat radius (mm)']

        x1_start = x1c[0]
        x1_end = x1c[-1]
        y1_start = y1c[0]
        y1_end = y1c[-1]


        ## Exit throat circular arc (Curve 2) [3][1]
        theta2 = np.linspace(-90, (15 - 90), num=100)
        x2c = 0.382 * conical['Throat radius (mm)'] * np.cos(np.radians(theta2))
        y2c = 0.382 * conical['Throat radius (mm)'] * np.sin(np.radians(theta2)) + 0.382 * conical['Throat radius (mm)'] + conical['Throat radius (mm)']
        R_n = y2c[-1]
        X_n = x2c[-1]
        conical['Curve 2 Radius (mm)'] = 0.382*conical['Throat radius (mm)']

        x2_start = x2c[0]
        x2_end = x2c[-1]
        y2_start = y2c[0]
        y2_end = y2c[-1]
        print(y2_end)

        ###


        # Divergent section

        ## Divergent section length (15° Conical Nozzle Length) [1]
        L_d = (conical['Exit radius (mm)']-y2_end)/(np.tan(np.radians(15)))
        conical['Divergent Length (mm)'] = L_d

        ## Exit shape
        t = np.linspace(x2_end, L_d, num=100)
        x3c = t
        y3c = (np.tan(np.radians(15)))*t + y2_end-(np.tan(np.radians(15)))*x2_end

        x3_start = x3c[0]
        x3_end = x3c[-1]
        y3_start = y3c[0]
        y3_end = y3c[-1]

        ###


        conical_xy_1 = pd.DataFrame({'x (m)': [item/1000 for item in x1c], 'y (m)': [item/1000 for item in y1c]})
        conical_xy_2 = pd.DataFrame({'x (m)': [item/1000 for item in x2c], 'y (m)': [item/1000 for item in y2c]})
        conical_xy_3 = pd.DataFrame({'x (m)': [item/1000 for item in x3c], 'y (m)': [item/1000 for item in y3c]})

        # Download Button

        import io
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            conical_xy = pd.concat([conical_xy_1, conical_xy_2, conical_xy_3])
            conical_xy.reset_index(drop=True, inplace=True)
            conical_xy.to_excel(writer, sheet_name="CONICAL",index=False)
            # Close the Pandas Excel writer and output the Excel file to the buffer
            writer.close()

            st.download_button(
                label="Download Conical Nozzle Contour Coordinates",
                data=buffer,
                file_name="Conical_Nozzle_Contour_Coordinates.xlsx",
            )

        # Plot Nozzle Chart

        plt.plot(x1c, y1c, label='Curve 1')
        plt.plot(x2c, y2c, label='Curve 2')
        plt.plot(x3c, y3c, label='Curve 3')
        plt.scatter([x1_start, x1_end, x2_start, x2_end, x3_start, x3_end],
                  [y1_start, y1_end, y2_start, y2_end, y3_start, y3_end],
                  color=['blue', 'blue', 'orange', 'orange', 'green', 'green'],
                  label='Start/End Points', s=30)


        plt.xlabel('x (mm)')
        plt.ylabel('y (mm)')
        plt.title('Conical Nozzle')
        plt.legend()
        plt.axhline(y=0, color='black', linestyle='-.', linewidth=1.5)
        plt.axis('equal')
        plt.grid(True)
        st.pyplot(plt.gcf())

        # Coordinates plot
        coordinates_conical = {'Coordinate': ['Start (x, y)', 'End (x, y)'],
                               'Curve 1': [(round(x1_start, 2), round(y1_start, 2)), (round(x1_end, 2), round(y1_end, 2))],
                               'Curve 2': [(round(x2_start, 2), round(y2_start, 2)), (round(x2_end, 2), round(y2_end, 2))],
                               'Curve 3': [(round(x3_start, 2), round(y3_start, 2)), (round(x3_end, 2), round(y3_end, 2))]}

        coordinates_conical = pd.DataFrame(coordinates_conical)
        st.table(coordinates_conical)
        #

        table_conical_dimensions = go.Figure(data=[go.Table(header=dict(
            values=['Throat radius (mm)', 'Exit radius (mm)', 'Divergent Length (mm)', 'Curve 1 Radius (mm)',
                    'Curve 2 Radius (mm)'], height=40, align=['center'], line_color='darkslategray', fill_color='royalblue',
            font=dict(color='white', size=16)),
                                                            cells=dict(values=[round(conical['Throat radius (mm)'], 2),
                                                                               round(conical['Exit radius (mm)'], 2),
                                                                               round(conical['Divergent Length (mm)'], 2),
                                                                               round(conical['Curve 1 Radius (mm)'], 2),
                                                                               round(conical['Curve 2 Radius (mm)'], 2)],
                                                                       line_color='darkslategray', height=30,
                                                                       fill_color=['lightcyan'],
                                                                       font=dict(color='darkslategray', size=14)))
                                                   ], layout=go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
                                             )

        table_conical_dimensions.update_layout(title='Conical Nozzle Dimensions', titlefont=dict(color='royalblue', size=28),
                                               height=500)

        #

        st.write(table_conical_dimensions)


    if nozzle_choice == "Bell":

        x = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
        y = np.array([23, 26, 27.5, 29, 30, 30.5, 31, 31.5, 32, 32.5])

        bell = {}
        bell['Throat radius (mm)'] = initial_params["R_t"] * 1000
        bell['Exit radius (mm)'] = initial_params["R_2"] * 1000
        bell['Divergent Length (mm)'] = 0
        bell['Divergent Theta n (°)'] = 0
        bell['Divergent Theta e (°)'] = 0
        bell['Curve 1 Radius (mm)'] = 0
        bell['Curve 2 Radius (mm)'] = 0

        # Parameters obtained from curve fitting [4][3]

        ## theta n
        a = 4.090132978351974
        b = 16.539279319795025

        theta_n = a * np.log(initial_params['eps']) + b

        ## theta e
        a = -2.175213837970657
        b = 15.932404342184924

        theta_e = a * np.log(initial_params['eps']) + b

        ###

        # Throat circular arc

        ## Entrance throat circular arc (Curve 1) [3][5]
        theta1 = np.linspace(-135, -90, num=100)  # Values of theta from -135 to -90
        x1b = 1.5 * bell['Throat radius (mm)'] * np.cos(np.radians(theta1))
        y1b = 1.5 * bell['Throat radius (mm)'] * np.sin(np.radians(theta1)) + 1.5 * bell['Throat radius (mm)'] + bell[
            'Throat radius (mm)']
        initial_params['L_c'] = x1b[-1]  # Convergent length (mm)
        bell['Curve 1 Radius (mm)'] = 1.5 * bell['Throat radius (mm)']

        x1_start = x1b[0]
        x1_end = x1b[-1]
        y1_start = y1b[0]
        y1_end = y1b[-1]

        ## Exit throat circular arc (Curve 2) [3][5]
        theta2 = np.linspace(-90, (theta_n - 90), num=100)
        x2b = 0.382 * bell['Throat radius (mm)'] * np.cos(np.radians(theta2))
        y2b = 0.382 * bell['Throat radius (mm)'] * np.sin(np.radians(theta2)) + 0.382 * bell['Throat radius (mm)'] + bell[
            'Throat radius (mm)']
        R_n = y2b[-1]
        X_n = x2b[-1]
        bell['Curve 2 Radius (mm)'] = 0.382 * bell['Throat radius (mm)']

        x2_start = x2b[0]
        x2_end = x2b[-1]
        y2_start = y2b[0]
        y2_end = y2b[-1]

        ###

        # Divergent section [3][5]

        ## Divergent section length (80% 15° Conical Nozzle Length)
        L_d = 0.8 * ((((initial_params['eps'] ** 0.5) - 1) * bell['Throat radius (mm)']) / (np.tan(np.radians(15))))

        Nx = x2b[-1]
        Ny = y2b[-1]
        Ex = 0.8 * ((((initial_params["eps"] ** 0.5) - 1) * bell['Throat radius (mm)']) / (np.tan(np.radians(15))))
        Ey = bell['Exit radius (mm)']

        m1 = np.tan(np.radians(theta_n))
        m2 = np.tan(np.radians(theta_e))
        C1 = Ny - (m1 * Nx)
        C2 = Ey - (m2 * Ex)
        Qx = (C2 - C1) / (m1 - m2)
        Qy = ((C2 * m1) - (C1 * m2)) / (m1 - m2)

        ## Exit circular arc (Curve 3) [3]
        t = np.linspace(0, 1, num=100)
        x3b = (((1 - t) ** 2) * Nx) + (2 * (1 - t) * t * Qx) + ((t ** 2) * Ex)
        y3b = (((1 - t) ** 2) * Ny) + (2 * (1 - t) * t * Qy) + ((t ** 2) * Ey)

        x3_start = x3b[0]
        x3_end = x3b[-1]
        y3_start = y3b[0]
        y3_end = y3b[-1]

        ###

        bell_xy_1 = pd.DataFrame({'x (m)': [item / 1000 for item in x1b], 'y (m)': [item / 1000 for item in y1b]})
        bell_xy_2 = pd.DataFrame({'x (m)': [item / 1000 for item in x2b], 'y (m)': [item / 1000 for item in y2b]})
        bell_xy_3 = pd.DataFrame({'x (m)': [item / 1000 for item in x3b], 'y (m)': [item / 1000 for item in y3b]})

        # Download Button

        import io
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            bell_xy = pd.concat([bell_xy_1, bell_xy_2, bell_xy_3])
            bell_xy.reset_index(drop=True, inplace=True)
            bell_xy.to_excel(writer, sheet_name="BELL",index=False)
            # Close the Pandas Excel writer and output the Excel file to the buffer
            writer.close()

            st.download_button(
                label="Download Bell Nozzle Contour Coordinates",
                data=buffer,
                file_name="Bell_Nozzle_Contour_Coordinates.xlsx",
            )

        # Plot Nozzle Chart

        plt.plot(x1b, y1b, label='Curve 1')
        plt.plot(x2b, y2b, label='Curve 2')
        plt.plot(x3b, y3b, label='Curve 3')
        plt.scatter([x1_start, x1_end, x2_start, x2_end, x3_start, x3_end],
                    [y1_start, y1_end, y2_start, y2_end, y3_start, y3_end],
                    color=['blue', 'blue', 'orange', 'orange', 'green', 'green'],
                    label='Start/End Points', s=30)

        plt.xlabel('x (mm)')
        plt.ylabel('y (mm)')
        plt.title('Bell-shaped Nozzle')
        plt.legend()
        plt.axhline(y=0, color='black', linestyle='-.', linewidth=1.5)
        plt.axis('equal')
        plt.grid(True)
        st.pyplot(plt.gcf())

        bell['Divergent Length (mm)'] = L_d
        bell['Divergent Theta n (°)'] = theta_n
        bell['Divergent Theta e (°)'] = theta_e

        #

        # Coordinates plot

        coordinates_bell = {'Coordinate': ['Start (x, y)', 'End (x, y)'],
                            'Curve 1': [(round(x1_start, 2), round(y1_start, 2)), (round(x1_end, 2), round(y1_end, 2))],
                            'Curve 2': [(round(x2_start, 2), round(y2_start, 2)), (round(x2_end, 2), round(y2_end, 2))],
                            'Curve 3': [(round(x3_start, 2), round(y3_start, 2)), (round(x3_end, 2), round(y3_end, 2))]}

        coordinates_bell = pd.DataFrame(coordinates_bell)
        st.table(coordinates_bell)

        #

        # Table:

        table_bell_dimensions = go.Figure(data=[go.Table(header=dict(
            values=['Throat radius (mm)', 'Exit radius (mm)', 'Divergent Length (mm)', 'Divergent Theta n (°)',
                    'Divergent Theta e (°)', 'Curve 1 Radius (mm)', 'Curve 2 Radius (mm)'], height=40, align=['center'],
            line_color='darkslategray', fill_color='royalblue', font=dict(color='white', size=16)),
                                                         cells=dict(values=[round(bell['Throat radius (mm)'], 2),
                                                                            round(bell['Exit radius (mm)'], 2),
                                                                            round(bell['Divergent Length (mm)'], 2),
                                                                            round(bell['Divergent Theta n (°)'], 1),
                                                                            round(bell['Divergent Theta e (°)'], 1),
                                                                            round(bell['Curve 1 Radius (mm)'], 2),
                                                                            round(bell['Curve 2 Radius (mm)'], 2)],
                                                                    line_color='darkslategray', height=30,
                                                                    fill_color=['lightcyan'],
                                                                    font=dict(color='darkslategray', size=14)))
                                                ], layout=go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
                                          )

        table_bell_dimensions.update_layout(title='Bell-shaped Nozzle Dimensions',
                                            titlefont=dict(color='royalblue', size=28), height=500)

        #

        st.write(table_bell_dimensions)


    if nozzle_choice == "Spike":

        spike = {}
        spike['Throat gap (mm)'] = 0
        spike['Spike base radius (mm)'] = 0
        spike['Spike Length (mm)'] = 0
        spike['Spike Length 50% (mm)'] = 0
        spike['Initial angle (°)'] = 0
        spike['50% Length angle (°)'] = 0
        spike['Final angle (°)'] = 0

        # Method:

        # Method = 1   # 1: [6][7] Method | 2: [8][9] Method

        #

        i = 1

        if initial_params['mach_2'] <= 1.5:
            N = 1349
        elif initial_params['mach_2'] <= 2:
            N = 6205
        elif initial_params['mach_2'] <= 3:
            N = 27052
        elif initial_params['mach_2'] <= 4:
            N = 59094
        else:
            N = 97901

        if spike_detail is False or spike_detail == 0:
            N = 200
        elif isinstance(spike_detail, int) and spike_detail is not True:
            N = spike_detail if spike_detail > 100 else 200

        # Divergent section (Curve 1) - Method 1 [6][7]

        if Method == 1:

            thetab = (((initial_params['gamma'] + 1) / (initial_params['gamma'] - 1)) ** (1 / 2)) * np.arctan(((((
                                                                                                                             initial_params[
                                                                                                                                 'gamma'] - 1) / (
                                                                                                                             initial_params[
                                                                                                                                 'gamma'] + 1)) * (
                                                                                                                            (
                                                                                                                                        initial_params[
                                                                                                                                            'mach_2'] ** 2) - 1)) ** (
                                                                                                                           1 / 2))) - np.arctan(
                ((initial_params['mach_2'] ** 2) - 1) ** (1 / 2))
            re2_rt2 = (initial_params["A_t"] * np.cos(thetab)) / (np.pi)
            mach_list = []  # Mach number
            v_list = []
            x_list = []
            y_list = []

            while i <= N:
                mach_i = 1 + (i - 1) * ((initial_params['mach_2'] - 1) / (N - 1))  # Mach number
                mach_list.append(mach_i)

                v_i = (((initial_params['gamma'] + 1) / (initial_params['gamma'] - 1)) ** (1 / 2)) * np.arctan(((((
                                                                                                                              initial_params[
                                                                                                                                  'gamma'] - 1) / (
                                                                                                                              initial_params[
                                                                                                                                  'gamma'] + 1)) * (
                                                                                                                             (
                                                                                                                                         mach_i ** 2) - 1)) ** (
                                                                                                                            1 / 2))) - np.arctan(
                    ((mach_i ** 2) - 1) ** (1 / 2))
                u_i = np.arcsin(1 / mach_i)  # Angle of Mach
                thetha_i = thetab - v_i
                phi_i = thetab - v_i + u_i  # Polar angle

                Ai_At = (1 / mach_i) * (((2 / (initial_params['gamma'] + 1)) * (
                            1 + (((initial_params['gamma'] - 1) / 2) * (mach_i ** 2)))) ** (
                                                    (initial_params['gamma'] + 1) / (2 * (initial_params['gamma'] - 1))))

                y_i = ((initial_params["R_2"] ** 2) - (
                            (re2_rt2) * Ai_At * ((np.sin(phi_i)) / (np.sin(u_i) * np.cos(thetab))))) ** (1 / 2)
                x_i = (initial_params["R_2"] - y_i) / np.tan(phi_i)

                x_list.append(x_i)
                y_list.append(y_i)

                v_list.append(v_i)

                i = i + 1

            x1s = [item * 1000 for item in x_list]
            y1s = [item * 1000 for item in y_list]

            # Throat section (Curve 2)

            x2s = np.linspace(x1s[0], 0, num=N)
            y2s = np.tan(thetab) * (-x2s) + initial_params["R_2"] * 1000

            #


        # Divergent section (Curve 1) - Method 2 [8][9]

        elif Method == 2:

            thetab = (((initial_params['gamma'] + 1) / (initial_params['gamma'] - 1)) ** (1 / 2)) * np.arctan(((((
                                                                                                                             initial_params[
                                                                                                                                 'gamma'] - 1) / (
                                                                                                                             initial_params[
                                                                                                                                 'gamma'] + 1)) * (
                                                                                                                            (
                                                                                                                                        initial_params[
                                                                                                                                            'mach_2'] ** 2) - 1)) ** (
                                                                                                                           1 / 2))) - np.arctan(
                ((initial_params['mach_2'] ** 2) - 1) ** (1 / 2))
            lipang = (np.pi / 2) - thetab  # 𝛙
            lambdab = initial_params["R_2"] / initial_params['eps']  # Initial polar ray (λ)

            lambda_list = [lambdab]  # Polar ray (λ)
            mach_list = []  # Mach number
            v_list = []

            x_list = []
            y_list = []

            while i <= N:
                ## Initial parameters for i
                lambda_i = lambda_list[-1]  # Polar ray (λ)

                mach_i = 1 + (i - 1) * ((initial_params['mach_2'] - 1) / (N - 1))  # Mach number
                mach_list.append(mach_i)

                v_i = (((initial_params['gamma'] + 1) / (initial_params['gamma'] - 1)) ** (1 / 2)) * np.arctan(((((
                                                                                                                              initial_params[
                                                                                                                                  'gamma'] - 1) / (
                                                                                                                              initial_params[
                                                                                                                                  'gamma'] + 1)) * (
                                                                                                                             (
                                                                                                                                         mach_i ** 2) - 1)) ** (
                                                                                                                            1 / 2))) - np.arctan(
                    ((mach_i ** 2) - 1) ** (1 / 2))
                u_i = np.arcsin(1 / mach_i)  # Angle of Mach
                phi_i = (np.pi / 2) - lipang - v_i + u_i  # Polar angle
                ##

                ## Parameters for i+1 in order to calculate 'beta_i'
                mach_i1 = 1 + ((i + 1) - 1) * ((initial_params['mach_2'] - 1) / (N - 1))
                v_i1 = (((initial_params['gamma'] + 1) / (initial_params['gamma'] - 1)) ** (1 / 2)) * np.arctan(((((
                                                                                                                               initial_params[
                                                                                                                                   'gamma'] - 1) / (
                                                                                                                               initial_params[
                                                                                                                                   'gamma'] + 1)) * (
                                                                                                                              (
                                                                                                                                          mach_i1 ** 2) - 1)) ** (
                                                                                                                             1 / 2))) - np.arctan(
                    ((mach_i1 ** 2) - 1) ** (1 / 2))
                u_i1 = np.arcsin(1 / mach_i1)
                phi_i1 = (np.pi / 2) - lipang - v_i1 + u_i1
                ##

                ## Dimensions for i
                alpha_i = np.pi - phi_i + thetab - v_i
                beta_i = phi_i1 - thetab + v_i

                y_i = (np.sin(phi_i)) * lambda_i
                x_i = (np.cos(phi_i)) * lambda_i

                x_list.append(x_i)
                y_list.append(y_i)

                ##

                lambda_i1 = (np.sin(alpha_i) / np.sin(beta_i)) * lambda_i
                lambda_list.append(lambda_i1)
                v_list.append(v_i)

                i = i + 1

            x1s = [item * 1000 for item in x_list]
            y1s = [item * 1000 for item in y_list]

            ###

            # Throat section (Curve 2)

            x2s = np.linspace(x1s[0], 0, num=N)
            y2s = np.tan(-thetab) * (-x2s)

            #

            # Normalizing data

            y_axline = y1s[-1]
            y1s = [abs(item - y_axline) for item in y1s]
            y2s = [abs(item - y_axline) for item in y2s]
            y_axline = y1s[-1]

            #

        else:
            x1s, y1s, x2s, y2s = [0], [0], [0], [0]

        x1_start = x1s[0]
        x1_end = last_valid(x1s)
        # x1_end = x1s[-1]
        y1_start = y1s[0]
        y1_end = last_valid(y1s)
        # y1_end = y1s[-1]

        x1_mean = abs((x1_end - x1_start) / 2)
        nearest_xmean = min(x1s, key=lambda x: abs(x - x1_mean))
        nearest_xmean_index = x1s.index(nearest_xmean)
        x150_start = x1s[0]
        x150_end = nearest_xmean
        y150_start = y1s[0]
        y150_end = y1s[nearest_xmean_index]

        x2_start = x2s[0]
        x2_end = x2s[-1]
        y2_start = y2s[0]
        y2_end = y2s[-1]

        spike['Throat gap (mm)'] = abs(y2_start - y1_start)
        spike['Spike base radius (mm)'] = initial_params["R_2"] * 1000
        spike['Spike Length (mm)'] = x1_end - x1_start
        spike['Spike Length 50% (mm)'] = x150_end - x1_start

        spike['Initial angle (°)'] = math.degrees(thetab - v_list[0])
        spike['50% Length angle (°)'] = math.degrees(thetab - v_list[nearest_xmean_index])
        spike['Final angle (°)'] = math.degrees(thetab - v_list[x1s.index(x1_end)])

        spike_xy_1 = pd.DataFrame({'x (m)': [item / 1000 for item in x1s], 'y (m)': [item / 1000 for item in y1s]})
        spike_xy_2 = pd.DataFrame({'x (m)': [item / 1000 for item in x2s], 'y (m)': [item / 1000 for item in y2s]})

        # Download Button

        import io
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            spike_xy_1.to_excel(writer, sheet_name="SPIKE - Curve 1",index=False)
            spike_xy_2.to_excel(writer, sheet_name="SPIKE - Curve 2",index=False)

            # Close the Pandas Excel writer and output the Excel file to the buffer
            writer.close()

            st.download_button(
                label="Download Spike Nozzle Contour Coordinates",
                data=buffer,
                file_name="Spike_Nozzle_Contour_Coordinates.xlsx",
            )

        # Plot Nozzle Chart

        plt.plot(x1s, y1s, label='Curve 1')
        plt.plot(x2s, y2s, label='Curve 2')

        plt.scatter([x1_start, x1_end, x2_start, x2_end, x150_start, x150_end],
                    [y1_start, y1_end, y2_start, y2_end, y150_start, y150_end],
                    color=['blue', 'blue', 'orange', 'orange', 'blue', 'blue'],
                    label='Start/End Points', s=30)

        plt.xlabel('x (mm)')
        plt.ylabel('y (mm)')
        plt.title('Spike Nozzle')
        plt.axhline(y=0, color='black', linestyle='-.', linewidth=1.5)
        plt.legend()
        plt.axis('equal')
        plt.grid(True)
        st.pyplot(plt.gcf())

        #

        # Coordinates plot

        coordinates_spike = {'Coordinate': ['Start (x, y)', 'End (x, y)'],
                             'Curve 1': [(round(x1_start, 2), round(y1_start, 2)), (round(x1_end, 2), round(y1_end, 2))],
                             'Curve 1 (50% length)': [(round(x150_start, 2), round(y150_start, 2)),
                                                      (round(x150_end, 2), round(y150_end, 2))],
                             'Curve 2': [(round(x2_start, 2), round(y2_start, 2)), (round(x2_end, 2), round(y2_end, 2))]}

        coordinates_spike = pd.DataFrame(coordinates_spike)
        st.table(coordinates_spike)

        #

        # Table:

        table_spike_dimensions = go.Figure(data=[go.Table(header=dict(
            values=['Spike base radius (mm)', 'Throat gap (mm)', 'Spike Length (mm)', 'Spike Length 50% (mm)',
                    'Initial angle (°)', '50% Length angle (°)', 'Final angle (°)'], height=40, align=['center'],
            line_color='darkslategray', fill_color='royalblue', font=dict(color='white', size=16)),
                                                          cells=dict(values=[round(spike['Spike base radius (mm)'], 2),
                                                                             round(spike['Throat gap (mm)'], 2),
                                                                             round(spike['Spike Length (mm)'], 2),
                                                                             round(spike['Spike Length 50% (mm)'], 2),
                                                                             round(spike['Initial angle (°)'], 2),
                                                                             round(spike['50% Length angle (°)'], 2),
                                                                             round(spike['Final angle (°)'], 2)],
                                                                     line_color='darkslategray', height=30,
                                                                     fill_color=['lightcyan'],
                                                                     font=dict(color='darkslategray', size=14)))
                                                 ], layout=go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
                                           )

        table_spike_dimensions.update_layout(title='Spike Nozzle Dimensions', titlefont=dict(color='royalblue', size=28),
                                             height=500)

        #

        st.write(table_spike_dimensions)
#except:
st.markdown("Click on 'Run'")
#    pass

