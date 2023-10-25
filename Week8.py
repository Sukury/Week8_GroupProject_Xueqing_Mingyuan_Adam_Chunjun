import streamlit as st
import pandas as pd
import plotly.express as px

#open data
Course_Section_info = pd.read_csv("data/Course section info.csv")
student_courseInfo=pd.read_csv("data/Student - course section info.csv")
student_careerInfo=pd.read_csv("data/Student career info.csv")
student_info=pd.read_csv("data/Student info.csv")
student_termInfo=pd.read_csv("data/Student term info.csv")