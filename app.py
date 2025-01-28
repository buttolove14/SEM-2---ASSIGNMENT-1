import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px

# Google Sheets API Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("rr.json", scope)
client = gspread.authorize(creds)

# Function to fetch data from Google Sheets
@st.cache_data(ttl=60)  # Cache the data for 60 seconds
def fetch_data(sheet_url, sheet_name="Sheet1"):
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Streamlit App
st.title("Google Sheets Insights in Streamlit")

# Input: Google Sheet URL
sheet_url = st.text_input(
    "Enter your Google Sheet URL:",
    placeholder="https://docs.google.com/spreadsheets/d/1_A-nQdfWg_EX6W_2Yd1w-m334s660gu6YjbvK7l_Utk/edit?usp=sharing"
)

if sheet_url:
    try:
        # Fetch data from Google Sheets
        df = fetch_data(sheet_url)

        # Ensure necessary columns exist
        required_columns = ['Name', 'Brand Name', 'Brand Tier', 'Portal']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.warning(f"Missing columns in the dataset: {', '.join(missing_columns)}")

        # Sidebar Navigation
        st.sidebar.title("Navigation")
        name_selected = st.sidebar.selectbox("Select a Name:", df['Name'].unique())

        if name_selected:
            # Filter data for the selected person
            filtered_data = df[df['Name'] == name_selected]

            # Display detailed insights for the selected person
            st.subheader(f"Insights for {name_selected}")
            st.write(f"**Total Number of Brands:** {filtered_data['Brand Name'].nunique()}")

            # Brand Categories by Tier
            if 'Brand Tier' in df.columns:
                brand_tiers = filtered_data.groupby('Brand Tier')['Brand Name'].nunique().reset_index()
                brand_tiers = brand_tiers.rename(columns={'Brand Name': 'Number of Brands'})

                st.write("**Brands by Tier:**")
                st.table(brand_tiers)

                # Visualization: Brands by Tier
                fig_tier = px.pie(
                    brand_tiers,
                    names='Brand Tier',
                    values='Number of Brands',
                    title="Brand Distribution by Tier",
                )
                st.plotly_chart(fig_tier)

            # Brand Categories by Portal
            if 'Portal' in df.columns:
                brand_portals = filtered_data.groupby('Portal')['Brand Name'].nunique().reset_index()
                brand_portals = brand_portals.rename(columns={'Brand Name': 'Number of Brands'})

                st.write("**Brands by Portal:**")
                st.table(brand_portals)

                # Visualization: Brands by Portal
                fig_portal = px.bar(
                    brand_portals,
                    x='Portal',
                    y='Number of Brands',
                    title="Brand Distribution by Portal",
                    labels={'Number of Brands': 'Brands', 'Portal': 'Portal'}
                )
                st.plotly_chart(fig_portal)

        # Overall Insights: Brands per person with categories
        st.subheader("Overall Insights")
        overall_brand_tiers = df.groupby(['Name', 'Brand Tier'])['Brand Name'].nunique().reset_index()
        overall_brand_tiers = overall_brand_tiers.rename(columns={'Brand Name': 'Number of Brands'})

        # Visualization: Overall Brands by Tier
        fig_overall = px.bar(
            overall_brand_tiers,
            x='Name',
            y='Number of Brands',
            color='Brand Tier',
            barmode='group',
            title="Brands Managed by Each Person (Grouped by Tier)",
            labels={'Number of Brands': 'Brands', 'Name': 'Person'}
        )
        st.plotly_chart(fig_overall)

    except Exception as e:
        st.error(f"Error: {e}")
