# app.py - Hospital Management System with Streamlit (No Charts)
import streamlit as st
import sqlite3
import pandas as pd

# Page config
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
DB_FILE = "hospital.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS Patients (
            pat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            address TEXT,
            email TEXT
        );
        CREATE TABLE IF NOT EXISTS Doctors (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            dept_id INTEGER,
            phone TEXT,
            email TEXT
        );
        CREATE TABLE IF NOT EXISTS Appointments (
            app_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER,
            doc_id INTEGER,
            app_date TEXT,
            app_time TEXT,
            status TEXT DEFAULT 'Scheduled'
        );
        CREATE TABLE IF NOT EXISTS MedicalRecords (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER,
            doc_id INTEGER,
            diagnosis TEXT,
            treatment TEXT,
            prescription TEXT
        );
        CREATE TABLE IF NOT EXISTS Billings (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER,
            amount REAL,
            details TEXT,
            payment_status TEXT DEFAULT 'Pending'
        );
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper functions
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

# Sidebar navigation
st.sidebar.title("🏥 Hospital Management")
page = st.sidebar.radio("Navigate", [
    "Home",
    "Patients",
    "Doctors",
    "Appointments",
    "Medical Records",
    "Billings"
])

if page == "Home":
    st.title("🏥 Hospital Management System")
    st.markdown("""
    Welcome to your hospital management dashboard!

    Use the sidebar to:
    - 👥 Add and view Patients
    - 👨‍⚕️ Add and view Doctors
    - 🗓️ Book and view Appointments
    - 📋 Add Medical Records
    - 💰 Generate Bills

    All data is saved permanently.
    """)
    st.success("System is ready!")

elif page == "Patients":
    st.header("👥 Patient Management")

    tab1, tab2 = st.tabs(["View & Edit All", "Add New Patient"])

    with tab1:
        df = get_data("Patients")
        st.subheader("All Patients")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        if st.button("💾 Save Changes"):
            conn = sqlite3.connect(DB_FILE)
            edited_df.to_sql("Patients", conn, if_exists="replace", index=False)
            conn.close()
            st.success("All patient data saved successfully!")
            st.rerun()

    with tab2:
        with st.form("add_patient_form"):
            st.subheader("Add New Patient")
            name = st.text_input("Name *")
            age = st.number_input("Age", min_value=0, max_value=150)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            phone = st.text_input("Phone *")
            address = st.text_area("Address")
            email = st.text_input("Email")

            submitted = st.form_submit_button("Add Patient")
            if submitted:
                if name and phone:
                    add_record("Patients", 
                               ["name", "age", "gender", "phone", "address", "email"],
                               [name, age, gender, phone, address, email])
                    st.success("Patient added successfully!")
                    st.rerun()
                else:
                    st.error("Name and Phone are required!")

elif page == "Doctors":
    st.header("👨‍⚕️ Doctor Management")

    with st.form("add_doctor_form"):
        st.subheader("Add New Doctor")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name *")
            specialty = st.text_input("Specialty")
            phone = st.text_input("Phone")
        with col2:
            dept_id = st.number_input("Department ID", min_value=1)
            email = st.text_input("Email")

        submitted = st.form_submit_button("Add Doctor")
        if submitted and name:
            add_record("Doctors", 
                       ["name", "specialty", "dept_id", "phone", "email"],
                       [name, specialty, dept_id, phone, email])
            st.success("Doctor added!")
            st.rerun()

    st.subheader("All Doctors")
    st.dataframe(get_data("Doctors"), use_container_width=True)

elif page == "Appointments":
    st.header("🗓️ Appointments")

    with st.form("book_appointment_form"):
        st.subheader("Book New Appointment")
        col1, col2 = st.columns(2)
        with col1:
            pat_id = st.number_input("Patient ID", min_value=1)
            doc_id = st.number_input("Doctor ID", min_value=1)
        with col2:
            app_date = st.date_input("Date")
            app_time = st.time_input("Time")

        submitted = st.form_submit_button("Book Appointment")
        if submitted:
            add_record("Appointments", 
                       ["pat_id", "doc_id", "app_date", "app_time"],
                       [pat_id, doc_id, str(app_date), str(app_time)])
            st.success("Appointment booked!")
            st.rerun()

    st.subheader("All Appointments")
    st.dataframe(get_data("Appointments"), use_container_width=True)

elif page == "Medical Records":
    st.header("📋 Medical Records")

    with st.form("add_record_form"):
        st.subheader("Add New Medical Record")
        col1, col2 = st.columns(2)
        with col1:
            pat_id = st.number_input("Patient ID", min_value=1)
            doc_id = st.number_input("Doctor ID", min_value=1)
        with col2:
            diagnosis = st.text_area("Diagnosis")
            treatment = st.text_area("Treatment")
            prescription = st.text_area("Prescription")

        submitted = st.form_submit_button("Save Record")
        if submitted:
            add_record("MedicalRecords", 
                       ["pat_id", "doc_id", "diagnosis", "treatment", "prescription"],
                       [pat_id, doc_id, diagnosis, treatment, prescription])
            st.success("Medical record saved!")
            st.rerun()

    st.subheader("All Records")
    st.dataframe(get_data("MedicalRecords"), use_container_width=True)

elif page == "Billings":
    st.header("💰 Billing Management")

    with st.form("new_bill_form"):
        st.subheader("Create New Bill")
        col1, col2 = st.columns(2)
        with col1:
            pat_id = st.number_input("Patient ID", min_value=1)
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        with col2:
            details = st.text_area("Bill Details")

        submitted = st.form_submit_button("Create Bill")
        if submitted:
            add_record("Billings", 
                       ["pat_id", "amount", "details"],
                       [pat_id, amount, details])
            st.success("Bill created!")
            st.rerun()

    st.subheader("All Bills")
    st.dataframe(get_data("Billings"), use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")
