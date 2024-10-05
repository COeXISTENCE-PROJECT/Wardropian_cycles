# in this file we plot the results of the greedy algorithm

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# read the data
data = pd.read_csv('stats.csv')

# plot the mean and variance over time

plt.figure()
# plt.plot(data['Mean'], label='mean')
plt.plot(data['Variance'], label='variance')
plt.xlabel('days')
plt.ylabel('value')

plt.legend()
plt.show()
