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
lhc_file = 'summary_results.txt'
hl_lhc_file = 'summary_results_HL_LHC.txt'

# Load LHC and HL-LHC data
Mtp_lhc, DMV_lhc, r_indiv_lhc, r_overall_lhc = load_data(lhc_file)
Mtp_hl, DMV_hl, r_indiv_hl, r_overall_hl = load_data(hl_lhc_file)

# Create interpolation grid
x_vals = np.arange(1200, 2301, 5)
y_vals = np.arange(0.025, 0.925, 0.01)
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
plt.figure(figsize=(11, 8))  # Half-size figure

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
             colors='red', alpha=0.2, zorder=1)
plt.contourf(grid_x, grid_y, r_overall_hl_grid, levels=[1, np.nanmax(r_overall_hl_grid)],
             colors='blue', alpha=0.2, zorder=2)

# r = 1 contours
plt.contour(grid_x, grid_y, r_indiv_lhc_grid, levels=[1], colors='red', linestyles='dashed', linewidths=2)
plt.contour(grid_x, grid_y, r_overall_lhc_grid, levels=[1], colors='red', linestyles='solid', linewidths=2)
plt.contour(grid_x, grid_y, r_indiv_hl_grid, levels=[1], colors='blue', linestyles='dashed', linewidths=2)
plt.contour(grid_x, grid_y, r_overall_hl_grid, levels=[1], colors='blue', linestyles='solid', linewidths=2)

# BM4 point
MTB=np.array([1792,2200,1950.8])
MVB=np.array([312.6,1255,1876])
DMVB=(MTB-MVB)/MTB
#plt.plot(1950, 100, 'ko', label='BM4')
plt.plot(MTB[0],DMVB[0], 'ko')
plt.plot(MTB[1],DMVB[1], 'ko')
plt.plot(MTB[2],DMVB[2], 'ko')

plt.text(MTB[0]*1.01, DMVB[0]*1.01, 'BM1', fontsize=20, ha='left', va='bottom', color='black')
plt.text(MTB[1]*1.01, DMVB[1]*1.01, 'BM2', fontsize=20, ha='left', va='bottom', color='black')
plt.text(MTB[2]*1.01, DMVB[2]*1.01, 'BM3', fontsize=20, ha='left', va='bottom', color='black')

# Axes labels (ASCII-safe LaTeX)
plt.xlabel(r'$m_F$ [GeV]')
plt.ylabel(r'$(m_F - M_{V_D})/m_F$')


plt.ylim(DMV_lhc.min(), DMV_lhc.max())
plt.xlim(Mtp_lhc.min(), Mtp_lhc.max())
# Ticks
plt.xticks(np.arange(1200, 2301, 100))

# Legend
handles = [
    plt.Line2D([], [], color='red', linestyle='dashed', label='LHC $95\%CL$ '),
    plt.Line2D([], [], color='red', linestyle='solid', label='LHC $95\%CL$ comb'),
    plt.Line2D([], [], color='blue', linestyle='dashed', label='HL-LHC $95\%CL$ '),
    plt.Line2D([], [], color='blue', linestyle='solid', label='HL-LHC $95\%CL$ com'),
]

#plt.legend(handles=handles, loc='upper left')
plt.legend(
    handles=handles,
    loc='upper center',
    bbox_to_anchor=(0.5, 1.13),
    ncol=2,
    frameon=False
)


# Contour lines for fixed M_V values
MV_vals = [200, 300, 500, 700, 900, 1100, 1300, 1500, 1800]  # Add/adjust as you wish
mtp_range = np.linspace(1200, 2300, 500)   # x-axis range

yoffset = 0*0.1 * (plt.ylim()[1] - plt.ylim()[0])
xoffset = 0*0.05 * (plt.xlim()[1] - plt.xlim()[0])

"""
for MV in MV_vals:
    DMV_line = 1 - MV / mtp_range
    # Only keep physical values: 0 < DMV < 1
    mask = (DMV_line > 0) & (DMV_line < 1)
    plt.plot(mtp_range[mask], DMV_line[mask], 'k--', linewidth=1)
    # Label the contour at the left end
    idx = np.argmax(mask)  # first True in mask
    if np.any(mask):
        plt.text(mtp_range[mask][10]+xoffset, DMV_line[mask][10]+yoffset, f'$M_V={MV}$', 
                 fontsize=12, color='k', va='bottom', ha='left', rotation=0)

"""

for MV in MV_vals:
    DMV_line = 1 - MV / mtp_range
    mask = (DMV_line > 0) & (DMV_line < 1)
    x_points = mtp_range[mask]
    y_points = DMV_line[mask]
    plt.plot(x_points, y_points, 'k--', linewidth=1)
    if len(x_points) > 0:
        frac = 0.5   # for middle, use 1/3 or 2/3 as desired
        idx = int(0.1 * (len(x_points) - 1))
        plt.text(
            x_points[idx],
            y_points[idx] + 0.01,   # adjust vertical offset as needed
            f'$M_{{V_D}}={MV}$',
            fontsize=14, color='k', va='bottom', ha='center'
        )
	
# Grid (also over shaded areas)
plt.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=1, zorder=20)


# Layout and save
#plt.tight_layout()
plt.savefig('mtp_dmv_exclusion_new.pdf')
plt.close()
