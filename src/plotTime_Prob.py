import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import os

def plto_tvprob( file_name ):
    with open( os.path.join('..', 'output' , file_name ), 'r') as json_file:
        data = json.load(json_file)

    # Extract keys (probabilities) and values from the data dictionary
    probabilities = [float(key) * 100 for key in data.keys()]
    values = [value * 1000 for value in data.values()]  # Divide values by 1000

    # Set up the interpolation
    x_new = np.linspace(min(probabilities), max(probabilities), 300)  # New x-values for interpolation
    spl = make_interp_spline(probabilities, values, k=3)  # Cubic spline interpolation

    # Compute the smoothed values
    y_smooth = spl(x_new)

    # Plotting the smoothed data
    plt.plot(x_new, y_smooth, color='blue')

    # Adding labels and title
    plt.xlabel('Drop Percentage')
    plt.ylabel('Time in milliseconds (ms)')
    #plt.title('Smoothed Plot of Values vs Probabilities')

    # Turn off the grid
    plt.grid(False)

    # Save the plot as an image file
    plt.savefig(os.path.join( '..' , 'plots' , 'timProb_' + file_name[:-4] + '.png'))

plto_tvprob('mem_restest_9_6.json')
