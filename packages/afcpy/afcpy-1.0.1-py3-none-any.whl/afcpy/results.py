import pandas as pd
from afcpy.analysis import Dataset

def output_animal_results(dst, test_h0=False, include_oe=True):
    """
    analyzes all datasets and writes the results to a csv file
    
    keywords
    --------
    dst : str
        the filepath/name for the csv file
    test_h0 : bool (default is False)
        flag for performing the boostrap hypothesis testing
    include_oe : bool (default is True)
        flag for including out-early trial-types
    """
    
    combos = (['VGlut2-cre','ChR2','blue'],
              ['VGlut2-cre','none','blue'],
              ['Gad2-cre','ChR2','blue'],
              ['Gad2-cre','Arch','green'],
              ['Gad2-cre','none','blue'],
              ['Gad2-cre','none','green'],
              ['wildtype','none','none'],
              )
    
    columns = ('filename',
               'bias_curve_fit',
               'bias_beta_coef',
               'boot_result_p',
               'mwu_result_left_u',
               'mwu_result_left_p',
               'mwu_result_right_u',
               'mwu_result_right_p',
               'med_rxn_time_manip_off_left',
               'med_rxn_time_manip_on_left',
               'med_rxn_time_manip_off_right',
               'med_rxn_time_manip_on_right',
               )
    
    df = pd.DataFrame(dict(),columns=columns)
    
    for combo in combos:
        
        # init the dataset
        ds = Dataset()
        ds.load(*combo,include_oe=include_oe)
        
        # perform bootstrap hypothesis testing
        if test_h0:
            ds.test(n_iters=5000)
        else:
            ds.p_values = np.full(len(ds.fileset),np.nan)
        
        # if analyzing the muscimol experiment extract the triplet of filenames
        if combo == ('wildtype','none','none'):
            basenames = []
            for trip in ds.fileset:
                trip_basenames = [os.path.basename(f) for f in trip]
                basenames.append(trip_basenames)
        else:
            basenames = [os.path.basename(f) for f in ds.fileset]
            
        df_data = (basenames,
                   ds.b1,
                   ds.b2,
                   ds.p_values,
                   ds.rt_effect_left_u,
                   ds.rt_effect_left_p,
                   ds.rt_effect_right_u,
                   ds.rt_effect_right_p,
                   ds.rt_iv_0_left,
                   ds.rt_iv_1_left,
                   ds.rt_iv_0_right,
                   ds.rt_iv_1_right
                   )
        df_temp = pd.DataFrame(np.array(df_data).T, columns=columns)
        df = df.append(df_temp)
    
    df.to_csv(dst)