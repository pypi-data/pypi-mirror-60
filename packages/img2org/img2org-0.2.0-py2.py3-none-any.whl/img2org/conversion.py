#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:36:05 2020

@author: henrik
"""
        
import re
import pandas as pd

def read_output_gnuplot(fname, skiprows=0):
    return pd.read_csv(fname, sep=' ', header=None, squeeze=True, skiprows=skiprows).dropna(1).dropna(0)

def create_organism_files(my_dict, init_filepath, neigh_filepath):
    """
    Converts dicionary of cell/PIN data into init and neigh text files which
    can be used by the Organism solver.
    
    Saves data in specified filepaths.
    """
    init = str(len(my_dict)) + " 8"
    neigh = str(len(my_dict)) + " 4"
    
    vals = []
    for r in range(len(my_dict)):
        num_neighs = len(my_dict[r]["neighbors"])
        vals.append([])
        for jj in range(num_neighs):
            val = my_dict[r]["P_ij"][jj]
            vals[-1].append(val)
    
    for r in range(len(my_dict)):
        init += "\n" + " ".join(str(n) for n in my_dict[r]["coords"])
        init += " " + str(float(my_dict[r]["volume"]))
        
        # PIN, auxin, AUX concentrations
        conc = float(my_dict[r]["total_PIN"] / my_dict[r]["volume"])
        for ii in range(3):
            init += " " + str(conc)
        init += " " + str(int(my_dict[r]["L1"])) + " "
        
        num_neighs = len(my_dict[r]["neighbors"])
        neigh += "\n" + str(r) + " " + str(num_neighs) # zero indexed
        neigh += " " + " ".join(str(n-1) for n in my_dict[r]["neighbors"])
        neigh += " " + " ".join(str(n) for n in my_dict[r]["A_ij"])
        for ii in range(2):
            for jj in range(num_neighs):
                neigh += " " + str(my_dict[r]["P_ij"][jj] / sum(my_dict[r]["P_ij"]) / my_dict[r]["A_ij"][jj])
#                neigh += " " + str(my_dict[r]["P_ij"][jj] / my_dict[r]["A_ij"][jj])
                
        total_area = sum(my_dict[r]["A_ij"][jj] for jj in range(num_neighs))
        total_pin = sum(my_dict[r]["P_ij"][jj] / sum(my_dict[r]["P_ij"]) for jj in range(num_neighs)) # 1
        
        for ii in range(num_neighs):
            neigh += " " + str(total_pin / total_area)
        
    with open(init_filepath, 'w') as f1:
        f1.write(init)
    with open(neigh_filepath, 'w') as f2:
        f2.write(neigh)


def gnuplot2newman(fin, fout, n_params, use_every=1, verbose=False):
    data = read_output_gnuplot(fin)
    
    # Account for the number of columns, as this varies between newman and gnuplot
    data = data.loc[:, 0:n_params + 3] # include time, printpoint and cell_id
    data.columns = ['print', 't', 'cell_id', 'n_neighs', 'x', 'y', 'z', 'volume'] + [f'var_{ii}' for ii in range(data.columns.size - 8)]
    data = data.drop_duplicates(['print', 't', 'cell_id'])

    # Get some general parameters
    n_cells = data['cell_id'].unique().shape[0] #len(np.unique(data['cell_id']))
    n_print = data['print'].unique().shape[0]  #len(np.unique(data['print']))
    times = data.drop_duplicates('print').t.values
    
    # Rearrange columns to newman order
    columns = [v for v in data.columns if v not in ['t', 'cell_id', 'n_neighs']] + ['n_neighs']
    data = data.loc[:, columns]

    # Write to file    
    with open(fout, 'w') as f:
        f.write(f'{n_print//use_every}\n')
    
        for ii in range(0, n_print, use_every):
            # Get right time-point and remove pesky whitespaces
            outstring = data.loc[data['print'] == ii, columns[1:]].to_string(index=False, header=False)
            outstring = re.sub('\n\s+', '\n', outstring).strip()
            
            if verbose:
                print(f'Printing time-point {ii//use_every} out of {n_print // use_every}')
            f.write(f'{n_cells} {n_params + 1} {times[ii]}\n')
            f.write(outstring)
            f.write('\n\n')
    