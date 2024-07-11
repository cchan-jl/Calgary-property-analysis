# Names: Carrie Chan and Paolo Geronimo
# Group Number: 8
# A terminal-based application for calculating and printing Calgary residential property assessment data.
# Data covers 3 communities in Calgary: Forest Lawn, New Brighton, and Hillhurst. 
# Data covers the years 2018 - 2022. 
# Program requires selection of one year and one community. 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import locale

def comm_stats(comm_yr_data, comm_name, input_year):
    """Calculates the statistics for the user selected year and community.

    This function uses aggregation computation, masking operations, 
    and grouby operations to print the statistics of the user selected subset of data.
    The calculations performed find the following values: number of houses, number and percent of houses below $300,000, 
    maximum, minimum, and median assessment values,
    maximum, minimum, and median percent growth, 
    maximum and minimum construction years that appear the most frequent, and
    the top 10 most expensive properties for this community. 

    Args:
        comm_yr_data: subset dataframe that only contains data for one year and one community, created according to user input
        comm_name: user selected community
        input_year: user selected year

    Returns:
        None
    """
    print("\n*** Statistics for", comm_name, "in", input_year, "***")

    house_count = len(comm_yr_data.loc[pd.IndexSlice[:, 'ROLL_NUMBER']].unique())  # counts the total number of properties and ensures each property is only counted once
    print("\nThe total number of houses in the selected year and community is: ", house_count)
    under_300 = len(comm_yr_data[comm_yr_data['ASSESSED_VALUE'] < 300000].loc[pd.IndexSlice[:, 'ROLL_NUMBER']].unique())  # use mask to filter for all assessments values under $300k and count the number of houses
    percent_under_300 = (under_300 / house_count) * 100
    print("The number and % of houses under $300,000 is: {0} and {1:.2f}%".format(under_300, percent_under_300))  # displays percentage with two decimal places

    locale.setlocale(locale.LC_ALL,'en_CA.UTF-8')  # formats values to Canadian currency
    max_value = locale.currency(comm_yr_data.loc[pd.IndexSlice[:, 'ASSESSED_VALUE']].max(), grouping = True)  # finds max value in ASSESSED_VALUE column of subset dataframe
    min_value = locale.currency(comm_yr_data.loc[pd.IndexSlice[:, 'ASSESSED_VALUE']].min(), grouping = True)  # finds min value in ASSESSED_VALUE column of subset dataframe
    print("The maximum property value for this year is {0} and the minimum is {1}.".format(max_value, min_value))

    # Replaces numbers that are too large and too small with NaN, uses mask operation to filter out NaN, then locates % growth column in subset dataframe
    growth_data = comm_yr_data.replace([np.inf, -np.inf], np.nan)[comm_yr_data.notnull()].loc[pd.IndexSlice[:, '% growth']]
    print("\nFrom years 2018 to 2022, % growth was calculated as % change of a property's assessment value from its previous year.")
    print("The statistics for % growth for the selected year and community are as follows:")

    if input_year == 2018:
        print("The % growth for 2018 was 0% since this was the base year in the data.")
    else:  # prints % growth stats to 2 decimal places if user input for year is not 2018
        print("Maximum: {0:.2f}%    Minimum: {1:.2f}%    Median: {2:.2f}%".format(growth_data.max(), growth_data.min(), growth_data.median()))

    # Find years that appear most frequent in YEAR_OF_CONSTRUCTION
    # By using grouby and count methods, counts the number of occurances that a unique year of construction appears
    freq_construction_yr = comm_yr_data.groupby("YEAR_OF_CONSTRUCTION").count()
    if freq_construction_yr.empty:  # some selected data subset have no reported years of construction 
        print("There were no reported property construction years.")
    else:
        pop_construction_yr = freq_construction_yr[freq_construction_yr['ROLL_NUMBER'] == freq_construction_yr['ROLL_NUMBER'].max()]  # mask operation to filer out and find the year that appears the most frequent
        print("The most frequent reported property year of construction is: ", *pop_construction_yr.index.astype(int))  # gets the YEAR_OF_CONSTRUCTION index and casts the year to display as an integer

    # Prints top 10 most expensive properties from subset data
    # Sorts the dataframe by ASSESSED_VALUE in descending order
    print("\n*** The Top 10 Most Expensive Properties for", comm_name, "in", input_year, "***")
    top_ten = comm_yr_data.sort_values(['ASSESSED_VALUE'], ascending = [False]).loc[pd.IndexSlice[: , ['ASSESSED_VALUE', 'ADDRESS', 'YEAR_OF_CONSTRUCTION', '$/SM'] ]]  # locates the other chosen columns to display
    top_ten = top_ten.head(10).replace(np.nan, "No reported value")  # gets the first ten rows and replaces any values that are NaN with a string
    top_ten.index = list(range(1, 11))  # sets the index to start from 1 to represent the order of the most expensive properties
    print(top_ten)

def dollar_per_land_size(full_data):
    """Creates three new columns in full dataframe that contains the assessed dollars per land size for each property.

    This function creates columns $/SM, $/SF, and $/AC using the ASSESSMENT_VALUE column and the three land size columns in the full dataframe.

    Args:
        full_data: full dataframe that contains all five years and all three communities

    Returns:
        None
    """
    full_data["$/SM"] = full_data["ASSESSED_VALUE"] / full_data["LAND_SIZE_SM"]
    full_data["$/SF"] = full_data["ASSESSED_VALUE"] / full_data["LAND_SIZE_SF"]
    full_data["$/AC"] = full_data["ASSESSED_VALUE"] / full_data["LAND_SIZE_AC"]

def main():

    # Read in excel files
    year_of_construction_data = pd.read_excel(r".\year_of_construction_data.xlsx")
    land_data = pd.read_excel(r".\land_data.xlsx")
    assessment_data = pd.read_excel(r".\assessment_data.xlsx")

    # Two merge operations done to merge all three excel files
    # Merge first two excel files along common columns ROLL_YEAR and ROLL_NUMBER
    # Merge last excel file along common columns ROLL_YEAR and ADDRESS to create a single dataframe, then drop all duplicate rows
    merged_data = pd.merge(year_of_construction_data, land_data, how = 'inner', on = ['ROLL_YEAR', 'ROLL_NUMBER'])
    full_data = pd.merge(merged_data, assessment_data, how = 'inner', on = ['ROLL_YEAR', 'ADDRESS']).drop_duplicates(keep = 'first')

    # Dataframe is sorted by ROLL_NUMBER and ROLL_YEAR so that %change can be calculated for each property's assessment values in each consecutive years starting from 2018
    # Data is sorted so that the years would be listed in ascending order from 2018 to 2022 for each house
    # Groups all the houses and calculates % change of the values reported in the ASSESSED_VALUE column to compute the change between the current year and previous year
    full_data.sort_values(['ROLL_NUMBER', 'ROLL_YEAR'], inplace = True)
    full_data["% growth"] = full_data.groupby("ROLL_NUMBER")["ASSESSED_VALUE"].pct_change() * 100  # Adds new column '% growth' to dataframe

    # Create hierarchical multiindex from ROLL_YEAR, COMM_CODE and COMM_NAME
    full_data.index = pd.MultiIndex.from_frame(full_data[['ROLL_YEAR', 'COMM_CODE', 'COMM_NAME']])
    full_data = full_data.sort_index().drop(columns = ['ROLL_YEAR', 'COMM_CODE', 'COMM_NAME']).replace(0, np.nan)  # sort, drop columns that were made into indices, and replace any reported values of zero

    pd.options.display.float_format = '{:.2f}'.format  # sets all floats to display with two decimal places

    dollar_per_land_size(full_data)  # adds 3 dollar per land size columns to dataframe

    print("\n*** Property Analysis for Three Communities in Calgary ***\n")
    # First stage of user input: selecting year
    while True:
        try:
            input_year = int(input("Please enter a year from 2018 up to and including 2022: "))
            if input_year in full_data.index.get_level_values("ROLL_YEAR"):  # checks if input is in year index
                break
            else:
                raise KeyError  # KeyError raised when input is not in index
        except (KeyError, ValueError):  # Value error raised when user inputs a letter, since input is cast to int
            print("Please enter a valid year.\n")
    
    # Second stage of user input: selecting community
    while True:    
        try:
            print("\nThe three communities with their corresponding codes are: Forest Lawn = FLN, New Brighton = NEB, Hillhurst = HIL")
            input_comm = input("Please enter a community name or code: ").strip().upper()  # remove leading/trailing whitespace, and set to uppercase to match indexes
            if input_comm in full_data.index.get_level_values("COMM_CODE"):  # if user enters community code
                comm_yr_data = full_data.loc[input_year, input_comm, :]  # create dataframe based on both user inputs
                comm_name = comm_yr_data.index[0]  # community name found in index of new dataframe
                break
            elif input_comm in full_data.index.get_level_values("COMM_NAME"):  # if user enters community name
                comm_yr_data = full_data.loc[input_year, :, input_comm]  # create dataframe based on both user inputs
                comm_name = input_comm
                break
            else:
                raise KeyError
        except KeyError:
                print("Please enter a valid community code or name.\n")

    comm_stats(comm_yr_data, comm_name, input_year)  # prints out statistics of the user selected year and community

    print("\n*** Statistics for All Three Communities ***\n")

    # Replace numbers too large and too small with NaN, apply mask to full data to filter out NaN
    # Print aggregate stats for entire dataset
    print(full_data.replace([np.inf, -np.inf], np.nan)[full_data.notnull()].describe())
    
    # Pivot table creation
    print("\n*** Pivot Table for Median House Assessment Value ***\n")
    median_pivot_table = full_data.pivot_table(index = "ROLL_YEAR", columns = "COMM_NAME", values = "ASSESSED_VALUE", aggfunc = 'median')
    print(median_pivot_table)
    
    full_data.to_excel("merged_data_export.xlsx")  # full dataset export
    
    # Setting up data to be plotted
    plot_data = full_data[full_data.notnull()].reset_index()  # mask out null values
    # Get mean of $/SM for each community in each year
    plot_data = plot_data.groupby(["ROLL_YEAR", "COMM_NAME"])["$/SM"].mean().reset_index()  # reset index to make year and community name column values
    print("\n*** Yearly Average $/Square Meter for Each Community ***\n")
    print(plot_data.to_string(index = False))  # print values to be plotted

    # Plot configuration
    fig, ax = plt.subplots()
    # for loop creates the plot for each community 
    for community, data in plot_data.groupby("COMM_NAME"):
        ax.plot(data["ROLL_YEAR"], data["$/SM"], label = community)  # year on x axis, $/SM on y axis

    # Making plot more presentable 
    plt.title("Yearly Average $/Square Meter")
    # By default, intermediate values (2018.5, 2019.5, etc) are displayed on x axis, 
    # so tick marks (axis units) are set manually
    xticks = [2018, 2019, 2020, 2021, 2022]  # locations of axis units
    xlabels = [2018, 2019, 2020, 2021, 2022]  # labels for each axis unit
    plt.xticks(ticks = xticks, labels = xlabels)
    plt.xlabel("Year")
    plt.ylabel("Avgerage $/Square Meter")
    ax.legend()  # show legend on plot
    plt.show()
    fig.savefig("yearly_averages_plot.png")  # export plot as PNG


if __name__ == '__main__':
    main()