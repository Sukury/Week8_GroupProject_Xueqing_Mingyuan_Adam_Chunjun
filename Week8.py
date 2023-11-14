import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

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
    st.title("Question 1: What is the Most Popular Course?")
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
    st.title("Question 2: What is the Percentage % of Different Types of Students in Different Programs?")
    st.title("")
    #join data
    joinedDatasetQ2 = student_info.merge(student_careerInfo, on=["Fake ID"],how="left")
    joinedDatasetQ2 = joinedDatasetQ2.dropna(subset="Academic plan")
    #replace n/s data to "unknown"
    joinedDatasetQ2.fillna('Unknown', inplace=True)
    #rename the info in data
    replace_International_values = {
        'N': 'No',
        'Y': 'Yes',
    }
    replace_Marital_values = {
        'U': 'Unmarried',
        'E': 'Married',
        'S': 'Single',
        'M': 'Separated',
        'D': 'Divorced',
    }
    replace_Sex_values = {
        'M': 'Male',
        'F': 'Female',
        'U': 'Unknown'
    }
    joinedDatasetQ2['Legal sex'] = joinedDatasetQ2['Legal sex'].replace(replace_Sex_values)
    joinedDatasetQ2['Marital status'] = joinedDatasetQ2['Marital status'].replace(replace_Marital_values)
    joinedDatasetQ2['International student'] = joinedDatasetQ2['International student'].replace(replace_International_values)

    #Add a selectbox to the sidebar for Program selection
    selected_program = st.sidebar.selectbox(
        'Select the Program',
        options=joinedDatasetQ2['Academic plan'].unique(),
    )
    st.subheader(f'In the Program of {selected_program}:')
    # Filter the DataFrame based on the selected program
    filtered_df = joinedDatasetQ2[joinedDatasetQ2['Academic plan']==selected_program]
    # 在侧边栏添加一个多选框以选择要显示饼图的类别
    categories = ['Race', 'Legal sex', 'Marital status', 'International student']
    selected_categories = st.sidebar.multiselect(
        'Select Student Info Types',
        options=categories,
    )
    # Display the DataFrame
    #st.dataframe(filtered_df)
    # 创建列，每行两个饼图
    cols = st.columns(2)

    if not selected_categories:
        st.info("Please select at least one student type.")
    else:
        # 用户选择了至少一个类别，继续显示饼图
        for index, category in enumerate(selected_categories):
            pie_data = filtered_df[category].value_counts()
            fig, ax = plt.subplots(figsize=(8, 8))
            wedges, texts, autotexts = ax.pie(pie_data, autopct='%1.1f%%', startangle=90)
            # 角标绘制加标注
            ax.legend(wedges, pie_data.index, title=category, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            col_index = index % 2
            col = cols[col_index]
            with col:
                # 使用Markdown居中标题，并用HTML来调整字体大小
                st.markdown(
                    f"<h6 style='text-align: center; color: blue;'>Student type by {category} </h6>",
                    unsafe_allow_html=True)
                st.pyplot(fig)

else:
    st.title("Question 3: What is the Success of Different Types of Students?")
    st.title("")
    # join data
    joinedDatasetQ3 = student_info.merge(student_careerInfo, on=["Fake ID"], how="left")
    joinedDatasetQ3 = joinedDatasetQ3.dropna(subset="Academic plan")
    joinedDatasetQ3p2 = joinedDatasetQ3.merge(student_termInfo, on=["Fake ID", "Academic plan"], how="left")

    # group by
    visibleData = joinedDatasetQ3p2[["Academic plan", "Fake ID","Marital status","Legal sex","Academic load","Race","Degree awarded","Term code","Term","Completion term code"]]
    filtered_df = visibleData[visibleData['Term code'] == visibleData['Completion term code']]

    #replace na data
    filtered_df.fillna('Unknown', inplace=True)
    replace_data_values = {
        'AA': 'Complete',
        'AAS': 'Complete',
        'BS': 'Complete',
        'BA':'Complete',
        'Unknown':'Incomplete'
    }
    filtered_df['Degree awarded'] = filtered_df['Degree awarded'].replace(replace_data_values)

    replace_Marital_values = {
        'U': 'Unmarried',
        'E': 'Married',
        'S': 'Single',
        'M': 'Separated',
        'D': 'Divorced',
    }
    replace_Sex_values = {
        'M': 'Male',
        'F': 'Female',
        'U': 'Unknown'
    }
    filtered_df['Legal sex'] = filtered_df['Legal sex'].replace(replace_Sex_values)
    filtered_df['Marital status'] = filtered_df['Marital status'].replace(replace_Marital_values)

    #visualize filter
    selected_program = st.sidebar.selectbox(
        'Select the Program',
        options=filtered_df['Academic plan'].unique(),
    )
    filtered_df = filtered_df[filtered_df['Academic plan'] == selected_program]

    # 定义筛选器类别
    filter_categories = {
        'term': 'Term',
        'part_time_full_time': 'Academic load',
        'race': 'Race',
        'marital_status': 'Marital status',
        'legal_sex': 'Legal sex'
    }

    # 对每个筛选器类别创建复选框和多选框
    selected_filters = {}
    selected_tags = []
    for key, category in filter_categories.items():
        # 创建一个复选框来选择是否启用该筛选器
        if st.sidebar.checkbox(f'Filter by {category}', key=key):
            # 如果复选框被勾选，显示一个多选框来选择该筛选器的值
            options = filtered_df[category].unique()
            selected_options = st.sidebar.multiselect(
                f'Select {category}',
                options=options,
                # default=options 默认选中所有选项
            )
            selected_filters[category] = selected_options
            # 如果有选项被选中，则添加到选定的标签中
            if selected_options:
                selected_tags.append(f"{category}: {', '.join(selected_options)}")

    # 应用筛选器
    for category, selections in selected_filters.items():
        if selections:
            filtered_df = filtered_df[filtered_df[category].isin(selections)]

    # 在界面上显示选定的程序和筛选标签
    st.write(f"In the program of **{selected_program}**, the selected filters are:")
    if selected_tags:
        st.write(" - " + "\n - ".join(selected_tags))
    else:
        st.write("No filters selected.")

    # 绘制显示学业完成状态的饼图
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(filtered_df['Degree awarded'].value_counts(), labels=filtered_df['Degree awarded'].value_counts().index, autopct='%1.1f%%', startangle=90)
        ax.legend(title='Completion Status')
        st.pyplot(fig)
    else:
        st.write("There are no records matching the selected filters.")

    #st.dataframe(filtered_df)
