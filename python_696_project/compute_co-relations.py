#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
data_analysis.py
Preliminary data analysis from csv

Handles the primary functions
"""

import os
import sys
import argparse
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')


def main():
    input_excel = get_args()
    print(f'\n\nGiven input : {input_excel}')
    process_excel(input_excel)


def get_args():
    """ Returns the parsed argument list and return code. """

    parser = argparse.ArgumentParser(description='Script to parse given excel to perform statistical analysis ')
    parser.add_argument("-c", "--csv_data_file", dest='excel', help="path to excel workbook", required=True)
    args = parser.parse_args()

    if not os.path.isfile(args.excel):
        raise FileNotFoundError
    elif os.stat(args.excel).st_size == 0:
        print(f'\n\nERROR: {args.excel} is empty\n\n')
        sys.exit(1)

    return os.path.abspath(args.excel)


def process_excel(input_excel):

    excel = pd.ExcelFile(input_excel)
    sheet_dict = convert_sheets_to_df_dicts(excel)
    compute_stn_activation(sheet_dict['LSTN_activation'], sheet_dict['dvSTN_activation'],
                           sheet_dict['RSTN_activation'])


def convert_sheets_to_df_dicts(excel):
    sheet_dict = {}
    for sheet_name in excel.sheet_names:
        sheet_dict[sheet_name] = excel.parse(sheet_name)
    return sheet_dict


def compute_stn_activation(lstn_df, dvstn_df, rstn_df):
    lstn_improvement_volt = process_lstn_activation(lstn_df)
    rstn_improvement_volt = process_lstn_activation(rstn_df)

    lstn_percent_activation = process_stn_activation(dvstn_df, 'L')
    rstn_percent_activation = process_stn_activation(dvstn_df, 'R')

    #print(rstn_percent_activation.corr(rstn_improvement_volt))
    #print(lstn_percent_activation.corr(lstn_improvement_volt))
    print(lstn_percent_activation)
    print(rstn_percent_activation)
    plt.scatter(lstn_percent_activation, lstn_improvement_volt)
    plt.scatter(rstn_percent_activation, rstn_improvement_volt)
    plt.show()


def process_lstn_activation(df):

    df = df.sort_values(['Patient'])
    patients = df['Patient']
    side = df['Side']
    motor_score_on_stim = df['Motor score (on stim)']
    motor_score_off_stim = df['Motor score (off stim)']
    voltage = df['Voltage [V]']
    improvement_volt = ((motor_score_off_stim/motor_score_on_stim)/voltage)

    return improvement_volt


def process_stn_activation(df, side):

    df = df.sort_values(['Patient'])
    dstn_vol = df['dSTN vol (' + side + ') [mm3]']
    vstn_vol = df['vSTN vol (' + side + ') [mm3]']
    left_stn_vol = dstn_vol + vstn_vol

    vta_inside_dstn = df['VTA inside dSTN (' + side + ') [mm3]']
    vta_inside_vstn = df['VTA inside vSTN (' + side + ') [mm3]']
    left_active_stn = vta_inside_dstn + vta_inside_vstn

    stn_percent_activation = (left_active_stn/left_stn_vol)*100
    return stn_percent_activation


if __name__ == "__main__":
    main()
