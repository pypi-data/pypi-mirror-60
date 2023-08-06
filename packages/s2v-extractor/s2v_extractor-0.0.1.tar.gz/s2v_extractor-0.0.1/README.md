# s2v-extractor

#you get "abc234d4" from this 2344 as number

#memory and age are column of datafrme which has values like 16GB and you want 16 as number it will return dataframe withconverted values

import pandas as pd


from test import s2v

 

df=pd.read_csv('test_data.csv')


obj=s2v(df,["Memory","Age"])         
              
print(obj.extract())



