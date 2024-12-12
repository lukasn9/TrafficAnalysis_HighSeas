import glob
import json
import re
import os


def save_lines(lines, krizovatka, configname):
    with open(f'Data/assets/intersections/{krizovatka}/lines/{configname}.json', 'w') as file:
        json.dump(lines, file)

def get_lines(krizovatka, configname):
    with open(f'Data/assets/intersections/{krizovatka}/lines/{configname}', 'r') as file:
        data = json.load(file)
    return data
def get_line_configs(krizovatka):
    folder_path = f'Data/assets/intersections/{krizovatka}/lines/'
    try:
        file_names = os.listdir(folder_path)  # Lists all files and folders in the directory
        return file_names
    except FileNotFoundError:
        print(f"The folder {folder_path} does not exist.")
        return []

async def save_history(output_path, data_path, krizovatka, video_name, start_time, end_time, analysis_start_time):
    path = f"Data/assets/history.json"

    with open(path, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print("Failed to load data")
            return False

    new_data = {"krizovatka": krizovatka, "video_name": video_name, "data_path": data_path, "start_time": start_time.isoformat(), "end_time": end_time.isoformat(), "analysis_start_time": analysis_start_time.isoformat()}
    data[output_path] = new_data

    with open(path, 'w') as file:
        json.dump(data, file, indent=4)
    return True


def get_history():
    path = f"Data/assets/history.json"

    with open(path, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print("Failed to load data")

    return data

async def save_data_analysis(new_data, path, intersection,source, start_time, end_time, analysis_start_time):
    # Step 1: Read the existing JSON data


    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

    try:

        with open(path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {'intersection': intersection, 'source': source, 'start_time': start_time.isoformat(), 'end_time': end_time.isoformat(), 'analysis_start_time': analysis_start_time.isoformat(), 'logs':[]}  # In case the JSON file is empty or invalid
    except FileNotFoundError:
        # If the file does not exist, initialize with default data
        data = {'intersection': intersection, 'source': source, 'start_time': start_time.isoformat(), 'end_time': end_time.isoformat(), 'analysis_start_time': analysis_start_time.isoformat(), 'logs': []}

    # Step 2: Update the data
    data['logs'].extend(new_data)
    data['end_time'] = end_time.isoformat()
    # Step 3: Write the updated data back to the JSON file
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)  # indent for pretty printing


def get_data(path):
    with open(path, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print("Failed to load data")
    intersections = dict()
    for log in data.get('logs', []):
        from_key = log['from']
        to_key = log['to']

        # Initialize 'from' key if not already in intersections
        if from_key not in intersections:
            intersections[from_key] = {'from': 0, 'to': 0}
        intersections[from_key]['from'] += 1

        # Initialize 'to' key if not already in intersections
        if to_key not in intersections:
            intersections[to_key] = {'from': 0, 'to': 0}
        intersections[to_key]['to'] += 1

    return intersections

def get_logs(path):
    with open(path, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print("Failed to load data")
            return []

    if 'logs' not in data or not isinstance(data['logs'], list):
        print("'logs' key is missing or invalid in the JSON file.")
        return []

    return data['logs']