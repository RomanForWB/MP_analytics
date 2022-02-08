import modules.files as files
import pandas as pd

dynamics_df = pd.read_excel('files/dynamics.xlsx', sheet_name='ОСТАТКИ')
print(dynamics_df)