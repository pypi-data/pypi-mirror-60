import math
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from randorank import MultiPeriod

test_constants = {'tau': .2,
                  'multi_slope': .008,
                  'multi_cutoff': 6,
                  'norm_factor': 1.3,
                  'victory_margin': 600,
                  'initial_rating': 1500,
                  'initial_deviation': 300,
                  'initial_volatility': .24
                 }

all_races = pickle.load(open("racesz3r.rr", "rb"))
#seasons = [all_races[:3], all_races[3:6], all_races[6:9], all_races[9:12]]

period_rankings = []
period_sheets = []
for period in all_races:
    if len(period_rankings) == 0:
        test_period = MultiPeriod()
        test_period.set_constants(test_constants)
    else:
        test_period = MultiPeriod()
        test_period.set_constants(test_constants)
        test_period.add_players(period_rankings[-1])
    
    filtered_period = filter(lambda x: len(x) > 1, period)
    filtered_period = filter(lambda x: len(list(filter(lambda y: math.isnan(y) is False, x.values()))) > 1, period)
    test_period.add_races(list(filtered_period))
    
    mid_rankings = test_period.rank()

    period_rankings.append(mid_rankings)

    test_df = pd.DataFrame.from_dict(mid_rankings, orient='index', columns=['rating', 'deviation', 'volatility', 'variance', 'delta', 'inactive_periods'])
    test_df = test_df.drop('variance', axis=1)
    test_df = test_df.drop('delta', axis=1)
    test_df = test_df.sort_values(by=['rating', 'deviation'], ascending=[False, True])
    test_df.insert(loc=0, column='rank', value=range(1, len(test_df) + 1))
    period_sheets.append(test_df)
    print(f'period done')

final_rankings = period_rankings[-1]

high_deviation = period_sheets[13][period_sheets[13]['deviation'] > 60].index
proc_sheet = period_sheets[13].drop(high_deviation)
proc_sheet = proc_sheet.drop('rank', axis=1)
proc_sheet.insert(loc=0, column='rank', value=range(1, len(proc_sheet) + 1))

with pd.ExcelWriter('scores.xlsx', engine='openpyxl') as writer:
        period_sheets[0].to_excel(writer, sheet_name='Period 1')
        period_sheets[1].to_excel(writer, sheet_name='Period 2')
        period_sheets[2].to_excel(writer, sheet_name='Period 3')
        period_sheets[3].to_excel(writer, sheet_name='Period 4')
        period_sheets[4].to_excel(writer, sheet_name='Period 5')
        period_sheets[5].to_excel(writer, sheet_name='Period 6')
        period_sheets[6].to_excel(writer, sheet_name='Period 7')
        period_sheets[7].to_excel(writer, sheet_name='Period 8')
        period_sheets[8].to_excel(writer, sheet_name='Period 9')
        period_sheets[9].to_excel(writer, sheet_name='Period 10')
        period_sheets[10].to_excel(writer, sheet_name='Period 11')
        period_sheets[11].to_excel(writer, sheet_name='Period 12')
        period_sheets[12].to_excel(writer, sheet_name='Period 13')
        period_sheets[13].to_excel(writer, sheet_name='Final Raw')
        proc_sheet.to_excel(writer, sheet_name='Final Processed')

plt.hist(period_sheets[13]['rating'], 50)
plt.savefig('chart.png')
