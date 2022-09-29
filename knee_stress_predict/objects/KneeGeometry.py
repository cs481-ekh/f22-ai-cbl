from pathlib import Path
import pyvista as pv
from knee_stress_predict.config import raw_data_dir
import re


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
    path = Path.joinpath(raw_data_dir, "2022.09.16_Geometries")
    knee = KneeGeometry(path)
    knee.pat_cart.plot(jupyter_backend="static")
