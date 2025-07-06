import streamlit as st
import pandas as pd
import sqlite3
import io
import os

# --- Page config ---
st.set_page_config(page_title="Investor Lookup & Deal Summary", layout="wide")

# --- Load data ---
@st.cache_data(show_spinner=False)
def load_data():
    if not os.path.exists("investor_lookup.db"):
        import subprocess
        subprocess.run(["python", "load_to_sqlite.py"])
    conn = sqlite3.connect("investor_lookup.db")
    investors = pd.read_sql_query("SELECT * FROM investors", conn)
    deals = pd.read_sql_query("SELECT * FROM deals", conn)
    projects = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()
    return investors, deals, projects

investors, deals, projects = load_data()

# --- App header ---
st.title("Investor Lookup & Deal Summary")
st.markdown("""
Paste an investor's email or ID below to view their profile, deal summary, and platform/project stats.\
Use the project table at the bottom for reference.\
""")

# --- Search bar ---
search_input = st.text_input("Search by Investor Email or ID", "", help="Paste the investor's email or their unique ID.")

# --- Investor lookup ---
def find_investor(search):
    if not search:
        return None
    mask = (
        investors["Record ID - Contact"].astype(str).str.lower() == search.strip().lower()
    ) | (
        investors["Email"].astype(str).str.lower() == search.strip().lower()
        if "Email" in investors.columns else False
    )
    matches = investors[mask]
    if matches.empty:
        return None
    return matches.iloc[0]

investor = find_investor(search_input)

if investor is None and search_input:
    st.warning("No investor found. Please check the email or ID and try again.")

if investor is not None:
    # --- Investor Profile ---
    st.subheader("Investor Profile")
    st.dataframe(pd.DataFrame([investor]))

    # --- Deal Summary Metrics ---
    st.subheader("Deal Summary")
    investor_email = investor.get("Email") or investor.get("Email Address")
    investor_id = investor.get("Record ID - Contact")
    # Find deals for this investor
    deal_mask = (
        (deals["Email Address"].astype(str).str.lower() == str(investor_email).lower())
        if "Email Address" in deals.columns else False
    ) | (
        (deals["Associated Contact IDs"].astype(str).str.contains(str(investor_id)))
        if "Associated Contact IDs" in deals.columns else False
    )
    investor_deals = deals[deal_mask]
    total_deals = len(investor_deals)
    total_invested = 0
    if "Amount in SGD" in investor_deals.columns:
        total_invested = investor_deals["Amount in SGD"].fillna(0).sum()
    elif "Total Investment Amount" in investor_deals.columns:
        total_invested = investor_deals["Total Investment Amount"].fillna(0).sum()
    col1, col2 = st.columns(2)
    col1.metric("Total Deals", total_deals)
    col2.metric("Total Invested (SGD)", f"${total_invested:,.2f}")

    # --- Download CSV ---
    profile_csv = pd.DataFrame([investor]).to_csv(index=False)
    st.download_button("Download Profile as CSV", profile_csv, file_name="investor_profile.csv", mime="text/csv")

# --- Platform Snapshot ---
st.subheader("Platform Snapshot")
col1, col2, col3 = st.columns(3)
col1.metric("Total Projects", len(projects))
if "Crowdfunded Amount (SGD)" in projects.columns:
    col2.metric("Total Crowdfunded (SGD)", f"${projects['Crowdfunded Amount (SGD)'].fillna(0).sum():,.2f}")
if "Crowdfunded Amount (IDR)" in projects.columns:
    col3.metric("Total Crowdfunded (IDR)", f"Rp{projects['Crowdfunded Amount (IDR)'].fillna(0).sum():,.0f}")

# --- Project Reference Table ---
st.subheader("Project Reference Table")
project_cols = [c for c in projects.columns if not c.startswith("Unnamed")]  # Hide empty columns
st.dataframe(projects[project_cols], use_container_width=True)

# --- Help/Instructions ---
st.info("""
**How to use:**
- Paste an investor's email or ID in the search bar and press Enter.
- View their profile, deal summary, and download their info as CSV.
- See overall platform stats and browse all projects below.
""")
 