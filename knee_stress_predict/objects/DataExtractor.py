from pathlib import Path
import pandas as pd
import os
from knee_stress_predict.config import raw_data_dir
from knee_stress_predict.objects.KneeGeometry import KneeGeometry

patients_knees = {}
data_set_name = "set_2"
data_dir = Path.joinpath(raw_data_dir, data_set_name)
for i, folder_name in enumerate(os.listdir(data_dir)):
    patient_dir = Path.joinpath(data_dir, folder_name)
    patient_knee = KneeGeometry(patient_dir)
    patients_knees[folder_name] = patient_knee

knee_df = pd.DataFrame(columns=['Code','Patella_PN','Femur_PN','Tibia_PN','Patella_Car_PN','Femur_Car_PN','Tibia_M_Car_PN', 'Tibia_L_Car_PN'])

for key, value in patients_knees.items():
    df = {'Code': key,
          'Patella_PN': value.patella.n_points,
          'Femur_PN': value.femur.n_points,
          'Tibia_PN': value.tibia.n_points,
          'Patella_Car_PN': value.pat_cart.n_points,
          'Femur_Car_PN': value.fem_cart.n_points,
          'Tibia_M_Car_PN': value.tibia_cart_med.n_points,
          'Tibia_L_Car_PN': value.tibia_cart_lat.n_points}
    knee_df = knee_df.append(df, ignore_index=True)

