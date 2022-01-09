import pandas as pd
from IPython.display import display
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def fuzzy_merge(df_left, df_right, keyleft, keyright, threshold=80, limit=3):
    """
    This function uses fuzzywuzzy process.extract to find matching records with threshold score
    :param df_left: the left table to join
    :param df_right: the right table to join
    :param keyleft: key column of the left table
    :param keyright: key column of the right table
    :param threshold: how close the matches should be to return a match, based on Levenshtein distance
    :param limit: the amount of matches that will get returned, these are sorted high to low
    :return: dataframe with boths keys and matches
    """
    s = df_right[keyright].tolist()
    m = df_left[keyleft].apply(lambda x: process.extract(x, s, limit=limit))
    df_left['matches'] = m
    # Explode and Split match column to map score against each row.
    df_matches = df_left.assign(matches=df_left.matches.tolist()).explode('matches')
    df_matches['Tech'], df_matches['Score'] = zip(*df_matches.matches)
    df_matches['Score'] = df_matches['Score'].astype(int)
    df_matches = df_matches[df_matches['Score'] >= threshold]

    return df_matches

def DataPrep():
    # Get raw data from input CR and SR sheets, apply necessary filters , merge based on fuzzy match.
    dfSR = pd.read_excel("D:\inputsheet.xlsx", 'SR Data')
    dfCR = pd.read_excel("D:\inputsheet.xlsx", 'CR Data')

    dfSR[(dfSR['On/Off'] == 'India') & (dfSR['Guidance Input'] != 'Capacity') & (
                dfSR['TalScope SR Status'] == 'Approved') \
         & (dfSR['SR Priority'] == 'Yes') & (dfSR['TalScope SR Status'] == 'Approved') & (
                     dfSR['TalScope SR Status'] == 'Approved')]
    dfCR[(dfCR['On Offshore'] == 'India') & (dfCR['Actual Status'].isin(['Available', 'Proposed']))]

    # dfCR.rename(columns = {'Primary L1':'Primary_L1'}, inplace = True)

    dfSRSkill = pd.DataFrame()
    dfmerge = pd.DataFrame()

    dfSRSkill['SRID'] = dfSR['SRID']
    dfSRSkill['Project Name'] = dfSR['Project Name']
    dfSRSkill['Derived Skill'] = dfSR['Derived Skill (Manual Update)']
    # dfSRSkill['Primary L1'] = dfSR['Derived Skill (Manual Update)']
    # dfSRSkill['Primary L2'] = dfSR['Derived Skill (Manual Update)']
    # dfSRSkill['Primary L3'] = dfSR['Derived Skill (Manual Update)']
    # dfSRSkill['Primary L4'] = dfSR['Derived Skill (Manual Update)']

    dffuzzyL4 = fuzzy_merge(dfSRSkill, dfCR, 'Derived Skill', 'Primary L4', threshold=70)
    # Total Score - 50
    dffuzzyL4['Score'] = dffuzzyL4['Score'].div(2)
    dffuzzyL3 = fuzzy_merge(dfSRSkill, dfCR, 'Derived Skill', 'Primary L3', threshold=70)
    # Total Score - 33
    dffuzzyL3['Score'] = dffuzzyL3['Score'].div(3)
    dffuzzyL2 = fuzzy_merge(dfSRSkill, dfCR, 'Derived Skill', 'Primary L2', threshold=70)
    # Total Score - 25
    dffuzzyL2['Score'] = dffuzzyL2['Score'].div(4)
    dffuzzyL1 = fuzzy_merge(dfSRSkill, dfCR, 'Derived Skill', 'Primary L1', threshold=70)
    # Total Score - 20
    dffuzzyL1['Score'] = dffuzzyL1['Score'].div(5)

    # dffuzzyL2.to_excel('D:\outputsheetF.xlsx')

    dfAllScore = pd.concat([
        pd.merge(dffuzzyL4, dfCR, how="inner", left_on=['Tech'], right_on=['Primary L4']).drop_duplicates(),
        pd.merge(dffuzzyL3, dfCR, how="inner", left_on=['Tech'], right_on=['Primary L3']).drop_duplicates(),
        pd.merge(dffuzzyL2, dfCR, how="inner", left_on=['Tech'], right_on=['Primary L2']).drop_duplicates(),
        pd.merge(dffuzzyL1, dfCR, how="inner", left_on=['Tech'], right_on=['Primary L1']).drop_duplicates()]
    )

    # dfAllScore.to_excel('D:\outputsheetF.xlsx')
    # dfFinal = dfAllScore.groupby(['SRID','Project Name','Tech','Employee','Employee Name'])['Score'].sum().to_excel('D:\outputsheetF.xlsx')

    # dfAllScoreAgg = dfAllScore[['SRID','Tech','Employee ID','Project Name','Employee Name','Actual Status','Proposed Date','Score']].copy()
    # dfAllScoreAgg.to_excel('D:\outputsheetF.xlsx')
    dfAllScore = dfAllScore.groupby(['SRID','Project Name','Derived Skill','Employee ID','Employee Name','Tech','Actual Status'])['Score'].sum()
        # .to_excel('D:\outputsheetF.xlsx')
    # dfAllScore['Score'] = dfAllScore['Score'].astype(int)
    # dfAllScore['PercentageScore'] = (dfAllScore['Score']/133) * 100
    # dfAllScore.to_excel('D:\outputsheetF.xlsx')
    dfAllScore = dfAllScore.reset_index().rename(columns= {'Employee ID': 'Employee_ID', 'Project Name': 'Project_Name',
                                'Employee Name': 'Employee_Name','Actual Status': 'Actual_Status', 'Tech' : 'Employee_Skill'})
    return dfAllScore



DataPrep()


