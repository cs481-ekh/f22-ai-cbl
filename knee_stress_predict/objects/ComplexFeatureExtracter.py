from pathlib import Path
from knee_stress_predict.config import raw_data_dir, processed_data_dir
from knee_stress_predict.objects.KneeGeometry import KneeGeometry
from knee_stress_predict.objects.Contour import get_img_cnts, get_cnt_center, get_cnt_center
import numpy as np
import pyvista as pv
import pandas as pd
import os
import cv2.cv2 as cv2

def plot_curv_subdivisions(patients_knees,data):
    p = pv.Plotter(shape=(4, 7))
    i = 0
    for key, value in patients_knees.items():
        p.subplot(i // 7, i % 7)
        # extract the surface and plot it
        surf_med = value.tibia_cart_med.extract_surface()
        surf_lat = value.tibia_cart_lat.extract_surface()

        curv_med = surf_med.curvature()
        curv_lat = surf_lat.curvature()

        # I decided to look at the absolute value of curvature. Not sure if it is the best way.
        #  Also, the edges of cartilage affect curvature a lot; as a suggestion to overcome this issue
        #  we can use CurvaturesAdjustEdges from vtk: https://kitware.github.io/vtk-examples/site/Python/PolyData/CurvaturesAdjustEdges/
        mean_curv_med = np.mean(abs(curv_med))
        mean_curv_lat = np.mean(abs(curv_lat))

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

def plot_damaged_status_subdivisions(patients_knees,data):
    p = pv.Plotter(shape=(4, 7))
    i = 0
    for key, value in patients_knees.items():
        p.subplot(i // 7, i % 7)

        p.add_mesh(value.tibia_cart_lat)
        p.add_mesh(value.tibia_cart_med)

        if (len(data.loc[data['Code']== key]) > 0):

            max_tib_lat_pressure = data.loc[data['Code'] == key, 'Max_tib_lat_contact_pressure'].iloc[0]
            max_tib_med_pressure = data.loc[data['Code'] == key, 'Max_tib_med_contact_pressure'].iloc[0]

            tib_med_ishealthy = data.loc[data['Code'] == key, 'tib_med_ishealthy'].iloc[0]
            tib_lat_ishealthy = data.loc[data['Code'] == key, 'tib_lat_ishealthy'].iloc[0]


            p.add_text(f'{key}: \n '
                       f'lat pressure = {max_tib_lat_pressure:.2f},\n '
                       f'med pressure = {max_tib_med_pressure:.2f}, \n'
                       f'med ishealthy = {tib_med_ishealthy} \n'
                       f'lat ishealthy = {tib_lat_ishealthy}'
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

def check_holes(cart_mesh):
    surf = cart_mesh.extract_surface()

    # Project surface on the xz plane. We can use this projection
    # to see if there are holes in the cartilage or surface is reduced
    origin = surf.center
    projected = surf.project_points_to_plane(origin=origin, normal=(0, 1, 0))

    # Save projection of the cartilage for the further analysis
    p = pv.Plotter(off_screen=True)

    # The code below helps to orient camera correctly and get projection for the further analysis
    origin_camera = origin.copy()
    origin_camera[1] -= surf.length * 5
    p.camera.position = origin_camera
    p.camera.focal_point = origin

    p.add_mesh(projected, color="white")
    img = p.screenshot(transparent_background=True, return_img=True)[:, :, 0]
    cntr = get_img_cnts(img=img, theshold=100)

    # There is a hole inside the cartilage. In case of projection we have two contours,
    #  one contour inside another contour
    return len(cntr) == 1

def evaluate_cartilage(patients_knees, data):
    """
    This function check if cartilages damaged.
    Based on the observation of cartilagies we sudgest to assume that cartilage is damages if:
    There is a hole inside the cartilage. In case of projection we have two contours,
    one contour inside another contour
    :return: df with status of cartilage heath
    """

    tib_med_ishealthy = []
    tib_lat_ishealthy = []

    for key, value in patients_knees.items():

        isHealthy_lat = check_holes(value.tibia_cart_lat)
        isHealthy_med = check_holes(value.tibia_cart_med)

        tib_med_ishealthy.append(isHealthy_med)
        tib_lat_ishealthy.append(isHealthy_lat)

    healthy_status_df = pd.DataFrame({'Code': patients_knees.keys(),
                                      'tib_med_ishealthy': tib_med_ishealthy,
                                      'tib_lat_ishealthy':tib_lat_ishealthy,
                                      })

    data = data.join(healthy_status_df.set_index('Code'), on='Code')

    return data


if __name__ == '__main__':
    path = Path.joinpath(raw_data_dir, "set_2/9968924M00")
    knee = KneeGeometry(path)

    # extract the surface of cartilage
    surf = knee.tibia_cart_med.extract_surface()

    # Project surface on the xz plane. We can use this projection
    # to see if there are holes in the cartilage or surface is reduced
    origin = surf.center
    projected = surf.project_points_to_plane(origin=origin, normal=(0, 1, 0))

    # Save projection of the cartilage for the further analysis
    p = pv.Plotter(off_screen=True)

    # The code below helps to orient camera correctly and get projection for the further analysis
    origin_camera = origin.copy()
    origin_camera[1] -= surf.length * 5
    p.camera.position = origin_camera
    p.camera.focal_point = origin

    p.add_mesh(projected, color="white")
    p.screenshot("screenshot.png")
    img = p.screenshot(transparent_background=True, return_img=True)[:,:,0]
    cntr = get_img_cnts(img=img, theshold=100)

    # Get biggest
    cnt = sorted(cntr, key=lambda cnt: cv2.contourArea(cnt), reverse=True)[0]


    # create a mask from your contour
    # hulls = [cv2.convexHull(cnt, False) for cnt in cntr]
    # mask = np.zeros_like(img)
    # cv2.drawContours(mask, hulls, -1, 255, -1)


    mask = np.zeros_like(img)
    cv2.drawContours(mask, [cv2.convexHull(cnt, False)], -1, 255, -1)

    cv2.imshow("mask", mask)
    cv2.waitKey(0)
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)

    radius_inner_circle = int(np.max(dist))
    origin = get_cnt_center(cnt)

    mask2 = np.zeros_like(img)
    cv2.circle(mask2, center=origin, radius=radius_inner_circle, color=(255, 255, 255), thickness=2)
    cv2.drawContours(mask2, cnt, -1, 255, -1)
    cv2.imshow("mask2", mask2)
    cv2.waitKey(0)

 #************************************************************************#

    a = 1


    # patients_knees = {}
    # data_set_name = "set_2"
    # data_dir = Path.joinpath(raw_data_dir, data_set_name)
    # for i, folder_name in enumerate(os.listdir(data_dir)):
    #     patient_dir = Path.joinpath(data_dir, folder_name)
    #     patient_knee = KneeGeometry(patient_dir)
    #     patients_knees[folder_name] = patient_knee
    #
    # data_set_name = "set_2"
    # file_path = Path.joinpath(processed_data_dir, data_set_name, "out_cleaned.csv")
    # data = pd.read_csv(file_path)
    # data = evaluate_cartilage(patients_knees, data)
    #
    # plotter = plot_damaged_status_subdivisions(patients_knees, data)
    # plotter.show()



