# app.py - Enhanced Hospital Management System with Visual Charts (Streamlit)
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(page_title="Hospital Management System", page_icon="🏥", layout="wide")

# Database initialization
DB_FILE = "hospital.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS Patients (
            pat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, age INTEGER, gender TEXT,
            phone TEXT, address TEXT, email TEXT, registration_date TEXT DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS Doctors (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, specialty TEXT, dept_id INTEGER,
            phone TEXT, email TEXT
        );
        CREATE TABLE IF NOT EXISTS Appointments (
            app_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER, doc_id INTEGER,
            app_date TEXT, app_time TEXT, status TEXT DEFAULT 'Scheduled'
        );
        CREATE TABLE IF NOT EXISTS MedicalRecords (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER, doc_id INTEGER,
            diagnosis TEXT, treatment TEXT, prescription TEXT, record_date TEXT DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS Billings (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER, amount REAL,
            details TEXT, payment_status TEXT DEFAULT 'Pending', bill_date TEXT DEFAULT (date('now'))
        );
    ''')
    conn.commit()
    conn.close()

init_db()

# Helpers
def get_data(table):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

def add_record(table, columns, values):
    conn = sqlite3.connect(DB_FILE)
    placeholders = ', '.join(['?' for _ in values])
    conn.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", values)
    conn.commit()
    conn.close()

# Sidebar
st.sidebar.title("🏥 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Patients", "Doctors", "Appointments", "Medical Records", "Billings"])

# ================ DASHBOARD WITH VISUAL CHARTS ================
if page == "Dashboard":
    st.title("📊 Hospital Dashboard")

    patients_df = get_data("Patients")
    doctors_df = get_data("Doctors")
    appointments_df = get_data("Appointments")
    billings_df = get_data("Billings")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients", len(patients_df))
    col2.metric("Total Doctors", len(doctors_df))
    col3.metric("Total Appointments", len(appointments_df))
    col4.metric("Total Bills", len(billings_df))

    st.markdown("### Patient Demographics")
    if not patients_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            gender_fig = px.pie(patients_df, names='gender', title="Gender Distribution")
            st.plotly_chart(gender_fig, use_container_width=True)
        with col2:
            age_fig = px.histogram(patients_df, x='age', nbins=20, title="Age Distribution")
            st.plotly_chart(age_fig, use_container_width=True)

    st.markdown("### Appointments Overview")
    if not appointments_df.empty:
        appointments_df['app_date'] = pd.to_datetime(appointments_df['app_date'])
        daily_apps = appointments_df.groupby('app_date').size().reset_index(name='count')
        line_fig = px.line(daily_apps, x='app_date', y='count', title="Daily Appointments")
        st.plotly_chart(line_fig, use_container_width=True)

    st.markdown("### Billing Summary")
    if not billings_df.empty:
        status_fig = px.pie(billings_df, names='payment_status', title="Payment Status")
        st.plotly_chart(status_fig, use_container_width=True)
        amount_fig = px.bar(billings_df, x='pat_id', y='amount', title="Billing Amounts by Patient")
        st.plotly_chart(amount_fig, use_container_width=True)

# ================ OTHER PAGES (same as before, with minor improvements) ================
elif page == "Patients":
    st.header("👥 Patient Management")
    # (Keep the previous Patients code with data_editor and add form)

    # Example chart in Patients tab
    patients_df = get_data("Patients")
    if not patients_df.empty:
        st.markdown("### Patient Age Distribution")
        age_hist = px.histogram(patients_df, x='age', title="Patient Ages")
        st.plotly_chart(age_hist, use_container_width=True)

    # ... rest of Patients code from previous version

# Add similar charts to other tabs if desired (e.g., Doctor specialties pie chart in Doctors tab)

# Keep the rest of the code for Patients, Doctors, Appointments, Medical Records, Billings as in the previous version

st.sidebar.info("Enhanced with visual charts using Plotly!")
