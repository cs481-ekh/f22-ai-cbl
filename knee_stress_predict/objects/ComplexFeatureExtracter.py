from pathlib import Path
from knee_stress_predict.config import raw_data_dir, processed_data_dir
from knee_stress_predict.objects.KneeGeometry import KneeGeometry
from knee_stress_predict.objects.Contour import get_img_cnts, get_cnt_center, get_cnt_center
import numpy as np
import pyvista as pv
import pandas as pd
import os
import cv2.cv2 as cv2
from scipy.spatial import KDTree, distance


def plot_curv_subdivisions(patients_knees, data):
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

        if (len(data.loc[data['Code'] == key]) > 0):
            max_tib_lat_pressure = data.loc[data['Code'] == key, 'Max_tib_lat_contact_pressure'].iloc[0]
            max_tib_med_pressure = data.loc[data['Code'] == key, 'Max_tib_med_contact_pressure'].iloc[0]

            p.add_text(f'{key}: \n '
                       f'lat pressure = {max_tib_lat_pressure:.2f},\n '
                       f'med pressure = {max_tib_med_pressure:.2f}, \n'
                       f'lat curv = {mean_curv_lat} \n'
                       f'med curv = {mean_curv_med}'
                       , font_size=10, )
            i = i + 1

    p.link_views()
    p.view_isometric()
    return p


def plot_damaged_status_subdivisions(patients_knees, data):
    p = pv.Plotter(shape=(4, 7))
    i = 0
    for key, value in patients_knees.items():
        p.subplot(i // 7, i % 7)

        p.add_mesh(value.tibia_cart_lat)
        p.add_mesh(value.tibia_cart_med)

        if (len(data.loc[data['Code'] == key]) > 0):
            max_tib_lat_pressure = data.loc[data['Code'] == key, 'Max_tib_lat_contact_pressure'].iloc[0]
            max_tib_med_pressure = data.loc[data['Code'] == key, 'Max_tib_med_contact_pressure'].iloc[0]

            tib_med_ishealthy = data.loc[data['Code'] == key, 'tib_med_ishealthy'].iloc[0]
            tib_lat_ishealthy = data.loc[data['Code'] == key, 'tib_lat_ishealthy'].iloc[0]

            p.add_text(f'{key}: \n '
                       f'lat pressure = {max_tib_lat_pressure:.2f},\n '
                       f'med pressure = {max_tib_med_pressure:.2f}, \n'
                       f'med ishealthy = {tib_med_ishealthy} \n'
                       f'lat ishealthy = {tib_lat_ishealthy}'
                       , font_size=10, )
            i = i + 1

    p.link_views()
    p.view_isometric()
    return p


def plot_femur_gap_subdivisions(patients_knees, data):
    p = pv.Plotter(shape=(4, 7))
    i = 0
    for key, value in patients_knees.items():
        p.subplot(i // 7, i % 7)

        p.add_mesh(value.femur, opacity=0.50)

        if (len(data.loc[data['Code'] == key]) > 0):
            left_point = data.loc[data['Code'] == key, "femur_left_gap_p"].iloc[0]
            right_point = data.loc[data['Code'] == key, "femur_right_gap_p"].iloc[0]
            distance = data.loc[data['Code'] == key, "femur_gap_dist"].iloc[0]

            line = pv.Line(right_point, left_point)

            p.add_mesh(line, color="yellow", line_width=10)
            p.add_text(f'{key}: \n '
                       f'femur gap = {distance:.2f},\n '
                       , font_size=10, )
            i = i + 1

    p.link_views()
    p.view_isometric()
    return p


def add_tib_car_curv(patients_knees, data):
    """
    This function adds a new feature: the average curvature of all elements of lateral and medial tibia cartilages for all provided knees
    :param patients_knees: Patient knees
    :param data: DataFrame where new features "tib_med_curv" and "tib_lat_curv" will be added
    :return: data: updated DataFrame
    """
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

    tib_curv_df = pd.DataFrame(
        {'Code': patients_knees.keys(), 'tib_med_curv': tib_med_curv, 'tib_lat_curv': tib_lat_curv})

    data = data.join(tib_curv_df.set_index('Code'), on='Code')

    return data


def check_holes_and_rough_edges(cart_mesh):
    """
    This function checks if provided cartilage is damaged.
    Based on the observation of cartilages, we assume that cartilage is damaged if:
        1. There is a hole inside the cartilage. In the case of projection, we have two contours, one contour inside another contour.
        2. The counter of the cartilage edge is rough
    :param cart_mesh
    :return: True is cartilage is healthy, False is cartilage is damaged
    """

    isHealthy = True
    cutt_off = 1.2  # cut off ration  convex hull to contour
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

    # 1. If there is a hole inside the cartilage. In case of projection we have two contours,
    #  one contour inside another contour
    isHealthy = len(cntr) == 1

    # 2. If there are rough edges the cartilage is damaged:
    if isHealthy:
        cnt = sorted(cntr, key=lambda cnt: cv2.contourArea(cnt), reverse=True)[0]
        hull_cnt = cv2.convexHull(cnt, False)
        cnt_area = cv2.contourArea(cnt)
        hull_cnt_area = cv2.contourArea(hull_cnt)
        isHealthy = (hull_cnt_area / cnt_area < cutt_off)

    return isHealthy


def evaluate_cartilage(patients_knees, data):
    """
    This function adds a new feature: the health status of medial and lateral tibia cartilages for all provided knees
    Based on the observation of cartilages, we assume that cartilage is damaged if:
        1. There is a hole inside the cartilage. In the case of projection, we have two contours, one contour inside another contour.
        2. The counter of the cartilage edge is rough
    :return: DataFrame where new features "tib_med_ishealthy" and "tib_lat_ishealthy" will be added
    """

    tib_med_ishealthy = []
    tib_lat_ishealthy = []

    for key, value in patients_knees.items():
        isHealthy_lat = check_holes_and_rough_edges(value.tibia_cart_lat)
        isHealthy_med = check_holes_and_rough_edges(value.tibia_cart_med)

        tib_med_ishealthy.append(isHealthy_med)
        tib_lat_ishealthy.append(isHealthy_lat)

    healthy_status_df = pd.DataFrame({'Code': patients_knees.keys(),
                                      'tib_med_ishealthy': tib_med_ishealthy,
                                      'tib_lat_ishealthy': tib_lat_ishealthy,
                                      })

    data = data.join(healthy_status_df.set_index('Code'), on='Code')

    return data


def find_femur_gap_distance(femur):
    """
    Finds distance of the femur gap
    :param femur:
    :return: distance (double), left_point(tuple), right_point(tuple)
    """

    origin = femur.center

    # Move origin to the position of the center of the gap
    origin[1] = origin[1] / 3
    origin[2] -= (femur.bounds[5] - femur.bounds[4])/2 * 1/2 #femur.bounds retuns (xmin, xmax, ymin, ymax, zmin, zmax)
    # origin[2] -= 2 * origin[2]

    # Single slice - origin defaults to the center of the mesh
    single_green = femur.slice(normal=[0, 1, 0], origin=origin)
    single_red = femur.slice(normal=[0, 0, 1], origin=origin)
    r = np.asarray(single_red.points)
    g = np.asarray(single_green.points)

    # Search points only in the specified area. We do not need only points that are located close to the origin
    search_frame = np.max(single_green.points[:, 0]) * 0.5
    r_limited_right = np.asarray(r[(r[:, 0] < (origin[0] + search_frame)) & (r[:, 0] > origin[0])])
    r_limited_left = np.asarray(r[(r[:, 0] > (origin[0] - search_frame)) & (r[:, 0] < origin[0])])

    tree_g = KDTree(g)
    points_sorted_right = sorted([tree_g.query(r_limited_right[0, :]) for i in range(r_limited_right.shape[0])],
                                 key=lambda pair: pair[0])
    points_sorted_left = sorted([tree_g.query(r_limited_left[0, :]) for i in range(r_limited_left.shape[0])],
                                key=lambda pair: pair[0])

    right_point_indx = points_sorted_right[0][1]
    right_point = tree_g.data[right_point_indx]

    left_point_indx = points_sorted_left[0][1]
    left_point = tree_g.data[left_point_indx]

    # We need to modify left or right points, so they will be different only based on x
    y = np.max([right_point[1], left_point[1]])
    z = np.max([right_point[2], left_point[2]])

    left_point = [left_point[0], y, z]
    right_point = [right_point[0], y, z]

    line = pv.Line(right_point, left_point)
    fem_distance = line.length

    return fem_distance, left_point, right_point


def add_femur_gap_distance(patients_knees, data):
    """
    This function adds a new feature: femur gap distance.
    We recommend verifying the output of this function visually as well using plot_femur_gap_subdivisions.
    To do so, this function saves femur_left_gap_p and femur_right_gap_p. These two features should be used to draw the verification line.

    :return: DataFrame with new features "femur_gap_dist", and additional features for verification line drawing "femur_left_gap_p" and "femur_right_gap_p".
    """

    femur_gap_dists = []
    femur_left_gap_ps = []
    femur_right_gap_ps = []

    for key, value in patients_knees.items():
        distance, left_point, right_point = find_femur_gap_distance(value.femur)
        femur_gap_dists.append(distance)
        femur_left_gap_ps.append(left_point)
        femur_right_gap_ps.append(right_point)

    femur_gap_dists_df = pd.DataFrame({'Code': patients_knees.keys(),
                                       'femur_gap_dist': femur_gap_dists,
                                       "femur_left_gap_p": femur_left_gap_ps,
                                       "femur_right_gap_p": femur_right_gap_ps,
                                       })
    data = data.join(femur_gap_dists_df.set_index('Code'), on='Code')

    return data


if __name__ == '__main__':
    # path = Path.joinpath(raw_data_dir, "set_2/9967358M00")
    # knee = KneeGeometry(path)
    #
    # femur = knee.femur
    #
    # origin = femur.center
    # origin[1] = origin[1] / 3
    # origin[2] -= 2 * origin[2]
    #
    # # Single slice - origin defaults to the center of the mesh
    #
    # single_green = femur.slice(normal=[0, 1, 0], origin=origin)
    # single_red = femur.slice(normal=[0, 0, 1], origin=origin)
    #
    # # projected = single_red.project_points_to_plane(origin=origin, normal=(0, 1, 0))
    # # collision, ncol = projected.collision(single_red, cell_tolerance=1)
    # # green_points = single_green.points
    # # projected_points = projected.points
    #
    # r = np.asarray(single_red.points)
    # g = np.asarray(single_green.points)
    # search_frame = np.max(single_green.points[:, 0]) * 0.3
    # r_limited_right = np.asarray(r[(r[:, 0] < (origin[0] + search_frame)) & (r[:, 0] > origin[0])])
    # r_limited_left = np.asarray(r[(r[:, 0] > (origin[0] - search_frame)) & (r[:, 0] < origin[0])])
    #
    # tree = KDTree(g)
    # points_sorted_right = sorted([tree.query(r_limited_right[0, :]) for i in range(r_limited_right.shape[0])],
    #                              key=lambda pair: pair[0])
    # points_sorted_left = sorted([tree.query(r_limited_left[0, :]) for i in range(r_limited_left.shape[0])],
    #                             key=lambda pair: pair[0])
    #
    # right_point_indx = points_sorted_right[0][1]
    # right_point = tree.data[right_point_indx]
    #
    # left_point_indx = points_sorted_left[0][1]
    # left_point = tree.data[left_point_indx]
    #
    # line = pv.Line(right_point, left_point)
    #
    # p = pv.Plotter()
    # p.add_mesh(femur)
    # p.add_mesh(single_green, color="green")
    # p.add_mesh(single_red, color="red")
    # # p.add_mesh(projected, color="yellow")
    # p.add_mesh(line, color="yellow", line_width=10)
    # p.show_axes()
    # p.show()
    # distance = line.length
    #
    # a = 1

    # plotter.show()

# ************************************************************************#

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
    # data = evaluate_cartilage(patients_knees, data)
    #
    # plotter = plot_damaged_status_subdivisions(patients_knees, data)

    data = add_femur_gap_distance(patients_knees, data)
    plotter = plot_femur_gap_subdivisions(patients_knees, data)

    plotter.show()
