#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pd_clinical_outcome_stats.py
Using the before and after treatment motor scores of Parkison's patients,
this script calculates the motor improvement score and percentage STN activation.
It also performs Wilcoxon signed rank test based on the improvement score and
creates a scatter plot of improvement score and percentage STN activation

Handles the primary functions
"""

import os
import sys
import argparse
import scipy
from scipy import stats
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

SUCCESS = 0
INVALID_DATA = 1
IO_ERROR = 2

def main(argv=None):
    sheet_list = 'LSTN_activation, dvSTN_activation, RSTN_activation'

    try:
        input_excel = get_args(argv)
        process_excel(input_excel)
    except FileNotFoundError as f:
        warning(f'Given input excel - {argv[1]} doesn\'t exist', f)
        return IO_ERROR
    except TypeError as e:
        return INVALID_DATA
    except KeyError as k:
        warning(f'Given excel input should have sheets ({sheet_list})', k)
        return INVALID_DATA

def get_args(argv):
    """ Returns the parsed argument list and return code. """

    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Script to parse given excel to perform statistical analysis ')
    parser.add_argument("-c", "--csv_data_file", dest='excel', help="path to excel workbook", required=True)

    args = None
    args = parser.parse_args(argv)
    if not os.path.isfile(args.excel):
        raise FileNotFoundError()

    return os.path.abspath(args.excel)


def warning(*objs):
    """Writes a message to stderr."""
    print("WARNING: ", *objs, file=sys.stderr)


def process_excel(input_excel):
    """
    Call the function to parse the input excel sheet into dictionary data frames
    and computing STN activation percentage
    """
    print(f'\n\nGiven input : {input_excel}')
    excel = pd.ExcelFile(input_excel)
    sheet_dict  = convert_sheets_to_df_dicts(excel)
    #print(sheet_dict.keys())
    compute_stn_activation(sheet_dict['LSTN_activation'], sheet_dict['dvSTN_activation'], sheet_dict['RSTN_activation'])


def convert_sheets_to_df_dicts(excel):
    """
    Parses the input excel sheets into data frame
    :param excel: object that contains the input excel.
    returns sheet_dict: dictionary with sheet names as key and corresponding dataframe as value
    """
    sheet_dict = {}
    for sheet_name in excel.sheet_names:
        sheet_dict[sheet_name] = excel.parse(sheet_name)

    if 'LSTN_activation' not in sheet_dict or 'dvSTN_activation' not in sheet_dict or 'RSTN_activation' not in sheet_dict :
        raise KeyError()

    return sheet_dict


def compute_stn_activation(lstn_df, dvstn_df, rstn_df):
    """
    Calculate the motor improvement score normalized by the voltage for left and right side
    :param: lstn_df: excel sheet containing the motor scores for left side
    :param: rstn_df: excel sheet containing the motor scores for right side
    :param: dvstn_df: excel sheet containing info to calculate % STN activation
    :return: wilcoxon score and scatter plot of improvement score and % STN activation for both sides
    """

    lstn_improvement_volt = process_lstn_activation(lstn_df)
    rstn_improvement_volt = process_lstn_activation(rstn_df)

    lstn_percent_activation = process_stn_activation(dvstn_df, 'L')
    rstn_percent_activation = process_stn_activation(dvstn_df, 'R')

    # Performing Wilcoxon signed rank test
    p_value = perform_wilcoxon_rank_test(lstn_improvement_volt, rstn_improvement_volt)

    #writing p-values to a file
    out_txt_name = 'wilcoxon_test_out.txt'
    with open(out_txt_name, 'w') as output:
        output.write(f"Wilcoxon_p-values:\n{p_value}")
        print (f"Wilcoxon test output: {out_txt_name}")

    # plotting the improvement score and % STN activation for both sides
    ldat = plt.scatter(lstn_percent_activation, lstn_improvement_volt)
    rdat = plt.scatter(rstn_percent_activation, rstn_improvement_volt)
    plt.title('Parkinsons Patient Data')
    plt.xlabel('STN percent activation (%)')
    plt.ylabel('Voltage normalized motor improvement score')
    plt.legend((ldat, rdat), ('Left Side','Right_side'), loc='upper right')
    #plt.show()
    out_fig_name = 'co_relations.png'
    plt.savefig(out_fig_name)
    print(f"Scatter plot image: {out_fig_name}")

    return SUCCESS


def process_lstn_activation(df):
    """
    Calculates the score improvement normalized by voltage for each patient
    :param:df: contains the two excel sheets 'LSTN', 'RSTN' as dictionaries
    returns: improvement score normalized by voltage for both the sides in each patient
    """
    df = df.sort_values(['Patient'])
    patients = df['Patient']
    side = df['Side']
    motor_score_on_stim = df['Motor score (on stim)']
    motor_score_off_stim = df['Motor score (off stim)']
    voltage = df['Voltage [V]']
    improvement_volt = ((motor_score_off_stim/motor_score_on_stim)/voltage)

    return improvement_volt


def process_stn_activation(df, side):

    """
    Calculates STN activation percentage
    :param df: dictionary containing STN volume and active STN volume for patients
    :param side: side of the brain 'L' or 'R'
    :return: STN activation percentage for each side for all patients
    """

    #print(list(df))
    df = df.sort_values(['Patient'])
    left_stn_vol = df['STN vol (' + side + ') [mm3]']
    left_active_stn = df['VTA inside STN (' + side + ') [mm3]']

    stn_percent_activation = (left_active_stn/left_stn_vol)*100
    return stn_percent_activation


def perform_wilcoxon_rank_test(x,y):
    """
    Performs wilcoxon rank test for two variables
    :param x: Improvement score for left side
    :param y: Improvement score for right side
    :return: p_value from the wilcoxon signed rank test
    """
    return scipy.stats.ranksums(x,y)


if __name__ == "__main__":
    status = main()
    sys.exit(status)
