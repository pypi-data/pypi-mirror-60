import math

import mysql.connector
import randorank as rr

# first connect to the db and extract races for the relative "season"
# note that races may recorded on SRL after the period ends
# extracting can be done in any manner you see fit but the data structure before
# calculating scores should be a list of races (which are dictionaries with names as keys
# and times in seconds as values) for each period since periods are calculated as if
# their races happened simultaneously. suppose we have a season of one year and periods
# of four weeks, we should have 13 lists (periods) containing dictionaries for every race
# that happened in four weeks period because 52 / 4 = 13 

def extract():
    conn = mysql.connect(host="localhost", user="", password="", database="")
    cursor = conn.cursor()

    # now we extract all race data for the current "season"
    # need to figure out the best way to implement extracting races from db between dates
    # e.g. these could be manually set in the script. or could be a value in a table
    # in the db.

    # this is an example with hard coded dates. we sort by ascending here for separating into
    # periods later. we use a "season" of 3 months and separate into periods of two weeks each
    # we are only getting the race ids here from the races table which we'll use to wuery
    # the results table for the races themselves.

    # we could also store finished periods as tables in the db and simply query for the results of
    # previous periods instead of extracting all the races in a season. but we'd have to 
    # take care to handle races recorded after their period ends because that period and every
    # subsequent period would need to be recalculated. but if there are no races in older
    # periods, we can just take that period's final results

    # adding new races on an individual basisis also possible. with shorter periods, say 3 months
    # as Kat suggested, the time/performance benefit would be minimal. we should probably
    # calculate either the whole season every time or use the aforementioned method of storing
    # previous period results and recalculating only when necessary
    races_query = "SELECT * FROM races WHERE (date >= '2020-01-01 00:00:01' AND date < '2020-03-31 23:59:59') ORDER BY date ASC"
    cursor.execute(races_query)
    race_ids = cursor.fetchall()
    
    # in this implementation, category information is lost after this step.
    # this is a detail the prod implementation will have to figure out.
    # e.g. you could call extract once for every category and pass the category
    # as an argument or you could restructure this to retain the race goals,
    # still collect *all* the races in this step, then filter later

    # for this example, suppose we only want one category here and the goal *must*
    # have at least one keyword in a collection we call "category" in its goal to be
    # extracted and scored.
    race_ids = filter(lambda x: any(i in x[2] for i in category) , race_ids)

    # we have the ids for every race in the season. now we get those races from the results tables
    all_races = get_races(cursor, race_ids)

    return all_races

def get_races(cursor, race_ids):
    # we also get the date here and return a collection of tuples in the form (race_dict, date)
    # the date is used for separating into periods then discarded
    # (the randorank library only has a Period object right now. i can/plan on adding a Season
    # object that will accept dates and handle this but for now i think the Period object is
    # ergonomic/convenient enough for this kind of continuous ranking)
    
    # we start with an empty collection that we'll fill with race tuples in the form (race_dict, date)
    all_races = []
    for race_id in race_ids:
        race_query = f'SELECT * FROM results WHERE race_id={race_id}'                                   
        date_query = f'SELECT date FROM races where id={race_id}'
        
        cursor.execute(race_query)
        race = cursor.fetchall()
        race = map(lambda x: (x[3], x[4]), race)
        # we filter out banned runners in this step before races are processed
        # this could also be a value/table in the db. just make sure to replace the 
        # variable with a collection of runners you don't want to calculate.
        # also note that we're dealing with the query results in the shape of the data
        # recieved from Synack's srldata db. the zeroth element of the collection in this
        # case (where we have a single race) is the runner's name
        # if the shape changes, the script must change to account
        race = filter(lambda x: x[0] not in filtered_runners, race)                                     
        # transform from a filter object to a dictionary
        race = dict(race)
        # in Synack's db, forfeits are a None value. we need to transform these into Nan for
        # randorank
        race = {k: math.nan if v is None else v for k, v in race.items()}
        
        # now we get the date of the race
        cursor.execute(date_query)
        date = cursor.fetchone()[0]

        # and append the tuple
        race = (race, date)
        all_races.append(race)
    
    # we've collected all the races, return the collection
    return all_races

def separate_periods_weeks(races):
    """
    Divides races into periods of four weeks each
    """

    period_lower = 1
    period_upper = 3
    period_buf = []
    bucket = []
    for race in races:
        # the date part of the race tuples is a python datetime object
        # so isocalendar()[1] is the week in the year (1-52) that the race
        # occurred.

        # this algorithm (hard coded for 2 week periods) will iteratively
        # add races into a "bucket" then once it reaches a race (in the
        # collection of tuples that we sorted earlier) in the next period,
        # the bucket has all of a period's races. it adds that full bucket
        # to period_buf, puts the race (which occurred in the next period)
        # to a new bucket, and starts over
        if period_lower <= race[1].isocalendar()[1] < period_upper:
            bucket.append(race[0])
        else:
            period_buf.append(bucket)
            period_lower += 2
            period_upper += 2
            bucket = []
            bucket.append(race[0])

        if period_lower > 52:
            period_lower = 1
            period_upper = 3
    
    # add the last bucket
    period_buf.append(bucket)

    return period_buf

# in the main function we extract, transform, and load the data
# the specific implementation details need to be adjusted. in this
# example, we're calculating the entire "season" at one time. as
# previously stated, this is not the only way to do this. we could
# for example have a database with tables for every period, write the script
# to be aware of which period we're currently in, and take pre-period values
# from the stored data. performance-wise I think the main bottleneck will not
# be the ranking itself but the data extraction from the db. scoring a
# whole season of one year (~3000 races) from a pickled data set previously extracted
# took less than a second for me on an old laptop. so simply scoring the entire
# season at once for every leaderboard update may not be out of the question
# and would be simplest to concretely implement.

def main():
    # collect all the season's races with the extract function
    season_races = [i for i in extract() if i is not None]

    # separate them into periods. the extract function handles getting all
    # the races *for the active season*. in production we'll need a way for the script
    # to determine the start and end of the active season and also account for
    # races recorded on SRL after their season but happened during the previous
    # season. the period length (my suggestion: 2 week period for 3 month seasons) can
    # be hard coded into the separate_periods_weeks function

    separated_races = separate_periods_weeks(season_races)

    # now we have a list of lists containing dicts for each race *in one category*.
    # when dealing with multiple categories, we'll want to do the next step for each one
    # different categories may also need different glicko constants, but the defaults
    # i've chosen for standard/open should be close enough as a starting point

    # a MultiPeriod has a default set of constants identical to this, but i will
    # add these constants manually for clarity

    example_constants = {'tau': .2,
                         'multi_slope': .008,
                         'multi_cutoff': 6,
                         'norm_factor': 1.3, # this value may need adjusting for categories/different randomizers
                         'initial_rating': 1500,
                         'initial_deviation': 300,
                         'initial_volatility': .23
                        }

    # this list will store a rankings dict {'player name': {'player variable': value}}
    # for every period we're calculating since every period in a season depends on
    # values from the previous season

    period_rankings = []

    # we're iterating over every period here. if we take the approach of storing period
    # results, the prod script can skip to the next iteration and use the stored values
    # where it currently uses period_rankings[-1]. but it must be able to account for
    # races added later and know to update the record of previous periods by re-calculating
    # e.g. on Apr 2 a race is recorded from Mar 29. We are now in the period after this
    # race happened. the script has to calculate the values from the previous period BEFORE
    # it calculates values for the new period. if somehow a race gets recorded from multiple
    # periods ago, the script must know to recalculate the period the race was in and
    # *every* period before the current date to get correct rankings.

    for period in separated_races:
        # we're taking the last race of the period out and adding it later as a demonstration
        # of how single races can be added. this is not necessary, only a demonstration
        # everything in that section of the code can be skipped if we're not adding races
        # mid period and calculating the whole period at once every time we update the LB
        last_race = period[-1]
        period = period[:-1]
        if len(period_rankings) == 0:
            # we're on the first period
            test_period = rr.MultiPeriod()
            test_period.set_constants(example_constants)
        else:
            test_period = rr.MultiPeriod()
            test_period.set_constants(example_constants)
            # if we're not calculating the first period, we add some variables
            # from 
            test_period.add_players(period_rankings[-1])
        for race in period:
            # now we're iterating over every race in the current period
            # we have to check that a race meets two conditions before adding:
            # 1. the race has more than one participant (just in case)
            # 2. at least one person finished and didn't forfeit
            # if we add races that don't meet these conditions, randorank is
            # designed to throw an exception
            if len(race) > 1 and len(list(filter(lambda x: math.isnan(x) is False, race.values()))) >= 1:
                test_period.add_race(race)
        
        # now we are going to try adding the race we removed. this will give the same results
        # as if we hadn't removed it, but we need to take some care with the values we pass.
        
        # notes:
        # pass end=False to the rank() method if the period isn't over and we're getting mid
        # period values. the difference is that we get two variables: delta and variance.
        # delta and variance should *never* be passed from a finished old period to a new
        # period. these values represent the results of all races that the players in the
        # added races have completed so far. what we do is create a new MultiPeriod object,
        # add ONLY the racers in the NEW races we want to add to this period and ONLY
        # add their variance and delta from the mid-period rankings while using their
        # *pre-period* rating, deviation, and volatility (or the default values when
        # applicable such as in the first period or if they haven't raced before ever or
        # in the period being calculated). the default variance and delta are 0. we *don't*
        # need to add any old races from the period to get an accurate score because they
        # are already encoded in the variance and delta.

        # this is kind of cumbersome, simply calculating the whole period or season
        # every time we want to update the leaderboard should be performant enough
        # but we will have to structure this differently for the latter method

        mid_rankings = test_period.rank(end=False)
        # get just the new racers from the race/races we want
        new_racers = last_race.keys()
        new_racer_dict = {}
        # create a dict we can add using the add_players() method containing just the new racers
        # and their appropriate values explained above
        for i in new_racers:
            new_racer_dict[i] = {'rating': test_period.constants['initial_rating'] if (len(period_rankings) == 0 or i not in period_rankings[-1].keys()) else period_rankings[-1][i]['rating'],
                                 'deviation': test_period.constants['initial_deviation'] if (len(period_rankings) == 0 or i not in period_rankings[-1].keys()) else period_rankings[-1][i]['deviation'],
                                 'volatility': test_period.constants['initial_volatility'] if (len(period_rankings) == 0 or i not in period_rankings[-1].keys()) else period_rankings[-1][i]['volatility'],
                                 'variance': mid_rankings[i]['variance'] if i in mid_rankings.keys() else 0,
                                 'delta': mid_rankings[i]['delta'] if i in mid_rankings.keys() else 0,
                                 'inactive_periods': 0}
        # create a new MultiPeriod as per above, add the players, add the races (in this case just
        # one, the last one that we removed earlier)
        test_period2 = rr.MultiPeriod()
        test_period2.add_players(new_racer_dict)
        test_period2.add_race(last_race)
        
        # we use the rankings from this new period and add ONLY the new racers back to the main
        # rankings dict with their new values
        mid_rankings2 = test_period2.rank()
        for i in new_racers:
            mid_rankings[i] = mid_rankings2[i]

        # we MUST zero out the variance and delta values because this ranking dict will be passed
        # to the next period and currently it contains non-zero values for everyone
        for i in mid_rankings.keys():
            mid_rankings[i]['variance'] = 0
            mid_rankings[i]['delta'] = 0

        # we add the finalized period to our collection of period rankings dicts
        # when this loop concludes we have the final data for every period and
        # period_ranking[-1] will be the most current. note that we may want to process
        # this data further such as sorting and we only want to display players with
        # deviations above a certain threshhold (probably in the ballpark of 65-75 with
        # the current glicko constants) on the public leaderboard.
        # also note: with the recommended deviation threshhold, it will take some time
        # for racers to be displayed, analogous to how it may take multiple races
        # to show up on the SRL leaderboard
        period_rankings.append(mid_rankings)

# I used the pandas library and converted final ranking dicts into table-like dataframes
# for sorting, spreadsheets, and the rating histogram. python does have a built in sorted()
# function that can be used as well as an OrderedDict data type in the std lib.
