#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
sns.set(rc={'figure.figsize':(15,12)}, font_scale=2)


##  tour_cap_nat.tsv
df = pd.read_csv("data/tour_cap_nat.tsv", sep="\t")
df.columns = [e.strip() for e in df.columns.to_list()] # remove spaces from column names
new = df.loc[:,"accommod,unit,nace_r2,geo\\time"].str.split(',', n = 4, expand = True) # split merged column into 4 separate

df['accommod'] = new[0] # assign splitted columns to new columns in df
df['unit'] = new[1]
df['nace_r2'] = new[2]
df['geo_time'] = new[3]

df.drop(columns=["accommod,unit,nace_r2,geo\\time"], inplace=True) # remove merged column
df = df[["accommod", "unit", "nace_r2", "geo_time", "2016"]] # select required columns

idx_of_u = df[df['2016'].str.contains('u')].index # find the location index of rows where 2016 values contain u.
idx_of_bu = df[df['2016'].str.contains(' bu')].index # find the location index of rows where 2016 values contain bu.
idx_of_b = df[df['2016'].str.contains(' b')].index #  find the location index of rows where 2016 values contain b.

df.loc[idx_of_u, '2016'] = np.nan # replace u unreliable values with missing NaN
df.loc[idx_of_bu, '2016'] = np.nan # replace bu values with missing NaN
df.loc[idx_of_b, '2016'] = df.loc[idx_of_b, '2016'].str.replace(' b', '') # keep the value but remove suffix b

df = df.replace(': ', np.nan) # replace missing : with NaN

df["2016"] = df[["2016"]].apply(lambda x: x.str.strip() ) # remove extra spaces from values
df["2016"] = df[["2016"]].astype('float64') # make numeric column

df = df[(df.accommod == 'BEDPL') & (df.unit=='NR') & (df.nace_r2 == "I551")] # filtering according required conditions
df = df[~df.geo_time.isin( ["EA", 'EU27_2007', 'EU27_2020', 'EU28'])] # filter out EU organizations

df=df.dropna().drop_duplicates() # remove missing rows and drop any duplicates

## tin00083.tsv dataset
df2 = pd.read_csv("data/tin00083.tsv", sep="\t")



df2.columns = [e.strip() for e in df2.columns.to_list()] # remove extra spaces from column names
new = df2.loc[:,"indic_is,ind_type,unit,geo\\time"].str.split(',', n = 4, expand = True) # separate merged column into seprate columns

df2['indic_is'] = new[0] # assign new seprated column 
df2['ind_type'] = new[1]
df2['unit'] = new[2]
df2['geo_time'] = new[3]

df2.drop(columns=["indic_is,ind_type,unit,geo\\time"], inplace=True) # drop merged column
df2 = df2[['indic_is','ind_type','unit','geo_time', "2016"]] # selected required columns

idx_of_bu = df2[df2['2016'].str.contains('bu')].index # get index of rows with suffix bu
idx_of_u = df2[df2['2016'].str.contains('u')].index # get index of rows with suffix u
idx_of_b = df2[df2['2016'].str.contains('b')].index # # get index of rows with suffix b

df2.loc[idx_of_bu, '2016'] = np.nan # replace values with bu suffix on missing NaN
df2.loc[idx_of_u, '2016'] = np.nan # replace values with u suffix on missing NaN
df2.loc[idx_of_b, '2016'] = df2.loc[idx_of_b, '2016'].str.replace(' b', '') # keep values but remove suffix b

df2 = df2.replace(': ', np.nan) # replace missing values
df2 = df2.replace(':', np.nan)
df2["2016"] = df2[["2016"]].apply(lambda x: x.str.strip() ) # remove spaces

df2['2016']= df2['2016'].astype('float64') # make column numeric
df2 = df2[df2.ind_type=='IND_TOTAL'] # select by required filter

df2 = df2[~df2.geo_time.isin( ["EA", 'EU27_2007', 'EU27_2020', 'EU28'])] # filter out EU organizations

df2 = df2.dropna().drop_duplicates() # drop missing values and duplicates

df.rename(columns={'2016':'Number of Bed-places'}, inplace=True)
df2.rename(columns={'2016':'Percentage of individuals online'}, inplace=True)


## merge df tour_cap_nat dataset and df2 tin00083 dataset based on geo_time from df dataset.
merged_df = df[['geo_time', 'Number of Bed-places']].merge(df2[['geo_time', 'Percentage of individuals online']], on='geo_time')
merged_df.dropna(inplace=True)



"""
In order to find the best country for the business. We should calculate and maximize the potential profits.
If country has largest population and smallest user online then due to small user base it will not be possible to get high revenue.
If there is large online user base but country has small population then it is also cannot be high profit to extracted.

The best case is to have high population and also high online users percentage.

Assume, the Number of Bed-Places value is the maximum number available of places. 
Percentage of individuals online is the Market Share.

Suppose ideally all beds are allocated by customers in 1 day in 1 country. And all customers are required to pay 1 dollar for wifi lamp usage.
The amount customers who will use the beds will be close to the percentage of individuals online Expected Value.

The maximum possible profit can be calculated = Number of Bed-places * (Individual online/100) * 1 dollar

After calulcation we can see that UK yields a highest maximum possible profit in 1 day if all beds were allocated and the proportion of lamp usage was equal to online users.

"""

merged_df['Expected_profit'] = merged_df['Number of Bed-places'] * ( merged_df['Percentage of individuals online']/100.0)

# display a rank table
print(merged_df.sort_values('Expected_profit', ascending=False).reset_index(drop=True).head(11))
merged_df.sort_values('Expected_profit', ascending=False).reset_index(drop=True).head(11).to_csv('output/country ranking.csv')


# visualize
sns.set_context( font_scale=1.5)
ax = sns.scatterplot(x="Number of Bed-places", y="Percentage of individuals online", hue="Expected_profit",
                     data=merged_df)
ax.text(1950480, 81, 'UK')
ax.set_title("The Number of Bed-places vs Percentage of individuals online and its expected profit value")
ax.get_figure().savefig("output/scatter plot.png") # export visualization


# export merged result
merged_df[['Percentage of individuals online', 'Number of Bed-places']] = merged_df[['Percentage of individuals online', 'Number of Bed-places']].astype('int')
merged_df[['geo_time', 'Percentage of individuals online', 'Number of Bed-places' ]].rename(columns={'geo_time':'Country Code'}).to_csv('output/merged_csv.csv', index=False)






