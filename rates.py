import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import openpyxl
import os

# ------------ALL OF THE FOLLOWING IS TESTING CODE FOR SINGLE CASES---------------------

# import json file for US coordinate data
import json
from urllib.request import urlopen

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# import all libraries and create dictionary for all excel files
file_directory = r"\venv\Cancer"
all_files = {}

# separate all files into one list
for file in os.listdir(file_directory):
    if file.endswith(".xlsx"):
        df = pd.read_excel(os.path.join(file_directory, file))
        all_files[file] = df

def scatter(file_name, rate_or_count):
    df_names = []
    df_values_cancer = []
    df_values_infant_count = []
    df_values_infant_rate = []

    if file_name[-7:-5] == "FL":
        for row in range(4, 69):
            df_names.append(all_files[file_name]["County"][row])
            df_values_cancer.append(all_files[file_name][rate_or_count][row])

            df_values_infant_count.append(all_files["InfantDeath_FL.xlsx"]["Count"][row])
            df_values_infant_rate.append(all_files["InfantDeath_FL.xlsx"]["Rate"][row])

            if df_values_cancer[-1] == "* " or df_values_cancer[-1] == "3 or fewer":
                df_names.pop()
                df_values_cancer.pop()
                df_values_infant_count.pop()
                df_values_infant_rate.pop()

    df_values_cancer = np.array(df_values_cancer)
    df_values_infant_count = np.array(df_values_infant_count)
    df_values_infant_rate = np.array(df_values_infant_rate)

    if rate_or_count == "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000":
        plt.plot(df_values_infant_rate, df_values_cancer, "b.")
        m, b = np.polyfit(df_values_infant_rate, df_values_cancer, 1)
        plt.plot(df_values_infant_rate, m * df_values_infant_rate + b, "r")
        plt.xlabel("Infant Mortality (Aged 0-364 Days), Rate Per 1,000 Live Births")
        plt.ylabel(f"{rate_or_count} for {file_name[:-8]}")
        plt.title(f"{file_name[:-8]} Rate vs Infant Mortality Rate")
        plt.show()
    elif rate_or_count == "Average Annual Count":
        plt.plot(df_values_infant_count, df_values_cancer, "b.")
        m, b = np.polyfit(df_values_infant_count, df_values_cancer, 1)
        plt.plot(df_values_infant_count, m * df_values_infant_count + b, "r")
        plt.xlabel("Infant Mortality (Aged 0-364 Days) Count")
        plt.ylabel(f"{rate_or_count} for {file_name[:-8]}")
        plt.title(f"{file_name[:-8]} Count vs Infant Mortality Count")
        plt.show()

# create a function to create maps for universal cases
def mapping(file_name, rate_or_count):
    df_names = []
    df_values = []
    df_fips = []
    df_code = []

    if file_name[-7:-5] == "FL":
        for row in range(4, 69):
            df_names.append(all_files[file_name]["County"][row])
            df_values.append(all_files[file_name][rate_or_count][row])
            df_fips.append(all_files[file_name][" FIPS"][row])

            if df_values[-1] == "* " or df_values[-1] == "3 or fewer":
                df_names.pop()
                df_values.pop()
                df_fips.pop()
        title = rate_or_count + " for " + file_name[:-8] + " for Counties in Florida"

    if file_name[-7:-5] == "NC":
        for row in range(3, 3144):
            df_names.append(all_files[file_name]["County"][row])
            df_values.append(all_files[file_name][rate_or_count][row])
            df_fips.append(all_files[file_name][" FIPS"][row])

            if type(df_values[-1]) == str:
                df_names.pop()
                df_values.pop()
                df_fips.pop()
        title = rate_or_count + " for " + file_name[:-8] +  " for Counties in the US"

    if "National" in file_name:
        for row in range(4, 53):
            df_names.append(all_files[file_name]["State"][row])
            df_values.append(all_files[file_name][rate_or_count][row])
            df_code.append(all_files[file_name]["Code"][row])

            if df_values[-1] == "data not available ":
                df_names.pop()
                df_values.pop()
                df_code.pop()
        title = rate_or_count + " for " + file_name[:-14] +  " for States in the US"

    df_values = np.array(df_values)
    max_range = max(df_values)
    min_range = min(df_values)

    if file_name[-7:-5] == "FL" or file_name[-7:-5] == "NC":
        # print choropleth map of US, specifically florida for bladder data
        fig = px.choropleth(all_files[file_name], geojson = counties, locations = df_fips, color = df_values,
                        color_continuous_scale="Viridis",
                        scope="usa",
                        labels={'unemp': 'Incidence Rate'}
                        )
        fig.update_layout(
            title_text = title,
            geo_scope='usa',  # limit map scope to USA
        )
        fig.show()
    elif "National" in file_name:

        fig = go.Figure(data=go.Choropleth(
            locations= df_code,  # Spatial coordinates
            z= df_values,  # Data to be color-coded
            locationmode='USA-states',  # set of locations match entries in `locations`
            colorscale='Reds',
            colorbar_title=  rate_or_count,
        ))

        fig.update_layout(
            title_text= title,
            geo_scope='usa',  # limite map scope to USA
        )

        fig.show()

def graphing(file_name, rate_or_count):
    df_names = []
    df_values = []
    df_fips = []

    if file_name[-7:-5] == "FL":
        for row in range(2, 69):
            df_names.append(all_files[file_name]["County"][row])
            df_values.append(all_files[file_name][rate_or_count][row])
            df_fips.append(all_files[file_name][" FIPS"][row])

            if df_values[-1] == "* " or df_values[-1] == "3 or fewer":
                df_names.pop()
                df_values.pop()
                df_fips.pop()

        title = rate_or_count + " for " + file_name[:-8] + " for Counties in Florida"

    if file_name[-7:-5] == "NC":
        for row in range(3, 3144):
            df_names.append(all_files[file_name]["County"][row])
            df_values.append(all_files[file_name][rate_or_count][row])
            df_fips.append(all_files[file_name][" FIPS"][row])

            if df_values[-1] == "* " or df_values[-1] == "data not available ":
                df_names.pop()
                df_values.pop()
                df_fips.pop()

        title = rate_or_count + " for " + file_name[:-8] +  " for Counties in the US"

    if "National" in file_name:
        for row in range(4, 53):
            df_names.append(all_files[file_name]["State"][row])
            df_values.append(all_files[file_name][rate_or_count][row])
            df_fips.append(all_files[file_name][" FIPS"][row])

            if df_values[-1] == "data not available" or df_values[-1] == "data not available ":
                df_names.pop()
                df_values.pop()
                df_fips.pop()

        title = rate_or_count + " for " + file_name[:-14] +  " for States in the US"

    df_values = np.array(df_values)
    max_range = max(df_values)
    min_range = min(df_values)

    # Create horizontal bars
    plt.barh(df_names, df_values)

    # Labels and title
    plt.xlabel(rate_or_count)
    plt.ylabel('Counties')


    plt.title(title)

    # Display the plot
    plt.show()

graphing("Kidney and Renal Pelvis Cancer_FL.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
#graphing("Colorectal Cancer_FL.xlsx", "Average Annual Count")

'''mapping("Colorectal Cancer_National.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Colorectal Cancer_National.xlsx", "Average Annual Count")

mapping("Colorectal Cancer_NC.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Colorectal Cancer_NC.xlsx", "Average Annual Count")

mapping("Kidney and Renal Pelvis Cancer_National.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Kidney and Renal Pelvis Cancer_National.xlsx", "Average Annual Count")

mapping("Kidney and Renal Pelvis Cancer_FL.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Kidney and Renal Pelvis Cancer_FL.xlsx", "Average Annual Count")

mapping("Kidney and Renal Pelvis Cancer_NC.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Kidney and Renal Pelvis Cancer_NC.xlsx", "Average Annual Count")

mapping("Ovarian Cancer_FL.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Ovarian Cancer_FL.xlsx", "Average Annual Count")

mapping("Ovarian Cancer_National.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Ovarian Cancer_National.xlsx", "Average Annual Count")

mapping("Ovarian Cancer_NC.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Ovarian Cancer_NC.xlsx", "Average Annual Count")

mapping("Thyroid Cancer_FL.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Thyroid Cancer_FL.xlsx", "Average Annual Count")

mapping("Thyroid Cancer_National.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Thyroid Cancer_National.xlsx", "Average Annual Count")

mapping("Thyroid Cancer_NC.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")
mapping("Thyroid Cancer_NC.xlsx", "Average Annual Count")

mapping("Colorectal Cancer_FL.xlsx", "Average Annual Count")
mapping("Colorectal Cancer_FL.xlsx", "Age-Adjusted Incidence Rate([rate note]) - cases per 100,000")'''