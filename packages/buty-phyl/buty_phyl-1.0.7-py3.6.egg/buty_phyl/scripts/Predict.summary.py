import os
import glob
import pandas as pd
import numpy as np
import argparse

############################################ Arguments and declarations ##############################################
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-i",
                    help="result folder of buty_phyl prediction", type=str,
                    default='ButyPhyl',metavar='ButyPhyl')
parser.add_argument("-r",
                    help="result folder of the summary", type=str,
                    default='ButyPhyl_summary',metavar='ButyPhyl_summary')

################################################## Definition ########################################################
args = parser.parse_args()
try:
    os.mkdir(args.r)
except OSError:
    pass

################################################### Function ########################################################
def read_species(filename):
    return pd.read_csv(filename, sep='\t',index_col=0,header=0)

def merge_pathogen_commensal(df1, df2):
    filename = df1.columns[0] + '.sum'
    temp_species_df = pd.merge(df1, df2,
    how='outer', left_index = True, right_index = True)
    return pd.DataFrame(temp_species_df.sum(axis = 1), columns = [filename])

def add_pathogen_commensal(df1,df2):
    temp_abu_df = df1
    temp_abu_df['Abu_with_Traits'][0] = df1['Abu_with_Traits'][0] + df2['Abu_with_Traits'][0]
    return temp_abu_df

################################################### Programme #######################################################
result_species = glob.glob(os.path.join(args.i,'*.bpbspecies.commensal.abu'))
result_abu = glob.glob(os.path.join(args.i,'*.infertraits.commensal.abu'))

if result_species != []:
    i = 0
    for commensal_species in result_species:
        pathogen_species = commensal_species.replace('commensal','pathogen')
        pathogen_species_df = read_species(pathogen_species)
        commensal_species_df = read_species(commensal_species)
        if i == 0:
            all_species_df = merge_pathogen_commensal(pathogen_species_df, commensal_species_df)
        else:
            all_species_df = pd.merge(all_species_df,
            merge_pathogen_commensal(pathogen_species_df, commensal_species_df),
            how='outer', left_index = True, right_index = True)
        i += 1
    all_species_df.to_csv(os.path.join(args.r, 'all.bpbspecies.abu'), sep='\t',
                  header=True)

if result_abu != []:
    i = 0
    for commensal_abu in result_abu:
        pathogen_abu = commensal_abu.replace('commensal','pathogen')
        pathogen_abu_df = read_species(pathogen_abu)
        commensal_abu_df = read_species(commensal_abu)
        if i == 0:
            all_abu_df = add_pathogen_commensal(pathogen_abu_df, commensal_abu_df)
        else:
            all_abu_df = all_abu_df.append(add_pathogen_commensal(pathogen_abu_df, commensal_abu_df))
        i += 1
    all_abu_df.to_csv(os.path.join(args.r, 'all.bpb.abu'), sep='\t',
                  header=True)
