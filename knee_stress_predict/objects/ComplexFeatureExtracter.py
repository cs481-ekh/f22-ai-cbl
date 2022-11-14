from pathlib import Path
from knee_stress_predict.config import raw_data_dir, processed_data_dir
from knee_stress_predict.objects.KneeGeometry import KneeGeometry
import numpy as np
import pyvista as pv
import pandas as pd
import os

def plot_curv_subdivisions(patients_knees,data):
    p = pv.Plotter(shape=(4, 7))
    i = 0
    for key, value in patients_knees.items():
        p.subplot(i // 7, i % 7)
        # extract the surface and plot it
        surf_lat = value.tibia_cart_lat.extract_surface()
        surf_med = value.tibia_cart_med.extract_surface()

        curv_lat = surf_lat.curvature()
        curv_med = surf_med.curvature()

        # I decided to look at the absolute value of curvature. Not sure if it is the best way.
        #  Also, the edges of cartilage affect curvature a lot; as a suggestion to overcome this issue
        #  we can use CurvaturesAdjustEdges from vtk: https://kitware.github.io/vtk-examples/site/Python/PolyData/CurvaturesAdjustEdges/
        mean_curv_lat = np.mean(abs(curv_lat))
        mean_curv_med = np.mean(abs(curv_med))

        p.add_mesh(surf_lat, scalars=curv_lat)
        p.add_mesh(surf_med, scalars=curv_med)

        if (len(data.loc[data['Code']== key]) > 0):

            max_tib_lat_pressure = data.loc[data['Code'] == key, 'Max_tib_lat_contact_pressure'].iloc[0]
            max_tib_med_pressure = data.loc[data['Code'] == key, 'Max_tib_med_contact_pressure'].iloc[0]


            p.add_text(f'{key}: \n '
                       f'lat pressure = {max_tib_lat_pressure:.2f},\n '
                       f'med pressure = {max_tib_med_pressure:.2f}, \n'
                       f'lat curv = {mean_curv_lat} \n'
                       f'med curv = {mean_curv_med}'
                       , font_size=10,)
            i = i + 1

    p.link_views()
    p.view_isometric()
    return p


def add_tib_car_curv(patients_knees, data):
    tib_med_curv = []
    tib_lat_curv = []
    for key, value in patients_knees.items():
        surf_lat = value.tibia_cart_lat.extract_surface()
        surf_med = value.tibia_cart_med.extract_surface()

        curv_lat = surf_lat.curvature()
        curv_med = surf_med.curvature()

        # I decided to look at the absolute value of curvature. Not sure if it is the best way.
        #  Also, the edges of cartilage affect curvature a lot; as a suggestion to overcome this issue
        #  we can use CurvaturesAdjustEdges from vtk: https://kitware.github.io/vtk-examples/site/Python/PolyData/CurvaturesAdjustEdges/
        mean_curv_med = np.mean(abs(curv_med))
        mean_curv_lat = np.mean(abs(curv_lat))

        tib_med_curv.append(mean_curv_med)
        tib_lat_curv.append(mean_curv_lat)

    tib_curv_df = pd.DataFrame({'Code': patients_knees.keys(), 'tib_med_curv': tib_med_curv, 'tib_lat_curv':tib_lat_curv})

    data = data.join(tib_curv_df.set_index('Code'), on='Code')

    return data


if __name__ == '__main__':
    # path = Path.joinpath(raw_data_dir, "set_1/2022.09.16_Geometries")
    # knee = KneeGeometry(path)
    #
    # # extract the surface and plot it
    # surf = knee.tibia_cart_med.extract_surface()
    # curv = surf.curvature()
    # surf.plot(scalars=curv)
    # mean_curv = np.mean(abs(curv))
    # print(mean_curv)

    patients_knees = {}
    data_set_name = "set_2"
    data_dir = Path.joinpath(raw_data_dir, data_set_name)
    for i, folder_name in enumerate(os.listdir(data_dir)):
        patient_dir = Path.joinpath(data_dir, folder_name)
        patient_knee = KneeGeometry(patient_dir)
        patients_knees[folder_name] = patient_knee

    data_set_name = "set_2"
    file_path = Path.joinpath(processed_data_dir, data_set_name, "out_cleaned.csv")
    data = pd.read_csv(file_path)

    plotter = plot_curv_subdivisions(patients_knees, data)

    plotter.show()

    a = add_tib_car_curv(patients_knees, data)


