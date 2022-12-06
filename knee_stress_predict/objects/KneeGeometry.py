from pathlib import Path
import pyvista as pv
from scipy.spatial import KDTree
from knee_stress_predict.config import raw_data_dir
import re
import numpy as np
import os
from pyvista import examples

def generate_points(subset=0.02):
    """A helper to make a 3D NumPy array of points (n_points by 3)"""
    dataset = examples.download_lidar()
    ids = np.random.randint(low=0, high=dataset.n_points - 1, size=int(dataset.n_points * subset))
    return dataset.points[ids]

class KneeGeometry(object):
    def __init__(self, path):
        self.path = path
        self.femur = None
        self.tibia = None
        self.patella = None
        self.fem_cart = None
        self.pat_cart = None
        self.tibia_cart_lat = None
        self.tibia_cart_med = None
        self.get_meshes()

    def get_meshes(self):
        for i, elem_path in enumerate(self.path.rglob('*.inp')):
            elem_mesh = pv.read_meshio(elem_path, file_format="abaqus")
            self.add_to_knee_element(elem_path.name, elem_mesh)

    def add_to_knee_element(self, name, mesh):
        if re.compile("BONE2-FEMUR").match(name):
            self.femur = mesh
        elif re.compile("BONE3-TIBIA").match(name):
            self.tibia = mesh
        elif re.compile("BONE5-PATELLA-").match(name):
            self.patella = mesh
        elif re.compile("FEM_CART").match(name):
            self.fem_cart = mesh
        elif re.compile("PAT_CART").match(name):
            self.pat_cart = mesh
        elif re.compile("TIB_CART_LAT").match(name):
            self.tibia_cart_lat = mesh
        elif re.compile("TIB_CART_MED").match(name):
            self.tibia_cart_med = mesh


if __name__ == '__main__':
    data_set_name = "set_2"
    data_dir = Path.joinpath(raw_data_dir, data_set_name)
    # for i, folder_name in enumerate(os.listdir(data_dir)):
    patient_dir = Path.joinpath(data_dir, "9967358M00")
    knee = KneeGeometry(patient_dir)
    pl = pv.Plotter()
    _ = pl.add_mesh(knee.tibia_cart_med)
    _ = pl.add_mesh(knee.tibia_cart_lat)
    _ = pl.add_mesh(knee.tibia)
    _ = pl.add_mesh(knee.femur)
    _ = pl.add_mesh(knee.patella)
    _ = pl.add_mesh(knee.pat_cart)
    pl.show()



