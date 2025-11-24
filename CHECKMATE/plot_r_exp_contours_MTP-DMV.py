#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# Load data
def load_data(file):
    df = pd.read_csv(file, sep=r'\s+')  # ASCII-safe whitespace
    return df['Mtp'], df['DMV'], df['Best_Individual'], df['Overall_Best']

# Input files
lhc_file = 'summary_results_old.txt'
hl_lhc_file = 'summary_results_HL_LHC_old.txt'

# Load LHC and HL-LHC data
Mtp_lhc, DMV_lhc, r_indiv_lhc, r_overall_lhc = load_data(lhc_file)
Mtp_hl, DMV_hl, r_indiv_hl, r_overall_hl = load_data(hl_lhc_file)

# Create interpolation grid
x_vals = np.arange(1000, 2001, 10)
y_vals = np.arange(100, 701, 10)
grid_x, grid_y = np.meshgrid(x_vals, y_vals)

def interpolate(Mtp, DMV, r_vals):
    points = np.column_stack((Mtp, DMV))
    return griddata(points, r_vals, (grid_x, grid_y), method='linear')

# Interpolate all r-values
r_indiv_lhc_grid = interpolate(Mtp_lhc, DMV_lhc, r_indiv_lhc)
r_overall_lhc_grid = interpolate(Mtp_lhc, DMV_lhc, r_overall_lhc)
r_indiv_hl_grid = interpolate(Mtp_hl, DMV_hl, r_indiv_hl)
r_overall_hl_grid = interpolate(Mtp_hl, DMV_hl, r_overall_hl)

# Start plotting
plt.figure(figsize=(10, 8))  # Half-size figure

# Font size scale
plt.rcParams.update({
    'font.size': 20,
    'axes.labelsize': 20,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'legend.fontsize': 16,
})

# Shading exclusion regions
plt.contourf(grid_x, grid_y, r_overall_lhc_grid, levels=[1, np.nanmax(r_overall_lhc_grid)],
             colors='red', alpha=0.2)
plt.contourf(grid_x, grid_y, r_overall_hl_grid, levels=[1, np.nanmax(r_overall_hl_grid)],
             colors='blue', alpha=0.2)

# r = 1 contours
plt.contour(grid_x, grid_y, r_indiv_lhc_grid, levels=[1], colors='red', linestyles='dashed', linewidths=2)
plt.contour(grid_x, grid_y, r_overall_lhc_grid, levels=[1], colors='red', linestyles='solid', linewidths=2)
plt.contour(grid_x, grid_y, r_indiv_hl_grid, levels=[1], colors='blue', linestyles='dashed', linewidths=2)
plt.contour(grid_x, grid_y, r_overall_hl_grid, levels=[1], colors='blue', linestyles='solid', linewidths=2)

# BM4 point
plt.plot(1950, 100, 'ko', label='BM4 (1950,100)')

# Axes labels (ASCII-safe LaTeX)
plt.xlabel(r'$m_F$ [GeV]')
plt.ylabel(r'$m_F - M_{V_D}$ [GeV]')

# Grid (also over shaded areas)
plt.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.8)

# Ticks
plt.xticks(np.arange(1000, 2101, 100))
plt.text(1950 + 20, 100 + 10, 'BM4', fontsize=20, ha='left', va='bottom', color='black')
# Legend
handles = [
    plt.Line2D([], [], color='red', linestyle='dashed', label='LHC 95\%CL '),
    plt.Line2D([], [], color='red', linestyle='solid', label='LHC 95\%CL combined'),
    plt.Line2D([], [], color='blue', linestyle='dashed', label='HL-LHC 95\%CL '),
    plt.Line2D([], [], color='blue', linestyle='solid', label='HL-LHC 95\%CL combined'),
    plt.Line2D([], [], marker='o', color='k', lw=0, label='BM4 (1950,100)'),
]
plt.legend(handles=handles, loc='upper left')

# Layout and save
plt.tight_layout()
plt.savefig('mtp_dmv_exclusion.pdf')
