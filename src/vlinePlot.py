import os
import json
import matplotlib.pyplot as plt

# Function to load data from a JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
name = ""
# Function to extract memorymonitor data from loaded JSON
def extract_memory_monitor(json_data):
    return json_data.get('memoryMonitorH', [])
def plot_data_from_json_files(folder_path):
    json_files = [file for file in os.listdir(folder_path) if file.endswith('_output.json') and file.startswith('test_'+name)]
    json_files = sorted(json_files)
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # List of colors for lines
    file_path = os.path.join(folder_path, json_files[0])
    data = load_json(file_path)
    memory_monitor = extract_memory_monitor(data)
    y_values = [point[0] for point in memory_monitor]
    #indices = [point[1] for point in memory_monitor]
    #plt.plot(indices, sizes, label=f'{json_file[:8]}', color=colors[i])
    vertical_x = []
    vertical_y = []

    # Iterate through y values to detect changes
    plt.plot([0, 0], [0 , 0] , color='tomato' , label='increase' )
    plt.plot([0, 0], [0 , 0] , color='lime' , label='decrease' )
    for i in range(1, len(y_values)):
        if y_values[i] > y_values[i-1]:
            # If y increased, draw a red vertical line
            plt.plot([i, i], [y_values[i-1], y_values[i]], color='tomato'  )
        elif y_values[i] < y_values[i-1]:
            # If y decreased, draw a green vertical line
            plt.plot([i, i], [y_values[i-1], y_values[i]], color='lime' )
        # Store x and y values for the vertical lines
        vertical_x.append(i)
        vertical_y.append(y_values[i])

    # Plot the original y values
    #plt.plot(y_values, marker='o', linestyle='-')

    # Plot the vertical lines
    #plt.plot(vertical_x, vertical_y, marker='o', linestyle='None', markersize=6, color='black')

    # Set labels and title\
    plt.xlabel('Input Size')
    plt.ylabel('Memory')
    plt.axhline(y=50, color='cornflowerblue', linestyle='--', label='α')
    plt.axhline(y=100, color='fuchsia', linestyle='--', label='β')
    #plt.title('Y Values with Vertical Lines for Changes')
    plt.legend(loc='upper left')
    # Show plot
    # plt.show()
    # plt.xlabel('Input Size')
    # #plt.xscale('log')
    # plt.ylabel('Memory')
    # #plt.title('Memory Monitor Data')
    # plt.legend()
    # plt.grid(True)
    
    # Create a folder named "plots" if it doesn't exist
    plots_folder = os.path.join('..', 'plots2')
    if not os.path.exists(plots_folder):
        os.makedirs(plots_folder)
    
    # Save the plot as an image in the "plots" folder
    plt.savefig(os.path.join(plots_folder, 'v_line_memory_monitor_'+ name + '.png'))
    
    plt.show()

# Relative path to the output folder
folder_path = os.path.join('..', 'output')

# Plot data from JSON files and save as an image
name = "7_5"
plot_data_from_json_files(folder_path)