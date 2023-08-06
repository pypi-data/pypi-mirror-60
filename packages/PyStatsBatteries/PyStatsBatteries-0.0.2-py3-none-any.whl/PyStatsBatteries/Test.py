from PyStatsBatteries.Descriptors import *
from PyStatsBatteries.Management import *
import pandas as pd
import matplotlib.pyplot as plt

X = pd.read_csv('/home/marc/Bureau/Capacity_Analysis/Mehdi/Tableau_Moyenne.csv', sep=',')

d = Descriptors()
m = Management()
# d.Scatterplot(X, "tsol","Void")

d.Scatterplot(X, 'CC/solid', "AM")

