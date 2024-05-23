import os
import json
import matplotlib.pyplot as plt

# Function to load data from a JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
fn = ""
# Function to extract memorymonitor data from loaded JSON
def extract_memory_monitor(json_data):
    return json_data.get('memoryMonitorH', [])
def plot_data_from_json_files(folder_path):
    json_files = [file for file in os.listdir(folder_path) if file.endswith('_output.json') and file.startswith(fn)]
    json_files = sorted(json_files)
    colors = ['violet', 'green', 'blue', 'pink', 'gray', 'yellow', 'red' ]
    labels = [r'$2^6$',r'$2^8$',r'$2^{10}$',r'$2^{12}$',r'$2^{14}$',r'$2^{16}$',r'$2^{17}$',]
 # List of colors for lines
    for i, json_file in enumerate(json_files):
        file_path = os.path.join(folder_path, json_file)
        data = load_json(file_path)
        memory_monitor = extract_memory_monitor(data)
        sizes = [point[0] for point in memory_monitor]
        indices = [point[1] for point in memory_monitor]
        plt.plot(indices, sizes, label= labels[i], color=colors[i])
    
    plt.xlabel('Input Size')
    plt.xscale('log' , base=2 )
    plt.ylabel('Memory')
    #plt.title('Memory Monitor Data')
    plt.legend()
    plt.grid(False)
    
    # Create a folder named "plots" if it doesn't exist
    plots_folder = os.path.join('..', 'plots')
    if not os.path.exists(plots_folder):
        os.makedirs(plots_folder)
    
    # Save the plot as an image in the "plots" folder
    plt.savefig(os.path.join(plots_folder, 'memory_monitor_plot_' + fn[5] + '.png'))
    
    plt.show()

# Relative path to the output folder
folder_path = os.path.join('..', 'output')

for i in range( 1 , 10 ):
    fn = "test_" +  str(i)
    # Plot data from JSON files and save as an image
    plot_data_from_json_files(folder_path)