import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

#open data
Course_Section_info = pd.read_csv("data/Course section info.csv")
student_courseSectionInfo=pd.read_csv("data/Student - course section info.csv")
student_careerInfo=pd.read_csv("data/Student career info.csv")
student_info=pd.read_csv("data/Student info.csv")
student_termInfo=pd.read_csv("data/Student term info.csv")

#create interface
st.set_page_config(layout="wide")
st.sidebar.title("Filters")

#select the visualization
vis=st.sidebar.radio("Select Your Question:",
                     options=["Question 1",
                              "Question 2",
                              "Question 3"])

if vis=="Question 1":
    #Create interface for Q1
    st.title("Question 1: The Most Popular Course")
    #join two datasets
    joinedDataset = student_courseSectionInfo.merge(Course_Section_info, on=["Term code","Course section number"], how="left")
    joinedDataset=joinedDataset.dropna(subset="Course title")
    #st.dataframe(joinedDataset)
    #group by
    aggregatedDataset = joinedDataset.groupby(["Course title","Term_x"]).aggregate({"Fake ID":"count"}).reset_index()
    #rename column
    aggregatedDataset=aggregatedDataset.rename(columns={"Fake ID":"Student number","Term_x":"Year and Term"})
    #sort by the student number
    aggregatedDataset=aggregatedDataset.sort_values("Student number",ascending=False).drop_duplicates("Year and Term").sort_values("Year and Term").reset_index(drop=True)
    # Add a selectbox to the sidebar for year selection
    selected_year = st.sidebar.multiselect(
        'Select the Year and Term',
        options=aggregatedDataset['Year and Term'].unique(),
    )
    # Filter the DataFrame based on the selected year and term
    filtered_df = aggregatedDataset[aggregatedDataset['Year and Term'].isin(selected_year)]
    #st.dataframe(aggregatedDataset)
    fig=px.bar(filtered_df,x="Year and Term",y="Student number",text="Course title",hover_name="Student number")
    #fig2=px.bar(aggregatedDataset,x="Course title",y="Student number")
    #fig3=px.bar(aggregatedDataset,x="Year and Term",y="Course title")
    st.plotly_chart(fig)
    if selected_year:
        st.markdown("***The most popular courses for the selected Year and Terms are:***")
        for year_term in selected_year:
            # Filter again for each selected year and term
            year_term_df = filtered_df[filtered_df['Year and Term'] == year_term]
            # Check if there are any courses for the year and term
            if not year_term_df.empty:
                # Find the most popular course for the year and term
                most_popular_course = year_term_df.loc[year_term_df['Student number'].idxmax()]
                st.write(
                    f"In {most_popular_course['Year and Term']}, the most popular course is {most_popular_course['Course title']} with {most_popular_course['Student number']} students.")
            else:
                st.write(f"No data for {year_term}.")
    else:
        st.write("Please select at least one Year and Term to display the most popular courses.")
    #st.plotly_chart(fig2)
elif vis=="Question 2":
    st.title("Question 2: The Percentage % of Different Type of Students in Different Program")