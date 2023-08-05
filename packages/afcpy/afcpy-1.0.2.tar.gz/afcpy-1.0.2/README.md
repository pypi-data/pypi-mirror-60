## Description

The purpose of this package is to make the analysis and results of the optogenetics experiments performed in the [Felsen laboratory](https://medschool.cuanschutz.edu/physiology/faculty/gidon-felsen-phd) publicly available in an effort to increase transparency and reproducibility. This package includes data collected from optogenetic manipulations of specific cell-types in the intermediate and deep layers of the mouse superior colliculus while it performs an odor-guided alternative forced choice (afc) task. It also includes data from a pharmacological experiment performed in which muscimol was locally infused into the left colliculi prior to task performance. The results of these experiments are in preparation for publication as of January 27nd, 2020. Please direct all correspondence to gidon.felsen@cuanschutz.edu.

## Installation

via pip ([pypi](https://pypi.org/project/afcpy/)):
```
pip install afcpy
```
or from source:

1.) clone the repository
```
git clone https://github.com/jbhunt/afcpy
```
2.) run the setup.py script
```
python -m setup.py install
```

## Reproducing the analyses

#### Standardizing the data
 
The `afcpy.analysis.Session` class standardizes the behavioral data. The `Session` object possesses the `data` attribute which references a `pandas.DataFrame` of the shape (number of trials x number of trial features) indexed by the trial number. Each trial is associated with a set of features. The most important trial features are: "x_odor_left" and "x_odor_right" (the stimulus intensity), "x_choice" (the animal's choice coded 0 = right and 1 = left), and "x_light" (optogenetic manipulation coded 0 = no light and 1 = light). The "x_other" column denotes whether the trial belonged to a session in which saline or muscimol was delivered for the muscimol experiment (0 = saline and 1 = muscimol, respectively).

``` python
>>> from afcpy.analysis import Session
>>> session_id = '<installation directory>/afcpy/data/<experimenter name>/<animal ID>/<filename>.mat'
>>> s = Session(session_id)
>>> s.data 
         x_frac_odor_left  x_frac_odor_right  x_odor_left  x_odor_right  ...  x_choice  x_light  x_other
x_trial
0                    0.60               0.40          0.2           0.0  ...        1        1        0
1                    0.40               0.60          0.0           0.2  ...        1        0        0
2                    0.60               0.40          0.2           0.0  ...        1        0        0
3                    0.60               0.40          0.2           0.0  ...        1        0        0
...                   ...                ...          ...           ...  ...      ...      ...      ...
```

You can find the session meta data in the `afcpy.analysis.Session.sesh_meta_data` attribute (a dictionary).

```python
>>> tb = '<installation directory>/afcpy/data/josh/glu1/tb_@M2L-old_Andrew_glu1_ipsi_500-5-120_0.1mW_473nm_190401a.mat' 
>>> s = Session(tb)
>>> for key,val in s.sesh_meta_data.items(): print(key,val)
home_dir <installation directory>/afcpy/data/josh/glu1
ftype tb
protocol @M2L-old
experimenter Andrew
animal_id glu1
side ipsi
stim_params 500-5-120
laser_intensity 0.1
laser_wavelength 473
date 190401
animal_n 1
animal_class glu
program @M2L
version old
stim_on_time 500
pulse_on_width 5
laser_frequency 8.0
```

#### Loading whole datasets

If you want to play around with predefined datasets you can use the `afcpy.analysis.Dataset` class. This object collects and analyzes a pre-defined set of files corresponding to a particular experiment. All you need to do is specify the experiment by passing the genotype, transgene, and laser color (i.e., wavelength) to the load method. The following example demonstrates how to load only files corresponding to the experiment in which GABAergic cells in the intermediate and deep layers of the SC were transfected with Channelrhodopsin and excited with 473nm light during the choice epoch of the behavioral task:

```python
>>> from afcpy.analysis import Dataset
>>> ds = Dataset()
>>> ds.load(genotype='Gad2-cre',transgene='ChR2',laser='blue')
```

For advanced usage you can pass keyword arguments which select for certain session parameters. In the example below, only sessions in which the laser intensity was within the range of 0-5 mW for animals 'glu2' and 'glu3' will be collected and analyzed.

```python
>>> ds.load(genotype='VGlut2-cre',transgene='ChR2',laser='blue',laser_int=(0,5),animal_ids=['glu2','glu3'])
```

The muscimol experiment is treated differently than the optogentics experiments. Each session is actually a combination of three sessions: pre-treatment with muscimol, treatment with muscimol, and post-treatment of muscimol (i.e., wash). This is how you load the muscimol dataset:
```python
>>> ds.load('wildtype','none','none')
```

#### Measuring the effect on choice

The primary measure of effect for the optogenetic or pharmacological manipulation is a directional weight estimated with logistic regression. Briefly, the regression analysis uses the stimulus intensity and the experimental manipulation as predictor variables with the animals' choice as the outcome variable. The method for estimating the weight of the experimental manipulation is adapted from [Thompson et al., Elife (2017)](https://elifesciences.org/articles/16572) (see the behavioral analysis methods section). The value of these weights usually falls within the range of -4 and 4 and indicate the direction and magnitude of the bias caused by the experimental manipulation: a negative value indicates a leftward (or ipsilateral) bias in the animal's choice; whereas a positive value indicates a rightward (or contralateral) bias. This value for each session in a dataset is stored in a numpy array that is referenced by the `Session.b2` attribute:

```python
>>> ds.b2
array([ 1.38919164, -0.22015101, -0.45137623, ..., 0.81841271, 0.34306193, 0.73924127])
```

#### Outputting the results to a csv file

If you just want to get the results of the experiments as a csv you can use the `afcpy.results.output_animal_results` function. This will generate a csv file which contains a sesssion-by-session report of the analyses performed. Note that if want to perform the boostrap hypothesis testing for each session you'll need to set the "test_h0" flag equal to True (see below). This will take a long time for the large datasets.

```python
>>> from afcpy.results import output_animal_results
>>> dst = '<file path and name of the csv file>.csv'
>>> output_animal_results(dst,test_h0=True)
```