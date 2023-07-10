import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import requests
# Set page title and background color
st.set_page_config(
page_title='HUJI - Courses',
page_icon=':mortar_board:',
layout='wide',
initial_sidebar_state='collapsed'
)

@st.cache_data
def download_file_from_drive(file_id, destination_path):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)

    if response.status_code == 200:
        with open(destination_path, "wb") as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Failed to download file.")

# download files
file_id = st.secrets["main_df"]
destination_path = "df_with_grades.xlsx"
download_file_from_drive(file_id, destination_path)

# download files
file_id = st.secrets["grades_df"]
destination_path = "grades.xlsx"
download_file_from_drive(file_id, destination_path)


# download files
file_id = st.secrets["grades_df"]
destination_path = "grades.xlsx"
download_file_from_drive(file_id, destination_path)

# download files
file_id = st.secrets["main_py"]
destination_path = "courses_app.py"
download_file_from_drive(file_id, destination_path)

import sys
import os

file_directory = "/app/huji-courses"  # Replace with the actual directory containing courses_app.py
file_name = "courses_app.py"

# Add the file directory to the Python path
sys.path.append(file_directory)

# Check if the file exists
file_path = os.path.join(file_directory, file_name)
if os.path.exists(file_path):
    st.write("File exists.")
    # Import and run the function from the file
    #from courses_app import main_app
    #main_app()
else:
    print("File does not exist.")
