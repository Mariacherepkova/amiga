#!/usr/bin/env python

'''
AMiGA configuration file for setting and modifying default parameters used by AMiGA.
'''

__author__ = "Firas S Midani"
__email__ = "midani@bcm.edu"


# NOTES
#     colors are defined in (R,G,B,A) format where A is alpha and all values range
#     	 from 0.0 to 1.0 (i.e. map 0 to 255) but you can define colors in text or hex
#        string format, see https://het.as.utexas.edu/HET/Software/Matplotlib/api/colors_api.html 

config = {}

###	--------------------- ###
### DATA INPUT PARAMETERS ###
###	--------------------- ###

# acceptable values are seconds, minutes, or hours
config['time_input_unit'] = 'seconds'
config['time_output_unit'] = 'hours'

# default time interval between OD measurments is set to 600 seconds
config['interval'] = 600  # units ared based on 'time_input_unit' above  

# Negative or Zero OD vlaues are raised to the following floor
config['od_floor'] = 0.01

# whether to estimate OD at the first time point using a polynomial regression fit across replicates
config['PolyFit'] = True

###	------------- ###
### 96-Well Plots ###
###	------------- ###

# parameters related to plotting and fold change
config['fcg'] = 1.50  # fold-change threshold for growth
config['fcd'] = 0.50  # fold-change threshold for death

config['fcg_line_color'] = (0.0,0.0,1.0,1.0)
config['fcg_face_color'] = (0.0,0.0,1.0,0.15)

config['fcd_line_color'] = (1.0,0.0,0.0,1.0)
config['fcd_face_color'] = (1.0,0.0,0.0,0.15)

config['fcn_line_color'] = (0.0,0.0,0.0,1.0)  # fc-neutral: i.e. fold-change is within thresholds defined above
config['fcn_face_color'] = (0.0,0.0,0.0,0.15)  # fc-neutral: i.e. fold-change is within thresholds defined above

# parameters related to annotating grid plots with OD Max and Well ID values
config['fcn_well_id_color'] = (0.65,0.165,0.16,0.8)
config['fcn_od_max_color'] = (0.0,0.0,0.0,1.0)

# parameter for labeling y-axis of grid plots
config['grid_plot_y_label'] = 'Optical Density (620 nm)'
config['hypo_plot_y_label'] = 'OD'

###	---------------- ###
### Model Parameters ###
###	---------------- ###

# ard or kernel ?

# for GP regression with input-dependent noise, select a variance smoothing window: 
config['variance_smoothing_window'] = 6 # number of x-values, based on default paramters: 6 * 600 seconds = 1 hour


###	------------------------ ###
### Hypothesis Testing Plots ###
###	------------------------ ###

# hypothesis testing plot colors
config['hypo_colors']  = [(0.11,0.62,0.47),(0.85,0.37,0.01),(0.46,0.44,0.70),
						  (0.91,0.16,0.54),(0.40,0.65,0.12),(0.90,0.67,0.01),
						  (0.62,0.42,0.11),(0.36,0.36,0.36)]  
						  #seagreen, orange, purple, pink, olive, gold, brown, gray

config['HypoPlotParams'] = {'overlay_actual_data':True,
							'plot_linear_od':False,
							'fontsize':15,
							'tick_spacing':5,
							'legend':'inside'}

config['confidence'] = 0.95 # internally, quantile = 1 - (1-confidence)/2

###	----------------- ###
### GROWTH PARAMETERS ###
###	----------------- ###

# diaxuic shift paramters
config['diauxie_ratio_varb'] = 'K' # can be K (max OD) or r (max dOD/dt)
config['diauxie_ratio_min'] = 0.10  # minimum ratio relative to maximum growth or growth rate for each growth phase
config['diauxie_k_min'] = 0.10
 
# parameters for reporting results (not implemented yet)
config['report_parameters'] = ['auc_lin','auc_log','k_lin','k_log','death_lin','death_log',
							   'gr','dr','td','lagC','lagP',
                               'x_k','x_gr','x_dr','diauxie']
#config['report_parameters'] = ['auc_lin','k_lin','lagP','x_dr','diauxie']


# whether growth parameters (K and AUC) are inferred based on the log or linear scale
config['params_scale'] = 'log' # 'log or 'linear'

# how many samples from the posterior funtion are used for estimating mean/std of growth parameters
config['n_posterior_samples'] = 100

###	------------------ ###
### USER COMMUNICATION ###
###	------------------ ###

config['Ignore_RuntimeWarning'] = True
