import openpyxl
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import folium
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

# get basic spatial and temporal coverage of dataset
file = 'Nitrogen_FDEP.xlsx'
df = pd.read_excel(file)
df['COLLECTION_DATE'] = pd.to_datetime(df['COLLECTION_DATE']).dt.date

min_lat, max_lat = df['LATITUDE'].min(), df['LATITUDE'].max()
min_long, max_long = df['LONGITUDE'].min(), df['LONGITUDE'].max()
print(f"Spatial coverage: latitude from {min_lat} to {max_lat}, longitude from {min_long} to {max_long}")

# For temporal coverage
min_time, max_time = df['COLLECTION_DATE'].min(), df['COLLECTION_DATE'].max()
print(f"\nTemporal coverage: from {min_time} to {max_time}")

# Plotting the temporal distribution
df['COLLECTION_DATE'].hist(bins=30)
plt.title('Temporal distribution of data points')
plt.xlabel('Collection Date')
plt.ylabel('Frequency')
plt.show()

'''
# conduct density analysis for spatial data
sns.kdeplot(data=df, x="LONGITUDE", y="LATITUDE")
plt.title('Density of Spatial Data')
plt.show()'''

# conduct time series analysis to show overtime cumulative sum value per year
df.set_index('COLLECTION_DATE')['VALUE'].plot()
plt.title('Time series of Nitrate')
plt.xlabel('Collection Date')
plt.ylabel('Nitrate + Nitrite')
plt.show()

# create heatmap to show variation of value, dates, and counties
pivot_table = df.pivot_table(values='VALUE', index='COLLECTION_DATE', columns='COUNTY_NAME')
sns.heatmap(pivot_table)
plt.title('Heatmap of Nitrate Totals by County Over Time')
plt.show()

# -------------------------------------------------------------------------- longitudinal?

# Create a new column  that combines LATITUDE and LONGITUDE
df['LOCATION'] = list(zip(df.LATITUDE, df.LONGITUDE))

# Group by LOCATION and COLLECTION_DATE and count the number of occurrences
counts = df.groupby(['LOCATION', 'COLLECTION_DATE']).size()

# Group by PK_STATION and COLLECTION_DATE and count the number of occurrences
station_date_counts = df.groupby(['PK_STATION', 'COLLECTION_DATE']).size()

# If any station-date combination has more than one occurrence, the data is longitudinal
is_longitudinal_check1 = any(station_date_counts > 1)

# If any location-date combination has more than one occurrence, the data is longitudinal
is_longitudinal_check2 = any(counts > 1)
print(f"\nIs the data longitudinal? {'Yes' if (is_longitudinal_check1 and is_longitudinal_check2) else 'No'}")

# conclusion: data is longitudinal based on research checks. not sure if correct...

# --------------------------------------------------------------- determine if nitrate values are above EPA regulations
above_mcl_nitrate = df[df['VALUE'] > 10]
num_above_mcl_nitrate = len(above_mcl_nitrate)

print(f"\nNumber of observations above the MCL (nitrate): {num_above_mcl_nitrate}")
# now group for latitude, longitude, collection date, and county

violations_nitrate = []
for index, row in above_mcl_nitrate.iterrows():
    violation = [row['LATITUDE'], row['LONGITUDE'], row['COLLECTION_DATE'], row['COUNTY_NAME']]
    violations_nitrate.append(violation)
    print(f"Violation on {row['COLLECTION_DATE']} in {row['COUNTY_NAME']} county for nitrate")

# count how many violations in each county for nitrate
county_counts_nitrate = above_mcl_nitrate.groupby('COUNTY_NAME').size()
print("\nNumber of violations in each county (nitrate):")
print(county_counts_nitrate)

# plot for nitrate by county
plt.figure(figsize=(10, 6))
county_counts_nitrate.plot(kind='barh')
plt.ylabel('County Name')
plt.xlabel('Number of Violations')
plt.title('Number of Violations in Each County (Nitrate)')
plt.show()

# ------------------------------------------------------------------- group data violations by county and well types

# count how many violations in each county and well type for nitrate
county_well_type_counts_nitrate = above_mcl_nitrate.groupby(['COUNTY_NAME', 'WELL_TYPE']).size()
pd.set_option('display.max_rows', None)
print("\nNumber of violations in each county and well type (nitrate):")
print(f"{county_well_type_counts_nitrate}")

# visualize data above
# reset index to flatten the grouped data frame
flat_data = county_well_type_counts_nitrate.reset_index()

# rename the 0 column to 'COUNT'
flat_data = flat_data.rename(columns={0: 'COUNT'})

# create a bar plot
plt.figure(figsize=(10, 6))
sns.barplot(data=flat_data, x='COUNTY_NAME', y='COUNT', hue='WELL_TYPE')
plt.title('Number of Violations in Each County and Well Type (Nitrate)')
plt.xlabel('County Name')
plt.ylabel('Number of Violations')
plt.xticks(rotation=90)
plt.show()

# ------------------------------------------------------------------- group data violations by water management district

# Group data violations by WATER_MANAGEMENT_DISTRICT
grouped_violations = above_mcl_nitrate.groupby('WATER_MANGEMENT_DISTRICT').size()

# Print the grouped data
print(f"\n{grouped_violations}")

# Create a horizontal bar plot
plt.figure(figsize=(10, 6))
grouped_violations.plot(kind='barh')
plt.title('Number of Violations in Each Water Management District (Nitrate)')
plt.ylabel('Water Management District')
plt.yticks(fontsize=8)
plt.xlabel('Number of Violations')
plt.show()

# ---------------------------------------------------------------------------- Plot by County and Year for Violations

# Convert 'COLLECTION_DATE' to datetime
above_mcl_nitrate['COLLECTION_DATE'] = pd.to_datetime(above_mcl_nitrate['COLLECTION_DATE'])

# Create a new column for the year
above_mcl_nitrate['YEAR'] = above_mcl_nitrate['COLLECTION_DATE'].dt.year

# Create a count plot with 'YEAR' on the x-axis and 'COUNTY_NAME' on the y-axis
plt.figure(figsize=(10, 6))
sns.countplot(data=above_mcl_nitrate, x='YEAR', hue='COUNTY_NAME')

plt.title('Number of Violations in Each County Over Time (Nitrate)')
plt.xlabel('Year')
plt.ylabel('Number of Violations')
plt.show()

# ----------------------------------------------------- plot violation trends for well and land elevation

well_elevation = 'WELL_MEASURING_PT_ELEVATION'
land_elevation = 'LAND_SURFACE_ELEVATION'

# Group by well elevation and count the number of violations
grouped_violations_well = above_mcl_nitrate.groupby(well_elevation).size().reset_index(name='COUNT')

# Group by land elevation and count the number of violations
grouped_violations_land = above_mcl_nitrate.groupby(land_elevation).size().reset_index(name='COUNT')

# Create a scatter plot for well elevation vs. violations
plt.figure(figsize=(10, 6))
plt.scatter(grouped_violations_well[well_elevation], grouped_violations_well['COUNT'])
plt.axvline(x=60, color='r', linestyle='--')
plt.axvline(x=100, color='r', linestyle='--')
plt.xlabel('Well Elevation')
plt.ylabel('Number of Violations')
plt.title('Number of Violations in Relation to Well Elevation')
plt.show()

# Create a scatter plot for land elevation vs. violations
plt.figure(figsize=(10, 6))
plt.scatter(grouped_violations_land[land_elevation], grouped_violations_land['COUNT'])
plt.axvline(x=60, color='r', linestyle='--')
plt.axvline(x=100, color='r', linestyle='--')
plt.xlabel('Land Elevation')
plt.ylabel('Number of Violations')
plt.title('Number of Violations in Relation to Land Elevation')
plt.show()
