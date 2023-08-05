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
                  'initial_rating': 1500,
                  'initial_deviation': 300,
                  'initial_volatility': .23
                 }
test_players = {'etium': {'rating': 1550.0, 
                         'deviation': 32.0,
                         'volatility': 0.01002,
                         #'bolatility': 0.01002,
                         'variance': 20.0,
                         'delta': 3.0},
               'frostbite3030': {'rating': 1650.0, 
                                 'deviation': 24.0,
                                 'volatility': 0.009998,
                                 'variance': 15.0,
                                 'delta': 6.0}
               }
test_race = {'etium': 1768.0, 
             'frostbite3030': 1648.0, 
             'buane': 1598,
             'zelgadissan': 1597.0
             }
test_race2 = {'etium': 1768}

all_races = pickle.load(open("racesz3r.rr", "rb"))


period_rankings = []
period_sheets = []
for period in all_races:
    last_race = period[-1]
    period = period[:-1]
    if len(period_rankings) == 0:
        test_period = MultiPeriod()
        test_period.set_constants(test_constants)
    else:
        test_period = MultiPeriod()
        test_period.set_constants(test_constants)
        test_period.add_players(period_rankings[-1])
    for race in period:
        if len(race) > 1 and len(list(filter(lambda x: math.isnan(x) is False, race.values()))) >= 1:
            test_period.add_race(race)
    
    # test add races mid period
    mid_rankings = test_period.rank(end=False)
    new_racers = last_race.keys()
    new_racer_dict = {}
    for i in new_racers:
        new_racer_dict[i] = {'rating': test_period.constants['initial_rating'] if (len(period_rankings) == 0 or i not in period_rankings[-1].keys()) else period_rankings[-1][i]['rating'],
                             'deviation': test_period.constants['initial_deviation'] if (len(period_rankings) == 0 or i not in period_rankings[-1].keys()) else period_rankings[-1][i]['deviation'],
                             'volatility': test_period.constants['initial_volatility'] if (len(period_rankings) == 0 or i not in period_rankings[-1].keys()) else period_rankings[-1][i]['volatility'],
                             'variance': mid_rankings[i]['variance'] if i in mid_rankings.keys() else 0,
                             'delta': mid_rankings[i]['delta'] if i in mid_rankings.keys() else 0,
                             'inactive_periods': 0}
    test_period2 = MultiPeriod()
    test_period2.add_players(new_racer_dict)
    test_period2.add_race(last_race)
    mid_rankings2 = test_period2.rank()
    for i in new_racers:
        mid_rankings[i] = mid_rankings2[i]

    for i in mid_rankings.keys():
        mid_rankings[i]['variance'] = 0
        mid_rankings[i]['delta'] = 0


    period_rankings.append(mid_rankings)

    test_df = pd.DataFrame.from_dict(mid_rankings, orient='index', columns=['rating', 'deviation', 'volatility', 'variance', 'delta', 'inactive_periods'])
    test_df = test_df.drop('variance', axis=1)
    test_df = test_df.drop('delta', axis=1)
    test_df = test_df.sort_values(by=['rating', 'deviation'], ascending=[False, True])
    test_df.insert(loc=0, column='rank', value=range(1, len(test_df) + 1))
    period_sheets.append(test_df)
    print(f'period done')

final_rankings = period_rankings[-1]

high_deviation = period_sheets[13][period_sheets[13]['deviation'] > 65].index
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
