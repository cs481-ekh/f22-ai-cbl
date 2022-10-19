from pathlib import Path
import pandas as pd
import pyvista as pv
import numpy as np
import seaborn as sns
import os
import matplotlib.pyplot as plt
from knee_stress_predict.config import raw_data_dir, processed_data_dir
from knee_stress_predict.objects.KneeGeometry import KneeGeometry


def plot_subdivisions(patients_knees,data):
    display_args = dict(show_edges=True, color=True)
    p = pv.Plotter(shape=(4, 7))
    i = 0
    for key, value in patients_knees.items():
        p.subplot(i // 7, i % 7)

        p.add_mesh(value.femur, **display_args)
        p.add_mesh(value.tibia, **display_args)
        p.add_mesh(value.patella, **display_args)
        p.add_mesh(value.fem_cart, **display_args)
        p.add_mesh(value.pat_cart, **display_args)
        p.add_mesh(value.tibia_cart_lat, **display_args)
        p.add_mesh(value.tibia_cart_med, **display_args)

        max_tib_lat_pressure = data.loc[data['Code'] == key, 'Max_tib_lat_contact_pressure'].iloc[0]
        max_tib_med_pressure = data.loc[data['Code'] == key, 'Max_tib_med_contact_pressure'].iloc[0]


        p.add_text(f'{key}: \n lat = {max_tib_lat_pressure:.2f},  \n med = {max_tib_med_pressure:.2f}', font_size=10,)
        i = i + 1

    p.link_views()
    p.view_isometric()
    return p

if __name__ == '__main__':
    patients_knees = {}
    data_set_name = "set_2"
    data_dir = Path.joinpath(raw_data_dir, data_set_name)
    for i, folder_name in enumerate(os.listdir(data_dir)):
        patient_dir = Path.joinpath(data_dir, folder_name)
        patient_knee = KneeGeometry(patient_dir)
        patients_knees[folder_name] = patient_knee

    data_set_name = "set_2"
    file_path = Path.joinpath(processed_data_dir, data_set_name, "out.csv")
    data = pd.read_csv(file_path)

    plotter = plot_subdivisions(patients_knees, data)

    plotter.show()