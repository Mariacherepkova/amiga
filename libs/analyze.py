#!/usr/bin/env python

'''
AMiGA library of functions for analyzing growth curves.
'''

__author__ = "Firas S Midani"
__email__ = "midani@bcm.edu"


# TABLE OF CONTENTS (9 functions)

# basicSummaryOnly
# runGrowthFitting
# runCombinedGrowthFitting
# prepDataForFitting
# normalizeParameters
# normalizePooledParameters
# savePlots
# prepGpData
# savePlateData
# mergeSummaryData

import pandas as pd
import numpy as np
import tempfile
import sys
import os

from libs.model import GrowthModel 
from libs.growth import GrowthPlate
from libs.org import assembleFullName, assemblePath
from libs.utils import concatFileDfs, resetNameIndex, subsetDf
from libs.utils import getValue, getTimeUnits, selectFileName
from libs.comm import *
from libs.params import *
from libs.interface import checkParameterCommand


def basicSummaryOnly(data,mapping,directory,args,verbose=False):
    '''
    If user only requested plotting, then for  each data file, perform a basic algebraic summary
        and plot data. Once completed, exit system. Otherwise, return None.
 
    Args:
        data (dictionary): keys are plate IDs and values are pandas.DataFrames with size t x (n+1)
            where t is the number of time-points and n is number of wells (i.e. samples),
            the additional 1 is due to the explicit 'Time' column, index is uninformative.
        mapping (dictionary): keys are plate IDs and values are pandas.DataFrames with size n x (p)
            where is the number of wells (or samples) in plate, and p are the number of variables or
            parameters described in dataframe.
        directory (dictionary): keys are folder names, values are their paths
        args
        verbose (boolean)

    Returns:
        None: if only_plot_plate argument is False. 
    '''

    if not args['obs']:  # if not only_basic_summary
        return None

    print(tidyMessage('AMiGA is summarizing and plotting data files'))

    list_keys = []

    for pid,data_df in data.items():

        # define paths where summary and plot will be saved
        key_file_path = assemblePath(directory['summary'],pid,'.txt')
        key_fig_path = assemblePath(directory['figures'],pid,'.pdf')

        # grab plate-specific samples
        #   index should be well IDs but a      column Well should also exist
        #   in main.py, annotateMappings() is called which ensures the above is the case
        mapping_df = mapping[pid]
        mapping_df = resetNameIndex(mapping_df,'Well',False)

        # grab plate-specific data
        wells = list(mapping_df.Well.values)
        data_df = data_df.loc[:,['Time']+wells]

        # update plate-specific data with unique Sample Identifiers 
        sample_ids = list(mapping_df.index.values)
        data_df.columns = ['Time'] + sample_ids

        # create GrowthPlate object, perform basic summary
        plate = GrowthPlate(data=data_df,key=mapping_df)
        plate.convertTimeUnits(input=getTimeUnits('input'),output=getTimeUnits('output'))
        plate.computeBasicSummary()
        plate.computeFoldChange(subtract_baseline=True)

        # plot and save as PDF, also save key as TXT
        if not args['dp']:
            plate.plot(key_fig_path)

        if args['merges']: list_keys.append(plate.key) 
        else: plate.key.to_csv(key_file_path,sep='\t',header=True,index=False)

        smartPrint(pid,verbose=verbose)

    if args['merges']:
        filename = selectFileName(args['fout'])
        summary_path = assembleFullName(directory['summary'],'summary',filename,'_basic','.txt')
        summary_df = pd.concat(list_keys,sort=False)
        summary_df.to_csv(summary_path,sep='\t',header=True,index=False)

    smartPrint('\nSee {} for summary text file(s).'.format(directory['summary']),verbose)
    smartPrint('See {} for figure PDF(s).\n'.format(directory['figures']),verbose)

    msg = 'AMiGA completed your request and '
    msg += 'wishes you good luck with the analysis!'
    print(tidyMessage(msg))

    sys.exit()


def runGrowthFitting(data,mapping,directory,args,verbose=False):
    '''
    Uses Gaussian Processes to fit growth curves and infer paramters of growth kinetics.  

    Args:
        data (pandas.DataFrame): number of time points (t) x number of variables plus-one (p+1)
            plus-one because Time is not an index but rather a column.
        mapping (pandas.DataFrame): number of wells/samples (n) x number of variables (p)
        directory (dictionary): keys are folder names, values are their paths
        args (dictionary): keys are arguments and value are user/default choices
        verbose (boolean)

    Action:
        saves summary text file(s) in summary folder in the parent directory.
        saves figures (PDFs) in figures folder in the parent directory.
        saves data text file(s) in derived folder in the parent directory.
    '''

    if args['pool']:
        runCombinedGrowthFitting(data,mapping,directory,args,verbose=verbose)
        return None

    # only store data if user requested its writing or requested plotting
    if args['sgd'] or args['plot'] or args['pd']: store = True
    else: store = False

    # if user requested merging of summary/data, store each plate's data/summary in temp directory first
    tmpdir = tempfile.mkdtemp()
    saved_umask = os.umask(0o77)  ## files can only be read/written by creator for security
    print('Temporary directory is {}\n'.format(tmpdir))

    # pre-process data
    plate = prepDataForFitting(data,mapping,subtract_baseline=True)

    dx_ratio_varb = getValue('diauxie_ratio_varb')
    dx_ratio_min = getValue('diauxie_ratio_min')
 
    ls_temp_files = []
    ls_summ_files = []
    ls_diux_files = []

    # for each plate, get samples and save individual text file for plate-specific summaries
    for pid in plate.key.Plate_ID.unique():

        smartPrint('Fitting {}'.format(pid),verbose)

        # grab plate-specific summary
        sub_plate = plate.extractGrowthData(args_dict={'Plate_ID':pid})

        # the primary motivation of this function: run gp model 
        sub_plate.model(nthin=args['nthin'],store=store,verbose=verbose)

        # normalize parameters, if requested
        sub_plate.key = normalizeParameters(args,sub_plate.key)

        # save plots, if requested by user
        savePlots(sub_plate,args,directory,pid)
        
        # define file paths where data will be written
        if args['merges']:
            temp_path = assembleFullName(tmpdir,'',pid,'gp_data','.txt')
            summ_path = assembleFullName(tmpdir,'',pid,'summary','.txt') 
            diux_path = assembleFullName(tmpdir,'',pid,'diauxie','.txt') 
        else:
            temp_path = assembleFullName(directory['derived'],'',pid,'gp_data','.txt')
            summ_path = assembleFullName(directory['summary'],'',pid,'summary','.txt')
            diux_path = assembleFullName(directory['summary'],'',pid,'diauxie','.txt')

        # save data, if requested by user
        savePlateData(args['sgd'],sub_plate,temp_path,summ_path,diux_path)

        # track all potentially created files
        ls_temp_files.append(temp_path)
        ls_summ_files.append(summ_path)
        ls_diux_files.append(diux_path)

    # if user did not pass file name for output, use time stamp, see selectFileName()
    filename = selectFileName(args['fout'])

    # if user requested merging, merge all files in temporary directory
    mergeSummaryData(args,directory,ls_temp_files,ls_summ_files,ls_diux_files,filename)

    # remove temporary directory
    os.umask(saved_umask)
    os.rmdir(tmpdir)

    return None


def runCombinedGrowthFitting(data,mapping,directory,args,verbose=False):
    '''
    Uses Gaussian Processes to fit growth curves and infer paramters of growth kinetics.
        While runGrowthFitting() analyzes data one plate at a time, runCombinedGrowthFitting()
        can pool experimental replicates across different plates. The downside is that data
        summary must be merged and no 96-well plate grid figure can be produced.  

    Args:
        data (pandas.DataFrame): number of time points (t) x number of variables plus-one (p+1)
            plus-one because Time is not an index but rather a column.
        mapping (pandas.DataFrame): number of wells/samples (n) x number of variables (p)
        directory (dictionary): keys are folder names, values are their paths
        args (dictionary): keys are arguments and value are user/default choices
        verbose (boolean)

    Action:
        saves summary text file(s) in summary folder in the parent directory.
        saves figures (PDFs) in figures folder in the parent directory.
        saves data text file(s) in derived folder in the parent directory.
    '''   

    # if user did not pass file name for output, use time stamp, see selectFileName()
    filename = selectFileName(args['fout'])

    # pre-process data
    plate = prepDataForFitting(data,mapping,subtract_baseline=False)

    # which meta-data variables do you use to group replicates?
    combine_keys = args['pb'].split(',')
    missing_keys = [ii for ii in combine_keys if ii not in plate.key.columns]

    if missing_keys:
        msg = 'FATAL USER ERROR: The following keys {} are '.format(missing_keys)
        msg += 'missing from mapping files.'
        sys.exit(msg)

    # continue processing data
    plate.subtractBaseline(to_do=True,poly=getValue('PolyFit'),groupby=combine_keys)
    plate_key = plate.key.copy()
    plate_data = plate.data.copy()
    plate_time = plate.time.copy()
    plate_cond = plate_key.loc[:,combine_keys+['Group','Control']].drop_duplicates(combine_keys).reset_index(drop=True)

    smartPrint('AMiGA detected {} unique conditions.\n'.format(plate_cond.shape[0]),verbose)

    data_ls, diauxie_dict = [], {}

    # get user-defined values from config.py
    dx_ratio_varb = getValue('diauxie_ratio_varb')
    dx_ratio_min = getValue('diauxie_ratio_min')
    posterior_n = getValue('n_posterior_samples')
    scale = getValue('params_scale')

    posterior = args['slf']
    fix_noise = args['fn']
    nthin = args['nthin']

    # initialize empty dataframes for storing growth parameters
    params_latent = initParamDf(plate_cond.index,complexity=0)
    params_sample = initParamDf(plate_cond.index,complexity=1)

    # for each unique condition based on user request
    for idx,condition in plate_cond.iterrows():

        # get list of sample IDs
        cond_dict = condition.drop(['Group','Control'])
        cond_dict = cond_dict.to_dict() # e.g. {'Substate':['D-Trehalose'],'PM':[1]} 
        cond_idx = subsetDf(plate_key,cond_dict).index.values  # list of index values for N samples
        smartPrint('Fitting\n{}'.format(tidyDictPrint(cond_dict)),verbose)

        # get data and format for GP instance
        cond_data = plate_data.loc[:,list(cond_idx)] # T x N
        cond_data = plate_time.join(cond_data) # T x N+1

        cond_data = cond_data.melt(id_vars='Time',var_name='Sample_ID',value_name='OD')
        cond_data = cond_data.drop(['Sample_ID'],axis=1) # T*R x 2 (where R is number of replicates)
        cond_data = cond_data.dropna()
        
        gm = GrowthModel(df=cond_data,ARD=True,heteroscedastic=fix_noise,nthin=nthin)#,

        curve = gm.run(name=idx)

        # get parameter estimates using latent function
        diauxie_dict[idx] = curve.params.pop('df_dx')
        params_latent.loc[idx,:] = curve.params

        # get parameter estimates using samples fom the posterior distribution
        if posterior: params_sample.loc[idx,:] = curve.sample().posterior

        # passively save data, manipulation occurs below (input OD, GP fit, & GP derivative)
        if args['sgd']:
            time = pd.DataFrame(gm.x_new,columns=['Time'])
            mu0,var0 = np.ravel(gm.y0),np.ravel(np.diag(gm.cov0))
            mu1,var1 = np.ravel(gm.y1),np.ravel(np.diag(gm.cov1))

            if fix_noise: sigma_noise = np.ravel(gm.error_new)+gm.noise
            else: sigma_noise = np.ravel([gm.noise]*time.shape[0])

            mu_var = pd.DataFrame([mu0,var0,mu1,var1,sigma_noise],index=['mu','Sigma','mu1','Sigma1','Noise']).T
            gp_data = pd.DataFrame([list(condition.values)]*len(mu0),columns=condition.keys())
            gp_data = gp_data.join(time).join(mu_var)
            data_ls.append(gp_data)

    # summarize diauxie results
    diauxie_df = mergeDiauxieDfs(diauxie_dict)

    if posterior: gp_params = params_sample.join(params_latent['diauxie'])
    else: gp_params = params_latent

    # record results in object's key
    plate_cond = plate_cond.join(gp_params)
    plate_cond.index.name = 'Sample_ID'
    plate_cond = plate_cond.reset_index(drop=False)
    plate_cond = pd.merge(plate_cond,diauxie_df,on='Sample_ID')

    params = initParamList(0) + initParamList(1)
    params = list(set(params).intersection(set(plate_cond.keys())))

    df_params = plate_cond.drop(initDiauxieList(),axis=1).drop_duplicates()
    df_diauxie = plate_cond[plate_cond.diauxie==1]
    df_diauxie = df_diauxie.drop(params,axis=1)
    df_diauxie = minimizeDiauxieReport(df_diauxie)

    summ_path = assembleFullName(directory['summary'],'',filename,'summary','.txt')
    diux_path = assembleFullName(directory['summary'],'',filename,'diauxie','.txt')

    # normalize parameters, if requested
    df_params = normalizePooledParameters(args,df_params)
    df_params = df_params.drop(['Group','Control'],1)
    df_params = minimizeParameterReport(df_params)

    # save results
    df_params.to_csv(summ_path,sep='\t',header=True,index=False)
    if df_diauxie.shape[0]>0:
        df_diauxie.to_csv(diux_path,sep='\t',header=True,index=False)

    # save latent functions
    if args['sgd']:
        file_path = assembleFullName(directory['derived'],'',filename,'gp_data','.txt')
        gp_data = pd.concat(data_ls,sort=False).reset_index(drop=True)
        gp_data.to_csv(file_path,sep='\t',header=True,index=True)

    return None


def prepDataForFitting(data,mapping,subtract_baseline=True):
    '''
    Packages data set into a grwoth.GrowthPlate() object and transforms data in preparation for GP fitting.

    Args:
        data (pandas.DataFrame): number of time points (t) x number of variables plus-one (p+1)
            plus-one because Time is not an index but rather a column.
        mapping (pandas.DataFrame): number of wells/samples (n) x number of variables (p)
       
    Returns:
        plate (growth.GrwothPlate() object)
    '''

    # merge data-sets for easier analysis and perform basic summaries and manipulations
    plate = GrowthPlate(data=data,key=mapping)

    plate.computeBasicSummary()
    plate.computeFoldChange(subtract_baseline=subtract_baseline)
    plate.convertTimeUnits(input=getTimeUnits('input'),output=getTimeUnits('output'))
    plate.raiseData()  # replace non-positive values, necessary prior to log-transformation
    plate.logData()  # natural-log transform
    plate.subtractBaseline(subtract_baseline,poly=True)  # subtract first T0 (or rather divide by first T0)

    return plate


def normalizeParameters(args,df):
    '''
    Normalizes growth parameters to control samples. 

    Args:
        args (dictionary): keys are arguments and value are user/default choices
        df (pandas.DataFrame): rows are samples, columns are experimental variables. Must include
            Plate_ID, Group, Control, auc, k, gr, dr, td, lag.

    Returns:
        df (pandas.DataFrame): input but with an additional 6 columns.
    '''

    if not args['norm'] or args['pool']: return df
    
    df_orig = df.copy()
    df_orig_keys = df_orig.columns 
    
    params_1 = initParamList(0)
    params_1.remove('diauxie')
    params_2 = ['mean({})'.format(ii) for ii in params_1]

    if any([ii in df_orig_keys for ii in params_2]): params = params_2
    else: params = params_1

    params_norm = initParamList(2)
    params_keep = ['Group','Control'] + params
    
    df = df.loc[:,['Plate_ID']+params_keep]
    
    for pid in df.Plate_ID.unique():
        
        df_plate = df[df.Plate_ID==pid].loc[:,params_keep]
        
        for group in df_plate.Group.unique():
            
            df_group = df_plate[df_plate.Group == group].astype(float)
            df_group = df_group / df_group[df_group.Control==1].mean() 
            df.loc[df_group.index,params_keep] = df_group.loc[:,params_keep]
            
    df = df.loc[:,params]
    df.columns = params_norm
    df = df_orig.join(df)
            
    return df     


def normalizePooledParameters(args,df):
    '''
    Normalizes growth parameters to control samples for pooled parametes. 

    Args:
        args (dictionary): keys are arguments and value are user/default choices
        df (pandas.DataFrame): rows are samples, columns are experimental variables. Must include
            Plate_ID, Group, Control, auc, k, gr, dr, td, lag.

    Returns:
        df (pandas.DataFrame): input but with an additional 6 columns.
    '''

    if (not args['norm']) or (not args['pool']): return df   

    df_orig = df.copy()
    df_orig_keys = df_orig.columns 

    poolby = args['pb'].split(',')
    normalizeby = checkParameterCommand(args['nb'])

    params_1 = initParamList(0)
    params_1.remove('diauxie')
    params_2 = ['mean({})'.format(ii) for ii in params_1]
    if any([ii in df_orig_keys for ii in params_2]): params = params_2
    else: params = params_1

    params_norm = initParamList(2)
    params_keep = ['Sample_ID'] + poolby + params

    df = df.loc[:,params_keep]
    controls = subsetDf(df,normalizeby)
    variable = list(set(poolby).difference(set(normalizeby.keys())))

    norm_df = []
    for _,row in df[variable].drop_duplicates().iterrows():

        sub_df = subsetDf(df,row.to_dict()).set_index(['Sample_ID']+poolby)
        sub_ctrl = subsetDf(controls,row.to_dict()).set_index(['Sample_ID']+poolby)
        norm_df.append((sub_df / sub_ctrl.values))#.reset_index())
        
    norm_df = pd.concat(norm_df,0)
    norm_df.columns = params_norm
    norm_df = norm_df.reset_index(drop=False)

    df = pd.merge(df_orig,norm_df,on=['Sample_ID']+poolby)
    #df = df.drop(['Group','Control'],1)

    return df


def savePlots(plate,args,directory,filename):
    '''
    Saves the GP model fits of grwoth.GrowthPlate() object as a plot. 

    Args:
        plate (growth.GrwothPlate() object)
        args (dictionary): keys are arguments and value are user/default choices
        directory (dictionary): keys are folder names, values are their paths
        filename (str): file name

    Returns:
        None
    '''

    if args['plot']:  # plot OD and its GP estimate

        fig_path = assembleFullName(directory['figures'],'',filename,'fit','.pdf')
        plate.plot(fig_path,plot_fit=True,plot_derivative=False)

    if args['pd']:  # plot GP estimate of dOD/dt (i.e. derivative)

        fig_path = assembleFullName(directory['figures'],'',filename,'derivative','.pdf')
        plate.plot(fig_path,plot_fit=False,plot_derivative=True)


def prepGpData(plate):
    '''
    Packages different variants of grwoth curves for a specific plate into a single pandas.DataFrame.

    Args:
        plate (growth.GrwothPlate() object)

    Returns: 
        pandas.DataFrame (10 columns). See gp_data attribute in GrwothPlate().__init__() for more info.
    '''

    col_order = ['Plate_ID','Sample_ID','Time','OD_Data','OD_Fit']
    col_order += ['GP_Input','GP_Output','OD_Growth_Data','OD_Growth_Fit','GP_Derivative']

    pids = plate.key.drop_duplicates(subset='Sample_ID').set_index('Sample_ID')
    pids = pids.loc[:,['Plate_ID']]

    data = plate.time.join(plate.input_data)
    data = data.melt(id_vars='Time',var_name='Sample_ID',value_name='OD_Data')
    data = data.join(pids,on='Sample_ID')

    data = pd.merge(data,plate.gp_data,on=['Sample_ID','Time'])
    data = data.sort_values(['Sample_ID','Time'],ascending=[True,True])
    data = data.loc[:,col_order]

    return data


def savePlateData(store_data,plate,data_path,summ_path,diux_path):
    '''
    Saves the 'gp_data' and 'key' (attributes of 'plate' object) as tab-delimited files. 

    Args:
        store_data (boolean): whether to run part of code or not (save data from gp-model)
        plate (growth.GrwothPlate() object)
        data_path (str): file path for storing data file
        summ_path (str): file path for storing summary file
    '''

    #params = getValue('params_report')

    params = initParamList(0) + initParamList(1) + initParamList(2) 
    params = list(set(params).intersection(set(plate.key.keys())))
    diauxie = initDiauxieList()

    df_params = plate.key.drop(diauxie,axis=1).drop_duplicates().reset_index(drop=True)
    df_params = minimizeParameterReport(df_params)

    df_diauxie = plate.key[plate.key.diauxie==1]
    df_diauxie = df_diauxie.drop(params,axis=1)
    df_diauxie = df_diauxie.loc[:,~df_diauxie.columns.str.startswith('norm_')]
    df_diauxie = df_diauxie.reset_index(drop=True)
    df_diauxie = minimizeDiauxieReport(df_diauxie)

    df_params.to_csv(summ_path,sep='\t',header=True,index=False)
    if df_diauxie.shape[0]>0:
        df_diauxie.to_csv(diux_path,sep='\t',header=True,index=False)

    if not store_data:
        return None

    prepGpData(plate).to_csv(data_path,sep='\t',header=True,index=True)


def mergeSummaryData(args,directory,ls_temp_files,ls_summ_files,ls_diux_files,filename):
    '''
    Reads files passed via list and concatenates them into a single pandas.DataFrame. This 
        is executed for summary files and gp_data files separately. 

    Args:
        args (dictionary): keys are arguments and value are user/default choices
        directory (dictionary): keys are folder names, values are their paths
        ls_temp_files (list): where each item is a file path (str)
        ls_temp_files (list): where each item is a file path (str)
        filename (str): base file name  
    '''

    if args['sgd'] and args['merges']:

        file_path = assembleFullName(directory['derived'],'',filename,'gp_data','.txt')
        concatFileDfs(ls_temp_files).to_csv(file_path,sep='\t',header=True,index=True)

    if args['merges']:

        summ_df = concatFileDfs(ls_summ_files)
        diux_df = concatFileDfs(ls_diux_files)

        summ_path = assembleFullName(directory['summary'],'',filename,'summary','.txt')
        diux_path = assembleFullName(directory['summary'],'',filename,'diauxie','.txt')

        summ_df.to_csv(summ_path,sep='\t',header=True,index=True)
        if diux_df.shape[0]>0:
            diux_df.to_csv(diux_path,sep='\t',header=True,index=True)

        # clean-up
        for f in ls_temp_files + ls_summ_files + ls_diux_files:
            if os.path.isfile(f):
                os.remove(f)

