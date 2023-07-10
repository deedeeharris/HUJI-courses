import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import requests

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

# Function to load the main DataFrame
def load_data():
    df_main = pd.read_excel('df_with_grades.xlsx')
    return df_main

# Function to filter the DataFrame based on search criteria
def filter_data(df, filters):
    filtered_df = df.copy()
    for key, value in filters.items():
        if value is not None:
            filtered_df = filtered_df[filtered_df[key] == value]
    return filtered_df

# Function to plot course-related visualizations
def plot_course_visualizations(df):
    # Plot relevant visualizations based on the DataFrame
    # Example:
    # Plot a bar chart of course scores
    scores = df["official_course_score"]
    plt.hist(scores, bins=10)
    plt.xlabel("Course Score")
    plt.ylabel("Frequency")
    plt.title("Distribution of Course Scores")
    st.pyplot()

# Function to plot teacher-related visualizations
def plot_teacher_visualizations(df):
    # Plot relevant visualizations based on the DataFrame
    # Example:
    # Plot a bar chart of teacher scores
    scores = df["official_teacher_score"]
    plt.hist(scores, bins=10)
    plt.xlabel("Teacher Score")
    plt.ylabel("Frequency")
    plt.title("Distribution of Teacher Scores")
    st.pyplot()


# Read the DataFrame and calculate attendance score
@st.cache_data
def read_main_df():
    df_main = pd.read_excel('df_with_grades.xlsx')
    # Drop duplicate rows based on teacher, course number, group type, and year
    df_main = df_main.drop_duplicates(subset=['name', 'course_number', 'year'])

    # Assign scores for each attendance level
    attendance_scores = {
        'attendance5': 100,
        'attendance4': 80,
        'attendance3': 60,
        'attendance2': 40,
        'attendance1': 0
    }

    # Calculate the total attendance score
    df_main['attendance_score'] = (
            df_main['attendance5'] * attendance_scores['attendance5'] +
            df_main['attendance4'] * attendance_scores['attendance4'] +
            df_main['attendance3'] * attendance_scores['attendance3'] +
            df_main['attendance2'] * attendance_scores['attendance2'] +
            df_main['attendance1'] * attendance_scores['attendance1']
    ) / 100  # Divide by 100 to normalize the score to a range of 0-100

    return df_main


@st.cache_data
def load_grade_data():
    # replace this line with your actual data loader
    df = pd.read_excel("grades.xlsx")
    return df


# Function to search and display course details
def search_course(df, course_number):
    result = df[df['course_number'] == course_number]
    return result

def display_teacher_scores(result):
    result.loc[:, 'official_teacher_score'] *= 10  # Use .loc indexer to set values
    teacher_df = result[['name', 'official_teacher_score', 'teacher_score_in_chug']]

    st.markdown('### 👩‍🏫 Teachers and Scores:', unsafe_allow_html=True)
    
    # Group the data by teacher name and calculate the mean scores
    grouped_df = teacher_df.groupby('name').mean()
    
    for teacher_name, row in grouped_df.iterrows():
        official_score = row['official_teacher_score']
        chug_score = row['teacher_score_in_chug']
        
        st.markdown(f'##### &emsp;&emsp; {teacher_name}, Official Score: {official_score:.1f}, Score in Chug: {chug_score:.1f}', unsafe_allow_html=True)

# Main Streamlit app
def main():
    # Set page title and background color
    st.set_page_config(
        page_title='HUJI - Courses',
        page_icon=':mortar_board:',
        layout='wide',
        initial_sidebar_state='collapsed'
    )
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f5f7fa;
        }
        .result-container {
            background-color: rgba(144, 238, 144, 0.5);
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .title-text {
            font-weight: bold;
            display: inline-block;
            width: 200px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Read the DataFrames and calculate mean values
    df_main_mean = read_main_df()
    df_grades = load_grade_data()

    # Page title and subtitle
    st.title('Course Details and Grades at the Faculty of Agriculture (HUJI)')
    st.markdown('### Yedidya Harris, Bnaya Hami @ 71253, HUJI')
    st.subheader('Search by Course Number')
    st.markdown('###### (Data updated as of 2022)')


    # Course number search input
    # Use st.columns to create two columns
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        course_number = st.text_input('Enter a course number:', 71449)
        search_button = st.button('Search')
    with col2: pass

    # Perform search and display results
    if search_button:
        if course_number:
            result = search_course(df_main_mean, int(course_number))

            # Plot grades figure
            course_df = df_grades[df_grades['course_number'] == int(course_number)]
            if len(course_df) == 0:
                st.warning(f"No grade data available for the course number {course_number}")
            else:
                course_df = course_df.drop(["course_number", "Grade Average"], axis=1).melt()
                course_df.columns = ["Year", "Grade"]
                course_df['Year'] = pd.to_numeric(course_df['Year'])

                # Drop the columns that don't have any values
                empty_cols = course_df.columns[course_df.isna().all()].tolist()
                course_df = course_df.drop(empty_cols, axis=1)

                if 'Grade' in course_df:
                    course_df.dropna(subset=['Grade'], inplace=True)

                    average_grade = course_df['Grade'].mean()
                    avg_grade = f"Average: {average_grade:.2f}"

                    fig, ax = plt.subplots(figsize=(4, 2))
                    ax.bar(course_df['Year'], course_df['Grade'])
                    ax.set_title(f"Course {course_number} Yearly Grades Distribution\n{avg_grade}")
                    ax.set_xlabel('Year')
                    ax.set_ylabel('Grade')

                    # Save the figure as an image
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                    buffer.seek(0)

                    # Display the saved image with a smaller size
                    st.image(buffer, output_format='PNG', width=400)

                    plt.close()  # Close the figure to release resources
                else:
                    st.warning(f"No grade data available for the course number {course_number}")
                            

            if not result.empty:
                st.success(f'Course details found.\n\nClick [here](https://shnaton.huji.ac.il/index.php/NewSyl/{course_number}) for updated course syllabus.')

                teachers = ', '.join(result['name'].values)
                with st.container():

                    st.markdown('<div class="result-container">', unsafe_allow_html=True)
                    st.markdown(f'### :1234: Course Number: {result["course_number"].values[0]}', unsafe_allow_html=True)
                    st.markdown(f'### :mortar_board: Chug Number: {result["chug_number"].values[0]}, {result["chug_name"].values[0]}', unsafe_allow_html=True)
                    st.markdown(f'### :date: Year: {result["year"].values[0]}', unsafe_allow_html=True)
                    st.markdown(f'### :calendar: Semester: {result["semester"].values[0]}', unsafe_allow_html=True)
                    #st.markdown(f'### :busts_in_silhouette: Group Type: {result["group_type"].values[0]}', unsafe_allow_html=True)

                    st.markdown(f'### ⭐️ Official Course Score: {10 * result["official_course_score"].values.mean():.1f}', unsafe_allow_html=True)
                    st.markdown(f'### :1234: Course Score in Chug: {result["course_score_in_chug"].values.mean():.1f}', unsafe_allow_html=True)

                    #st.markdown(f'### 👩‍🏫 Teachers: {teachers}', unsafe_allow_html=True)
                    #st.markdown(f'### :100: Official Teacher Score: {10 * result["official_teacher_score"].values[0]:.1f}', unsafe_allow_html=True)
                    #st.markdown(f'### :100: Teacher Score in Chug: {result["teacher_score_in_chug"].values[0]:.1f}', unsafe_allow_html=True)

                    display_teacher_scores(result)

                    st.markdown(f'### :mortar_board: Degree: {result["Degree"].values[0]}', unsafe_allow_html=True)
                    st.markdown(f'### :heavy_check_mark: Mandatory: {result["Mandatory"].values[0]}', unsafe_allow_html=True)
                    st.markdown(f'### :family: Course Size: {result["Course_Size"].values[0]}', unsafe_allow_html=True)
                    st.markdown(f'### :bar_chart: Attendance Score: {result["attendance_score"].values[0]}', unsafe_allow_html=True)
                    st.markdown(f'### :chart_with_upwards_trend: Grade: {average_grade:.1f}', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)



            else:
                st.warning(f'Detailed info missing for the given course number ({course_number}).\n\nTry [here](https://shnaton.huji.ac.il/index.php/NewSyl/{course_number}) for updated course syllabus.')
        else:
            st.warning('Please enter a course number.')


if __name__ == '__main__':
    main()
