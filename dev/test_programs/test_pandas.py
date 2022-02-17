import pandas as pd

# загрузка датафрейма из Excel-файла
dynamics_df = pd.read_excel('files/dynamics.xlsx', sheet_name='ОСТАТКИ')

sku = 12345678
size = 42

# фильтр по условию, возвращается датафрейм
result_df = dynamics_df.loc[(dynamics_df['Номенклатура'] == sku) & (dynamics_df['Размер вещи'] == size)]

# получение значения датафрейма
seventh_column_first_value = result_df.iloc[0][6]
