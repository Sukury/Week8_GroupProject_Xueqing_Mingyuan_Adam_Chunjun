import streamlit as st
import pandas as pd
import plotly.express as px

#open data
schoolData = pd.read_csv("data/schoolData.csv")
frpl=pd.read_csv("data/frpl.csv")

#mask out the unused data, only keep the raws which school_name contains total
mask = schoolData["school_name"].str.contains('Total')
schoolData=schoolData[mask]

#change the school_name by removing the 'total'
schoolData['school_name']=schoolData['school_name'].str.replace(" Total","")

#remove columns "X1","school_group","pi_pct","blank_col"
schoolData = schoolData.drop(columns=["school_group","grade","pi_pct","blank_col"])

#remove the row that school_name "Grand" because it has grand total
#mask = schoolData["school_name"]!="Grand"
mask = ~(schoolData["school_name"]=='Grand')
schoolData=schoolData[mask]

#remove the percentage data from the percentage column
def removePercentageSing(dataframe,column_name):
    dataframe[column_name]=dataframe[column_name].str.replace("%","")

removePercentageSing(schoolData,"na_pct")
removePercentageSing(schoolData,"aa_pct")
removePercentageSing(schoolData,"as_pct")
removePercentageSing(schoolData,"hi_pct")
removePercentageSing(schoolData,"wh_pct")

#clean Free Lunch data that school_name with no name,一般在有数据没有data的时候用来remove这一个row的data，sublet是让这里是在school_name这一列里的none data的row删掉，不加sublet那么所有没有data的row都会被删掉
frpl = frpl.dropna(subset=["school_name"])
#remove unused column
mask = frpl["school_name"].isin(["ELM K_08", "Mid Schl", "High Schl", "Alt HS", "Spec Ed Total", "Cont Alt Total", "Hospital Sites Total", "Dist Total"])
frpl = frpl[mask]
#remove percentage in free lunch data
removePercentageSing(frpl,"frpl_pct")

# Check unique values in schoolData and frpl for the school_name column
#st.write("Unique school names in schoolData:", schoolData["school_name"].unique())
#st.write("Unique school names in frpl:", frpl["school_name"].unique())

# Check datatypes
#st.write("Data type of school_name in schoolData:", schoolData['school_name'].dtype)
#st.write("Data type of school_name in frpl:", frpl['school_name'].dtype)

#join two datasets
joined_dataset = schoolData.merge(frpl, on=["school_name"], how="left")

#create interface
st.set_page_config(layout="wide")
st.title("School Data about Race and Poverty:")
st.sidebar.title("Filters")

#select the visualization
vis=st.sidebar.radio("Select a visualization",
                     options=["Race/Ethnicity Chart",
                              "Poverty Charts",
                              "Relation Between Race and Poverty"])
#select the size of the school
size=st.sidebar.slider("Select the size of schools:",
                       min_value=joined_dataset["tot"].min(),
                       max_value=joined_dataset["tot"].max(),
                       value=[joined_dataset["tot"].min(),joined_dataset["tot"].max()])
#filter the data according to the size of the school
mask=(joined_dataset["tot"]>=size[0])&(joined_dataset["tot"]<=size[1])
joined_dataset=joined_dataset[mask]

#create a multiselecter for the names of the schools
schools=st.sidebar.multiselect("Select the schools that you want to include:",
                       options=joined_dataset["school_name"].unique(),
                       default=joined_dataset["school_name"].unique())
#filter only the schools that are selected
mask=joined_dataset["school_name"].isin(schools)
joined_dataset=joined_dataset[mask]

#conver the free lunch percentage to number
joined_dataset["frpl_pct"]=pd.to_numeric(joined_dataset["frpl_pct"])

#mark all schools with frpl bigger than 75% as high poverty
joined_dataset["high_poverty"]=joined_dataset["frpl_pct"]>75

#convert from a wide dataset to a long dataset
long_dataset=joined_dataset.melt(
    id_vars=["school_name","high_poverty"],
    value_vars=["na_num","aa_num","hi_num","wh_num"],
    var_name="race_ethnicity",
    value_name="population"
)
long_dataset["race_ethnicity"]=long_dataset["race_ethnicity"].replace({
    "na_num":"Native American",
    "aa_num":"African American",
    "as_num":"Asian American",
    "hi_num":"Hispanic",
    "wh_num":"White"
})

if vis=="Race/Ethnicity Chart":
    col1,col2=st.columns(2)
    with col1:
        fig=px.pie(long_dataset,values="population",names="race_ethnicity",
               title="Percentage of Races in the School District")
        st.plotly_chart(fig)
    with col2:
        fig=px.histogram(long_dataset,x="race_ethnicity",y="population",
                     title="Total Number of Students per race")
        st.plotly_chart(fig)
elif vis=="Poverty Charts":
    col1,col2=st.columns(2)
    with col1:
        fig=px.pie(long_dataset,values="population",names="high_poverty",
                   title="Percentage of Students in High Poverty Schools")
        st.plotly_chart(fig)
    with col2:
        fig=px.histogram(long_dataset,x="high_poverty",y="population",
                         title="Total Number Students in High Poverty schools")
        st.plotly_chart(fig)
elif vis=="Relation Between Race and Poverty":
    fig=px.pie(long_dataset,values="population",names="race_ethnicity",
               facet_col="high_poverty",title="Percentage of Races in Schools according to Poverty")
    st.plotly_chart(fig)


st.dataframe(joined_dataset)
st.dataframe(long_dataset)



#st.subheader("School Data:")
#st.dataframe(schoolData)
#st.subheader("Free Lunch:")
#st.dataframe(frpl)

