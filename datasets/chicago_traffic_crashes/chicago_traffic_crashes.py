#%% md
# # Cleaning Messy Chicago Traffic Crashes Dataset
# Dataset from https://catalog.data.gov/dataset/traffic-crashes-crashes
#%%
import pandas as pd
import importlib

import lib

importlib.reload(lib)

log = lib.logger.getLogger(__name__)
#%% md
# # Read dataset
#%%
filename = 'chicago_traffic_crashes.csv'
df = lib.tools.read_data(filename, sep=',', encoding='ascii')
#%% md
# ## Getting the general info to see what we're working with
#%%
log.info(f'General Info {df.info()}')
log.info(f'General Info {df.shape}')
#%% md
# ### Checking for null indices and rows
#%%
null_indices, null_rows, null_columns = lib.tools.null_info(df)
#%% md
# ## No rows or columns that are ALL null. Moving onto cleaning columns.
#%% md
# ## Creating a backup
#%%
df_cp1 = df.copy()
#%% md
# # Processing NaN Values
#%%
df_cp1.columns
#%% md
# ## Checking for NaN and Non-NaN columns
#%%
# Create a null and non_null columns list
non_null_columns = lib.tools.notnull(df_cp1).columns
null_columns = lib.tools.hasnull(df_cp1).columns

log.info(non_null_columns)
log.info(null_columns)
#%% md
# ## Checking for columns whose values are 75% or more NaN
#%%
# Get columns that mostly have NaN values. Will need to look at these closer.
high_risk = lib.tools.data_risks_rate(df_cp1, err_rate=.75)
#%% md
# Taking a look at the high risk columns
#%%
high_risk
#%% md
# ## Removing data that is not useable
#%%
df_cp1 = df_cp1.drop(high_risk.keys(), axis=1)
#%% md
# ## Filling the rest of the NaN values with filler values
#%%
df_cp1, filler_values = lib.tools.fillnull(df_cp1)
#%% md
# ## Creating a backup
#%%
df_cp2 = df_cp1.copy()
#%%
df_cp2.columns
#%% md
# # Checking and Validating data
#%%
df_cp2.loc[:, 'CRASH_DATE']
#%% md
# Unifying proper formatting for pd.Timestamp data type
#%%
df_cp2.loc[:, 'POSTED_SPEED_LIMIT']
#%% md
# Quick check of values
#%%
minimum = df_cp2.loc[:, 'POSTED_SPEED_LIMIT'].min()
maximum = df_cp2.loc[:, 'POSTED_SPEED_LIMIT'].max()
average = df_cp2.loc[:, 'POSTED_SPEED_LIMIT'].mean()
log.info(f'Min/Max/Avg POSTED_SPEED_LIMIT {minimum}/{maximum}/{average}')
#%% md
# Valid values, no need to clean this column
#%% md
# Checking for categories
#%%
df_cp2.loc[:, 'DEVICE_CONDITION'].unique()
#%%
df_cp2.loc[:, 'WEATHER_CONDITION'].unique()
#%% md
# To keep with current formatting, switching 'BLOWING SAND, SOIL, DIRT' to '/'
#%%
df_cp2.loc[:, 'WEATHER_CONDITION'] = df_cp2.loc[:, 'WEATHER_CONDITION'].str.replace(', ', '/')
df_cp2.loc[:, 'WEATHER_CONDITION'].unique()
#%%
df_cp2.loc[:, 'LIGHTING_CONDITION'].unique()
#%%
df_cp2.loc[:, 'FIRST_CRASH_TYPE'].unique()
#%%
df_cp2['TRAFFICWAY_TYPE'].unique()
#%%
df_cp2['ALIGNMENT'].unique()
#%%
df_cp2['ROADWAY_SURFACE_COND'].unique()
#%%
df_cp2['ROAD_DEFECT'].unique()
#%%
df_cp2.columns
#%%
df_cp2['REPORT_TYPE'].unique()
#%%
df_cp2['CRASH_TYPE'].unique()
#%%
df_cp2['HIT_AND_RUN_I'].unique()
#%%
df_cp2['DAMAGE'].unique()
#%%
df_cp2['DATE_POLICE_NOTIFIED'].unique()
#%%
df_cp2['PRIM_CONTRIBUTORY_CAUSE'].unique()
#%%
df_cp2['SEC_CONTRIBUTORY_CAUSE'].unique()
#%%
df_cp2['STREET_NO']
#%%
df_cp2['STREET_DIRECTION'].unique()
#%%
df_cp2['STREET_DIRECTION'].value_counts()['Not Available']
#%%
df_cp2['BEAT_OF_OCCURRENCE']
#%%
df_cp2['NUM_UNITS'].unique()
#%%
df_cp2['MOST_SEVERE_INJURY'].unique()
#%%
df_cp2['INJURIES_TOTAL'].unique()
#%%
df_cp2['INJURIES_FATAL'].unique()
#%%
df_cp2['INJURIES_INCAPACITATING'].unique()
#%%
sorted(df_cp2['INJURIES_NON_INCAPACITATING'].astype(int).unique())
#%%
sorted(df_cp2['INJURIES_REPORTED_NOT_EVIDENT'].astype(int).unique())
#%%
sorted(df_cp2['INJURIES_NO_INDICATION'].astype(int).unique())
#%%
sorted(df_cp2['INJURIES_UNKNOWN'].astype(int).unique())
#%%
df_cp2['CRASH_HOUR'].unique() > 24
#%%
df_cp2['CRASH_DAY_OF_WEEK'].unique() > 7
#%%
df_cp2['CRASH_MONTH'].unique() > 12
#%%
df_cp2['LATITUDE']
#%%
df_cp2['LONGITUDE']
#%%
df_cp2['LOCATION']
#%% md
# ## Creating lists to process
#%%
to_drop = [
    'CRASH_RECORD_ID',
    'STREET_NAME',
    'STREET_NO',
    'STREET_DIRECTION',
    'BEAT_OF_OCCURRENCE',
    'MOST_SEVERE_INJURY', # Repeated in other INJURY_* columns
    'CRASH_HOUR',  # repeated in CRASH_DATE
    'CRASH_DAY_OF_WEEK',  # repeated in CRASH_DATE
    'CRASH_MONTH',  # repeated in CRASH_DATE
    'NUM_UNITS', # Would need clarification what this means
    'LOCATION'
]

# Convert to Timestamp
to_datetime = [
    'CRASH_DATE',
    'DATE_POLICE_NOTIFIED',
]

to_consolidate = [
    'WEATHER_CONDITION',
    'TRAFFIC_CONTROL_DEVICE',
    'DEVICE_CONDITION',
    'FIRST_CRASH_TYPE', #?
    'ALIGNMENT,'
    'TRAFFICWAY_TYPE',
    'ROADWAY_SURFACE_COND',
    'ROAD_DEFECT',
    'PRIM_CONTRIBUTORY_CAUSE',
    'SEC_CONTRIBUTORY_CAUSE',
    'ROADWAY_SURFACE_COND'

]

to_bools_manual = [
    'REPORT_TYPE', # Change to ON_SCENE
    'CRASH_TYPE', # Change to REPORTABLE
    'HIT_AND_RUN_I'
]

to_ints_manual = [
    'DAMAGE'
]

to_ints = [
    'INJURIES_TOTAL',
    'INJURIES_FATAL',
    'INJURIES_INCAPACITATING',
    'INJURIES_NON_INCAPACITATING',
    'INJURIES_REPORTED_NOT_EVIDENT',
    'INJURIES_NO_INDICATION'
]

# No need to check these
valid = [
    'POSTED_SPEED_LIMIT',
    'LIGHTING_CONDITION',
    'LATITUDE',
    'LONGITUDE',
]

keys2 = to_consolidate + to_bools_manual + to_ints_manual + to_ints + to_datetime + to_drop + valid
diff = set(df_cp2.columns).difference(set(keys2))
log.debug(f'Diff {diff}: {df_cp2.shape[1]}/{len(keys2)}')
#%% md
# ## Creating a backup
#%%
df_cp3 = df_cp2.copy()
#%% md
# ## Dropping unneeded Columns
#%%
df_cp3 = df_cp3.drop(to_drop, axis=1)
#%% md
# # Begin Cleaning Process
# 
# ## Stripping whitespaces from DataFrame
#%%
df_cp3 = lib.tools.str_strip(df_cp3)
#%% md
# ## Converting Datetime columns
#%%
for column in to_datetime:
    df_cp3[column] = pd.to_datetime(df_cp3.loc[:, column], format='%m/%d/%Y %I:%M:%S %p')
#%%
df_cp3[to_datetime]
#%% md
# ## Converting Ints columns
#%%
df_cp3['DAMAGE']
#%%
# Converting to ints
df_cp3['DAMAGE'] = df_cp3['DAMAGE'].replace('$500 OR LESS', 0)
df_cp3['DAMAGE'] = df_cp3['DAMAGE'].replace('$501 - $1,500', 1)
df_cp3['DAMAGE'] = df_cp3['DAMAGE'].replace('OVER $1,500', 2)
df_cp3['DAMAGE'].astype(int)
#%%
for column in to_ints:
    df_cp3[column] = df_cp3[column].astype(int)
#%% md
# ## Converting Bools columns
# -1 for Not Available
# 0 for False
# 1 for True
#%% md
# Renaming 'REPORT_TYPE' to 'ON_SCENE'
#%%
df_cp3['REPORT_TYPE'].unique()
#%% md
# Change to ON_SCENE
#%%
df_cp3.loc[:, 'REPORT_TYPE'] = df_cp3['REPORT_TYPE'].replace(
    {
        'ON SCENE': 1,
        'NOT ON SCENE (DESK REPORT)': 0,
        'Not Available': -1,
     }
)
#%%
df_cp3 = df_cp3.rename({'REPORT_TYPE': 'ON_SCENE'}, axis=1)
df_cp3.loc[:, 'ON_SCENE']

#%%
df_cp3.columns
#%% md
# Renaming to REPORTABLE
#%%
df_cp3['CRASH_TYPE'].unique()
#%%
df_cp3.loc[:, 'CRASH_TYPE'] = df_cp3['CRASH_TYPE'].replace(
    {
        'NO INJURY / DRIVE AWAY': False,
        'INJURY AND / OR TOW DUE TO CRASH': True,
     }
)
#%%
df_cp3 = df_cp3.rename({'CRASH_TYPE': 'REPORTABLE'}, axis=1)
df_cp3.loc[:, 'REPORTABLE']
#%% md
# Renaming to HIT_AND_RUN
#%%
df_cp3['HIT_AND_RUN_I'].unique()
#%%
df_cp3.loc[:, 'HIT_AND_RUN_I'] = df_cp3['HIT_AND_RUN_I'].replace(
    {
        'Not Available': -1,
        'N': 0,
        'Y': 1,
     }
)
df_cp3 = df_cp3.rename({'HIT_AND_RUN_I': 'HIT_AND_RUN'}, axis=1)
df_cp3.loc[:, 'HIT_AND_RUN']
#%% md
# ## Creating a backup
#%%
df_cp4 = df_cp3.copy()
#%% md
# ## Converting Consolidate column
# A manual process
#%%
df_cp4['WEATHER_CONDITION'].unique()
#%%
df_cp4['TRAFFIC_CONTROL_DEVICE'].unique()
#%%
df_cp4['DEVICE_CONDITION'].unique()
#%%
df_cp4['DEVICE_CONDITION'] = df_cp4['DEVICE_CONDITION'].replace(
    {
        'FUNCTIONING PROPERLY': True,
        'UNKNOWN': False,
        'NO CONTROLS': False,
        'FUNCTIONING IMPROPERLY': False,
        'OTHER': False,
        'NOT FUNCTIONING': False,
        'WORN REFLECTIVE MATERIAL': False,
        'MISSING': False,
    }
)
df_cp4 = df_cp4.rename({'DEVICE_CONDITION': 'TRAFFIC_DEVICE_FUNCTIONING'}, axis=1)
df_cp4.loc[:, 'TRAFFIC_DEVICE_FUNCTIONING']
#%%
df_cp4['FIRST_CRASH_TYPE'].unique()
#%%
# collision, fixed, movement, nonmotorist
df_cp4['FIRST_CRASH_TYPE'] = df_cp4['FIRST_CRASH_TYPE'].replace(
    {
        'SIDESWIPE SAME DIRECTION': 'Collision',
        'SIDESWIPE OPPOSITE DIRECTION': 'Collision',
        'REAR END': 'Collision',
        'REAR TO SIDE': 'Collision',
        'HEAD ON': 'Collision',
        'REAR TO FRONT': 'Collision',
        'OTHER OBJECT': 'Collision',
        'REAR TO REAR': 'Collision',

        'PARKED MOTOR VEHICLE': 'Fixed',
        'FIXED OBJECT': 'Fixed',
        'TRAIN': 'Fixed',

        'TURNING': 'Movement',
        'ANGLE': 'Movement',
        'OVERTURNED': 'Movement',

        'PEDALCYCLIST': 'Non-motorist',
        'PEDESTRIAN': 'Non-motorist',
        'ANIMAL': 'Non-motorist',

        'OTHER NONCOLLISION': 'OTHER NONCOLLISION',
    }
)
df_cp4 = df_cp4.rename({'FIRST_CRASH_TYPE': 'CRASH_TYPE'}, axis=1)
df_cp4.loc[:, 'CRASH_TYPE']
#%%
df_cp4['TRAFFICWAY_TYPE'].unique()
#%%
df_cp4['ROADWAY_SURFACE_COND'].unique()
#%%
df_cp4['ROAD_DEFECT'].unique()
#%%
df_cp4['ROAD_DEFECT'] = df_cp3['ROAD_DEFECT']
#%%
df_cp4['ROAD_DEFECT'] = df_cp4['ROAD_DEFECT'].replace(
    {
        'NO DEFECTS': False,
        'UNKNOWN': True,
        'SHOULDER DEFECT': True,
        'WORN SURFACE': True,
        'RUT, HOLES': True,
        'OTHER': True,
        'DEBRIS ON ROADWAY': True
    }
)
#%%
df_cp4['PRIM_CONTRIBUTORY_CAUSE'].unique()
#%%
df_cp4['SEC_CONTRIBUTORY_CAUSE'].unique()
#%%
x = pd.Series(df_cp4['PRIM_CONTRIBUTORY_CAUSE'].unique() + df_cp4['SEC_CONTRIBUTORY_CAUSE'].unique())
x.unique()
#%% md
# ## Renaming a few more columns
#%%
df_cp4 = df_cp4.rename({'ALIGNMENT': 'ROAD_LEVEL', 'DAMAGE': 'DAMAGE_AMT'}, axis=1)
#%% md
# # Final Cleaned Dataset
#%%
df_clean_data = df_cp4.copy()
#%% md
# ## Reorder columns
#%%
reordered_columns = [
    'CRASH_DATE',
    'DATE_POLICE_NOTIFIED',

    'ON_SCENE',
    'HIT_AND_RUN',

    'POSTED_SPEED_LIMIT',

    'TRAFFIC_CONTROL_DEVICE',
    'TRAFFIC_DEVICE_FUNCTIONING',

    'WEATHER_CONDITION',
    'LIGHTING_CONDITION',
    'ROADWAY_SURFACE_COND',
    'ROAD_DEFECT',

    'TRAFFICWAY_TYPE',
    'ROAD_LEVEL',

    'DAMAGE_AMT',

    'CRASH_TYPE',

    'PRIM_CONTRIBUTORY_CAUSE',
    'SEC_CONTRIBUTORY_CAUSE',

    'REPORTABLE',
    'INJURIES_TOTAL',
    'INJURIES_FATAL',
    'INJURIES_INCAPACITATING',
    'INJURIES_NON_INCAPACITATING',
    'INJURIES_REPORTED_NOT_EVIDENT',
    'INJURIES_NO_INDICATION',
    'INJURIES_UNKNOWN',

    'LATITUDE',
    'LONGITUDE',
]
df_clean_data = df_clean_data[reordered_columns]
#%%
df_clean_data
#%% md
# ## Export to CSV
#%%
export_path = lib.path.get_cleaned_path(filename)
df_clean_data.to_csv(export_path)
#%%
