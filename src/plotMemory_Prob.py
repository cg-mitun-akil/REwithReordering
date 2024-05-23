import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import os

def plto( filename ):
    with open( os.path.join('..', 'output' , filename ), 'r') as json_file:
        data = json.load(json_file)

    # Extract keys (probabilities) and values from the data dictionary
    probabilities = [float(key) * 100 for key in data.keys()]
    values = list(data.values())
    # Set up the interpolation
    x_new = np.linspace(min(probabilities), max(probabilities), 300)  # New x-values for interpolation
    spl = make_interp_spline(probabilities, values, k=3) 

    y_smooth = spl(x_new)

    plt.plot(x_new, y_smooth, color='red')

    # Plotting the data as a smooth red line
    #plt.plot(probabilities, values, color='red')

    # Adding labels and title
    plt.xlabel('Drop Percentage')
    plt.ylabel('Memory')
    #plt.title('Plot of Values vs Probabilities (Probabilities multiplied by 100)')

    # Displaying the plot
    #plt.grid(True)
    plt.tight_layout()

    plt.savefig(os.path.join( '..' , 'plots' , 'memProb_' + filename[:-4] + '.png'))

plto('mem_restest_7_6.json')