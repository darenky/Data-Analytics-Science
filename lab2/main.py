from datetime import datetime
import os
import pandas as pd
import requests

# Dictionary for changing region indexes used on website to NOAA indexes
NOAAIndex = {
        1:24,
        2:25,
        3:5,
        4:6,
        5:27,
        6:23,
        7:26,
        8:7,
        9:11,
        10:13,
        11:14,
        12:15,
        13:16,
        14:17,
        15:18,
        16:19,
        17:21,
        18:22,
        19:8,
        20:9,
        21:10,
        22:1,
        23:3,
        24:2,
        25:4, 
        26:12, # for Kyiv
        27:20 # for Sevastopol
}

save_dir = "files"  

# Create the directory if it doesn't exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Function to clear the directory
def clear_dir(save_dir):
    file_list = os.listdir(save_dir)
    for file_name in file_list:
        file_path = os.path.join(save_dir, file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error: {e}")

# Download data from website + data cleaning 
def download_data(region_index, save_dir):
    noaa_index = NOAAIndex[region_index]
    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?provinceID={noaa_index}&country=UKR&yearlyTag=Weekly&type=Mean&TagCropland=land&year1=1982&year2=2023"
    response = requests.get(url)

    if response.status_code == 200:  # Successful request 
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(save_dir, f"file_{formatted_datetime}.csv")

        with open(filename, 'wb') as file:
            content = response.text
            replacements = [("</pre></tt>", ""), ("<tt><pre>", ""), ("<br>", ""), (" VHI", "VHI"), (" SMN", "SMN"), ("weeklyfor", "weekly for")]
    
            for old, new in replacements:
                content = content.replace(old, new)

            content = content.replace(',\n', '\n')  # Remove trailing commas
            file.write(content.encode('utf-8'))

        print(f"{filename} has been downloaded and saved")
        return filename
    else:
        print("Failed to download the file")
        return None


desired_region_index = 1  # Desired region index

downloaded_filename = download_data(desired_region_index, save_dir)

headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI']
df = pd.read_csv(downloaded_filename, header=1, names=headers)
df = df[df['SMN'] != -1.0]  # Delete rows that contain "-1"

df.to_csv(downloaded_filename, index=False)  # Need it to save previous change in file itself 

def extremums_vhi(df, year: int):  # Find extremums for the specific year
    year_str = str(year)
    max_vhi = df.loc[df['Year'].astype(str) == year_str, 'VHI'].max()
    min_vhi = df.loc[df['Year'].astype(str) == year_str, 'VHI'].min()
    return max_vhi, min_vhi

print(extremums_vhi(df,1995))

def extreme_drought():  # Get info about extreme droughts for the entire time
  return  df[(df.VHI <= 15)]

print(extreme_drought())

def moderate_drought():  # Get info about moderate droughts for the entire time
  return  df[(df.VHI > 15)&(df.VHI <= 35)]

print(moderate_drought())

#clear_dir('files')