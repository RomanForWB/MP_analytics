import modules.files as files
import modules.google_work as google_work
import pandas as pd

GOOGLE_WB_KEY = '1i639nTdBNRp3TyDvA1qPT-QP0RdNaJiwkxBIOPMZoLs'

# stats_table = files.open_table('files/dynamics.xlsx', 'ОСТАТКИ')
# for row in stats_table:
#     print(row)

dynamics_df = pd.read_excel('files/dynamics.xlsx', sheet_name='ОСТАТКИ')
# print(dynamics_df)

worksheet = google_work.open_sheet('1i639nTdBNRp3TyDvA1qPT-QP0RdNaJiwkxBIOPMZoLs', 'Сравнение остатков 07.02')
sku_size_list = google_work.get_columns(worksheet, 1, 2, 6)
new_table = list()
for i in range(len(sku_size_list[0])):
    sku = int(sku_size_list[0][i])
    try: size = int(sku_size_list[1][i])
    except: size = sku_size_list[1][i]
    stats_row = dynamics_df.loc[(dynamics_df['Номенклатура'] == sku) & (dynamics_df['Размер вещи'] == size)]
    if len(stats_row) > 0:
        try: on_the_way = round(stats_row.iloc[0][6])
        except: on_the_way = ''
        try: available = round(stats_row.iloc[0][7])
        except: available = ''
        try: all = round(stats_row.iloc[0][20])
        except: all = ''
        new_table.append([all, available, on_the_way])
    else: new_table.append(['', '', ''])
print(new_table)
worksheet.update('L2', new_table)

# sku = 50110638
# size = 42
# sku_df = dynamics_df.loc[(dynamics_df['Номенклатура'] == sku)]
# print(sku_df)
# stats_row = dynamics_df.loc[(dynamics_df['Номенклатура'] == sku) & (dynamics_df['Размер вещи'] == size)]
# print(stats_row)


