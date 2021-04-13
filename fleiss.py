#!/usr/bin/env python

import pandas as pd
import glob

def checkInput(rate, n):
    """ 
    Check correctness of the input matrix
    @param rate - ratings matrix
    @return n - number of raters
    @throws AssertionError 
    @author: skarumbaiah
    """
    N = len(rate)
    k = len(rate[0])
    assert all(len(rate[i]) == k for i in range(k)), "Row length != #categories)"
    assert all(isinstance(rate[i][j], int) for i in range(N) for j in range(k)), "Element not integer" 
    assert all(sum(row) == n for row in rate), "Sum of ratings != #raters)"

def fleissKappa(rate,n):
    """ 
    Computes the Kappa value
    @param rate - ratings matrix containing number of ratings for each subject per category 
    [size - N X k where N = #subjects and k = #categories]
    @param n - number of raters   
    @return fleiss' kappa
    @author: skarumbaiah
    """

    N = len(rate)
    k = len(rate[0])
    print("#raters = ", n, ", #subjects = ", N, ", #categories = ", k)
    checkInput(rate, n)

    #mean of the extent to which raters agree for the ith subject 
    PA = sum([(sum([i**2 for i in row])- n) / (n * (n - 1)) for row in rate])/N
    print("PA = ", PA)
    
    # mean of squares of proportion of all assignments which were to jth category
    PE = sum([j**2 for j in [sum([rows[i] for rows in rate])/(N*n) for i in range(k)]])
    print("PE =", PE)
    
    kappa = -float("inf")
    try:
        kappa = (PA - PE) / (1 - PE)
        kappa = float("{:.3f}".format(kappa))
    except ZeroDivisionError:
        print("Expected agreement = 1")

    print("Fleiss' Kappa =", kappa)
    
    return kappa


def gen_df_from_path(path):
  
    all_files = glob.glob(path)

    # Concatenate all CSVs in the specified path into one dataframe
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    if li == []:
        return None

    df = pd.concat(li, axis=0, ignore_index=True)
    return df.sort_values('uid')


if __name__ == "__main__":

    stud_df = gen_df_from_path('ratings/student_evals/*.csv')
    julie_df = gen_df_from_path('ratings/julie_evals/*.csv')
    aryan_df = pd.read_csv('ratings/samples_aryan.csv', index_col=None, header=0)

    d1 = list(stud_df['uid'])
    d2 = list(julie_df['uid'])
    d3 = list(aryan_df['uid'])
    
    for i in range(len(d1)):
        assert(d1[i] == d2[i])
        assert(d2[i] == d3[i])

    r1 = list(stud_df['Correct?'])
    r2 = list(julie_df['Correct?'])
    r3 = list(aryan_df['Correct?'])

    rate = []

    for i in range(len(d1)):
        true = 0
        false = 0

        if r1[i]:
            true += 1
        else:
            false += 1

        if r2[i]:
            true += 1
        else:
            false += 1

        if r3[i] == "True":
            true += 1
        else:
            false += 1

        assert((true + false) == 3)
        rate.append([true,false])

    ratings = pd.DataFrame(rate, columns=['Correct', 'Incorrect'])
    ratings.to_csv('ratings.csv')

    fleissKappa(rate, 3)

