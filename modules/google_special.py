import modules.google_work as google_work
import modules.info as info
import re
from copy import copy
from datetime import date, datetime, timedelta
from statistics import mean

ru_month = {1: 'января',
            2: 'февраля',
            3: 'марта',
            4: 'апреля',
            5: 'мая',
            6: 'июня',
            7: 'июля',
            8: 'августа',
            9: 'сентября',
            10: 'октября',
            11: 'ноября',
            12: 'декабря'}


def day_report(worksheet, report_table):
    first_column = google_work.get_columns(worksheet, 0, 1)
    for i in range(len(first_column)):
        if 'Динамика' in first_column[i]:
            worksheet.delete_rows(1, i-1)
            break

    report_table[0] += ['*% выкупа']
    for i in range(1, len(report_table)):
        day = datetime.strptime(report_table[i][0], '%Y-%m-%d')
        report_table[i][0] = f'{day.day} {ru_month[int(day.month)]}'
        try: report_table[i].append(report_table[i][3]/report_table[i][1])
        except ZeroDivisionError: report_table[i].append(0)

    report_table.append(['Общий итог 7 дней',
                        sum([row[1] for row in report_table[2:]]),
                        sum([row[2] for row in report_table[2:]]),
                        sum([row[3] for row in report_table[2:]]),
                        sum([row[4] for row in report_table[2:]]),
                        sum([row[5] for row in report_table[2:]]),
                        sum([row[6] for row in report_table[2:]]),
                        mean([row[7] for row in report_table[2:]])])
    try: dynamic_1 = report_table[-2][1] / report_table[-3][1] - 1
    except ZeroDivisionError: dynamic_1 = ''
    try: dynamic_1 = report_table[-2][1] / report_table[-3][1] - 1
    except ZeroDivisionError: dynamic_1 = ''
    dynamics_1_row = ['Динамика 1 день',
                      report_table[-2][1] / report_table[-3][1] - 1 if (report_table[-3][1] != 0) else '',
                      report_table[-2][2] / report_table[-3][2] - 1 if (report_table[-3][2] != 0) else '',
                      report_table[-2][3] / report_table[-3][3] - 1 if (report_table[-3][3] != 0) else '',
                      report_table[-2][4] / report_table[-3][4] - 1 if (report_table[-3][4] != 0) else '',
                      report_table[-2][5] / report_table[-3][5] - 1 if (report_table[-3][5] != 0) else '',
                      report_table[-2][6] / report_table[-3][6] - 1 if (report_table[-3][6] != 0) else '',
                      report_table[-2][7] / report_table[-3][7] - 1 if (report_table[-3][7] != 0) else '']
    dynamics_7_row = ['Динамика 7 дней',
                      report_table[-2][1] / report_table[-9][1] - 1 if (report_table[-9][1] != 0) else '',
                      report_table[-2][2] / report_table[-9][2] - 1 if (report_table[-9][1] != 0) else '',
                      report_table[-2][3] / report_table[-9][3] - 1 if (report_table[-9][1] != 0) else '',
                      report_table[-2][4] / report_table[-9][4] - 1 if (report_table[-9][1] != 0) else '',
                      report_table[-2][5] / report_table[-9][5] - 1 if (report_table[-9][1] != 0) else '',
                      report_table[-2][6] / report_table[-9][6] - 1 if (report_table[-9][1] != 0) else '',
                      report_table[-2][7] / report_table[-9][7] - 1 if (report_table[-9][1] != 0) else '']

    google_work.insert_table(worksheet, [dynamics_1_row, dynamics_7_row], start_cell='A2')
    worksheet.insert_rows(report_table)
    worksheet.format('A1:H1', {"textFormat": {"bold": True, "fontFamily": 'Verdana', "fontSize": 12},
                               "backgroundColor": {"red": 0.8515625,
                                                   "green": 0.9296875,
                                                   "blue": 0.94921875}})
    worksheet.format(f'A{len(report_table)}:H{len(report_table)}',
                     {"textFormat": {"bold": True, "fontFamily": 'Verdana', "fontSize": 12},
                      "backgroundColor": {"red": 0.8515625,
                                          "green": 0.9296875,
                                          "blue": 0.94921875}})


def week_report(worksheet, report_table):
    first_column = google_work.get_columns(worksheet, 0, 1)
    plan_row = list()

    for i in range(len(first_column)):
        if 'Динамика' in first_column[i]:

            outcomes = google_work.get_columns(worksheet, 1, 9)[:(i - 3)]
            for k in range(len(outcomes)):
                try: outcomes[k] = int(re.sub(r"[^0-9]", '', outcomes[k]))
                except ValueError: outcomes[k] = 0
            outcomes_column = ['Отгрузки руб.'] + outcomes

            plan = worksheet.row_values(i + 3)[1:]
            plan_row = ['План'] + [int(re.sub("[^0-9]", '', item)) for item in plan]
            plan_row[7] = plan_row[7] / 100
            worksheet.delete_rows(1, i - 1)
            break

    report_table[0] += ['*% выкупа', 'Отгрузки руб.']
    days = [row[0] for row in report_table[1:]]
    for i in range(1, len(report_table)):
        day = datetime.strptime(report_table[i][0], '%Y-%m-%d')
        report_table[i][0] = f'{day.day} {ru_month[int(day.month)]}'
        try: report_table[i].append(report_table[i][3] / report_table[i][1])
        except ZeroDivisionError: report_table[i].append(0)
        try: report_table[i].append(outcomes_column[i])
        except IndexError: report_table[i].append(0)

    report_table.append(['Общий итог недели',
                        sum([row[1] for row in report_table[1:]]),
                        sum([row[2] for row in report_table[1:]]),
                        sum([row[3] for row in report_table[1:]]),
                        sum([row[4] for row in report_table[1:]]),
                        sum([row[5] for row in report_table[1:]]),
                        sum([row[6] for row in report_table[1:]]),
                        sum([row[7] for row in report_table[1:]])/len([row[7] for row in report_table[1:]]),
                        sum([row[8] for row in report_table[1:]])])

    if len(report_table) < 4: dynamics_1_row = ['Динамика 1 день']
    else: dynamics_1_row = ['Динамика 1 день',
                            report_table[-2][1] / report_table[-3][1] - 1 if (report_table[-3][1] != 0) else '',
                            report_table[-2][2] / report_table[-3][2] - 1 if (report_table[-3][2] != 0) else '',
                            report_table[-2][3] / report_table[-3][3] - 1 if (report_table[-3][3] != 0) else '',
                            report_table[-2][4] / report_table[-3][4] - 1 if (report_table[-3][4] != 0) else '',
                            report_table[-2][5] / report_table[-3][5] - 1 if (report_table[-3][5] != 0) else '',
                            report_table[-2][6] / report_table[-3][6] - 1 if (report_table[-3][6] != 0) else '',
                            report_table[-2][7] / report_table[-3][7] - 1 if (report_table[-3][7] != 0) else '',
                            ""]

    fact_row = copy(report_table[-1])
    fact_row[0] = 'Факт'
    gap_row = ['Отставание $',
               plan_row[1] - fact_row[1],
               plan_row[2] - fact_row[2],
               plan_row[3] - fact_row[3],
               plan_row[4] - fact_row[4],
               plan_row[5] - fact_row[5],
               plan_row[6] - fact_row[6],
               '',
               plan_row[8] - fact_row[8]]
    gap_percent_row = ['Отставание',
                       gap_row[1]/plan_row[1],
                       gap_row[2]/plan_row[2],
                       gap_row[3]/plan_row[3],
                       gap_row[4]/plan_row[4],
                       gap_row[5]/plan_row[5],
                       gap_row[6]/plan_row[6],
                       plan_row[7] - fact_row[7],
                       gap_row[8]/plan_row[8]]
    done_row = ['Сделано',
                1 - gap_percent_row[1],
                1 - gap_percent_row[2],
                1 - gap_percent_row[3],
                1 - gap_percent_row[4],
                1 - gap_percent_row[5],
                1 - gap_percent_row[6],
                fact_row[7]/plan_row[7],
                1 - gap_percent_row[8]]
    days_to_end = 7 - len(days)
    if days_to_end <= 0: today_plan_row = ['План на сегодня', '', '', '', '', '', '', '', '']
    else: today_plan_row = ['План на сегодня',
                            gap_row[1]/days_to_end,
                            gap_row[2]/days_to_end,
                            gap_row[3]/days_to_end,
                            gap_row[4]/days_to_end,
                            gap_row[5]/days_to_end,
                            gap_row[6]/days_to_end,
                            plan_row[7],
                            gap_row[8]/days_to_end]
    moving_to_row = ['Идём на $',
                     fact_row[1]/len(days)*7,
                     fact_row[2]/len(days)*7,
                     fact_row[3]/len(days)*7,
                     fact_row[4]/len(days)*7,
                     fact_row[5]/len(days)*7,
                     fact_row[6]/len(days)*7,
                     '',
                     fact_row[8]/len(days)*7]
    moving_to_percent_row = ['Идём на',
                             moving_to_row[1] / plan_row[1],
                             moving_to_row[2] / plan_row[2],
                             moving_to_row[3] / plan_row[3],
                             moving_to_row[4] / plan_row[4],
                             moving_to_row[5] / plan_row[5],
                             moving_to_row[6] / plan_row[6],
                             fact_row[7],
                             moving_to_row[8] / plan_row[8]]

    google_work.insert_table(worksheet, [dynamics_1_row, [''], plan_row, fact_row,
                                         gap_percent_row, gap_row, done_row, today_plan_row,
                                         moving_to_row, moving_to_percent_row], start_cell='A2')
    report_table = report_table[:-1] + [['']]*days_to_end + [report_table[-1]]
    worksheet.insert_rows(report_table)
    worksheet.format('A1:I1', {"textFormat": {"bold": True, "fontFamily": 'Verdana', "fontSize": 12},
                               "backgroundColor": {"red": 0.8515625,
                                                   "green": 0.9296875,
                                                   "blue": 0.94921875}})
    worksheet.format(f'A{len(report_table)}:I{len(report_table)}',
                     {"textFormat": {"bold": True, "fontFamily": 'Verdana', "fontSize": 12},
                      "backgroundColor": {"red": 0.8515625,
                                          "green": 0.9296875,
                                          "blue": 0.94921875}})


def month_report(worksheet, report_table):
    first_column = google_work.get_columns(worksheet, 0, 1)
    plan_row = list()

    for i in range(len(first_column)):
        if 'Динамика' in first_column[i]:

            outcomes = google_work.get_columns(worksheet, 1, 9)[:(i - 3)]
            for k in range(len(outcomes)):
                try: outcomes[k] = int(re.sub("\s+", '', outcomes[k]))
                except ValueError: outcomes[k] = 0
            outcomes_column = ['Отгрузки руб.'] + outcomes

            plan = worksheet.row_values(i+4)[1:]
            plan_row = ['План'] + [int(re.sub("\s+|,|%", '', item)) for item in plan]
            plan_row[7] = plan_row[7]/100
            worksheet.delete_rows(1, i - 1)
            break

    report_table[0] += ['*% выкупа', 'Отгрузки руб.']
    days = [row[0] for row in report_table[1:]]
    for i in range(1, len(report_table)):
        day = datetime.strptime(report_table[i][0], '%Y-%m-%d')
        report_table[i][0] = f'{day.day} {ru_month[int(day.month)]}'
        try: report_table[i].append(report_table[i][3]/report_table[i][1])
        except ZeroDivisionError: report_table[i].append(0)
        try: report_table[i].append(outcomes_column[i])
        except IndexError: report_table[i].append(0)

    report_table.append(['Общий итог месяца',
                        sum([row[1] for row in report_table[1:]]),
                        sum([row[2] for row in report_table[1:]]),
                        sum([row[3] for row in report_table[1:]]),
                        sum([row[4] for row in report_table[1:]]),
                        sum([row[5] for row in report_table[1:]]),
                        sum([row[6] for row in report_table[1:]]),
                        sum([row[7] for row in report_table[1:]])/len([row[7] for row in report_table[1:]]),
                        sum([row[8] for row in report_table[1:]])])

    if len(report_table) < 4: dynamics_1_row = ['Динамика 1 день']
    else: dynamics_1_row = ['Динамика 1 день',
                            report_table[-2][1] / report_table[-3][1] - 1 if (report_table[-3][1] != 0) else '',
                            report_table[-2][2] / report_table[-3][2] - 1 if (report_table[-3][2] != 0) else '',
                            report_table[-2][3] / report_table[-3][3] - 1 if (report_table[-3][3] != 0) else '',
                            report_table[-2][4] / report_table[-3][4] - 1 if (report_table[-3][4] != 0) else '',
                            report_table[-2][5] / report_table[-3][5] - 1 if (report_table[-3][5] != 0) else '',
                            report_table[-2][6] / report_table[-3][6] - 1 if (report_table[-3][6] != 0) else '',
                            report_table[-2][7] / report_table[-3][7] - 1 if (report_table[-3][7] != 0) else '',
                            '']

    if len(report_table) < 10: dynamics_7_row = ['Динамика 7 дней']
    else: dynamics_7_row = ['Динамика 7 дней',
                            report_table[-2][1] / report_table[-9][1] - 1 if (report_table[-9][1] != 0) else '',
                            report_table[-2][2] / report_table[-9][2] - 1 if (report_table[-9][2] != 0) else '',
                            report_table[-2][3] / report_table[-9][3] - 1 if (report_table[-9][3] != 0) else '',
                            report_table[-2][4] / report_table[-9][4] - 1 if (report_table[-9][4] != 0) else '',
                            report_table[-2][5] / report_table[-9][5] - 1 if (report_table[-9][5] != 0) else '',
                            report_table[-2][6] / report_table[-9][6] - 1 if (report_table[-9][6] != 0) else '',
                            report_table[-2][7] / report_table[-9][7] - 1 if (report_table[-9][7] != 0) else '',
                            ""]
    fact_row = copy(report_table[-1])
    fact_row[0] = 'Факт'
    gap_row = ['Отставание $',
               plan_row[1] - fact_row[1],
               plan_row[2] - fact_row[2],
               plan_row[3] - fact_row[3],
               plan_row[4] - fact_row[4],
               plan_row[5] - fact_row[5],
               plan_row[6] - fact_row[6],
               '',
               plan_row[8] - fact_row[8]]
    gap_percent_row = ['Отставание',
                       gap_row[1] / plan_row[1],
                       gap_row[2] / plan_row[2],
                       gap_row[3] / plan_row[3],
                       gap_row[4] / plan_row[4],
                       gap_row[5] / plan_row[5],
                       gap_row[6] / plan_row[6],
                       plan_row[7] - fact_row[7],
                       gap_row[8] / plan_row[8]]
    done_row = ['Сделано',
                1 - gap_percent_row[1],
                1 - gap_percent_row[2],
                1 - gap_percent_row[3],
                1 - gap_percent_row[4],
                1 - gap_percent_row[5],
                1 - gap_percent_row[6],
                fact_row[7] / plan_row[7],
                1 - gap_percent_row[8]]

    first_month_date = info.next_month_start_date(days[-1])
    days_to_end = len(info.days_list(from_date=days[-1], to_date=str(first_month_date))) - 2
    if days_to_end <= 0: today_plan_row = ['План на сегодня', '', '', '', '', '', '', '', '']
    else: today_plan_row = ['План на сегодня',
                            gap_row[1]/days_to_end,
                            gap_row[2]/days_to_end,
                            gap_row[3]/days_to_end,
                            gap_row[4]/days_to_end,
                            gap_row[5]/days_to_end,
                            gap_row[6]/days_to_end,
                            plan_row[7],
                            gap_row[8]/days_to_end]
    moving_to_row = ['Идём на $',
                     fact_row[1]/len(days)*(len(days)+days_to_end),
                     fact_row[2]/len(days)*(len(days)+days_to_end),
                     fact_row[3]/len(days)*(len(days)+days_to_end),
                     fact_row[4]/len(days)*(len(days)+days_to_end),
                     fact_row[5]/len(days)*(len(days)+days_to_end),
                     fact_row[6]/len(days)*(len(days)+days_to_end),
                     '',
                     fact_row[8]/len(days)*(len(days)+days_to_end)]
    moving_to_percent_row = ['Идём на',
                             moving_to_row[1] / plan_row[1],
                             moving_to_row[2] / plan_row[2],
                             moving_to_row[3] / plan_row[3],
                             moving_to_row[4] / plan_row[4],
                             moving_to_row[5] / plan_row[5],
                             moving_to_row[6] / plan_row[6],
                             fact_row[7],
                             moving_to_row[8] / plan_row[8]]

    google_work.insert_table(worksheet, [dynamics_1_row, dynamics_7_row, [''], plan_row, fact_row,
                                         gap_percent_row, gap_row, done_row, today_plan_row,
                                         moving_to_row, moving_to_percent_row], start_cell='A2')
    worksheet.insert_rows(report_table)
    worksheet.format('A1:I1', {"textFormat": {"bold": True, "fontFamily": 'Verdana', "fontSize": 12},
                               "backgroundColor": {"red": 0.8515625,
                                                   "green": 0.9296875,
                                                   "blue": 0.94921875}})
    worksheet.format(f'A{len(report_table)}:I{len(report_table)}',
                     {"textFormat": {"bold": True, "fontFamily": 'Verdana', "fontSize": 12},
                      "backgroundColor": {"red": 0.8515625,
                                          "green": 0.9296875,
                                          "blue": 0.94921875}})