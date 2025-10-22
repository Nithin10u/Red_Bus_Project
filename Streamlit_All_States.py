import streamlit as st
import pandas as pd

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    # Load datasets
    datasets = {
        "Andhra Pradesh": "AndhraPradesh_All_Bus_Data.csv",
        "Jodhpur": "Jodhpur_All_Bus_Data.csv",
        "Kerala": "Kerala_All_Bus_Data.csv",
        "Telangana": "Telangana_All_Bus_Data.csv",
        "Uttar Pradesh": "UttarPradesh_All_Bus_Data.csv",
        "Assam": "Assam_All_Bus_Data.csv",
        "Bihar": "Bihar_All_Bus_Data.csv",
        "Himachal Pradesh": "HimachalPradesh_All_Bus_Data.csv",
        "Kadamba": "Kadamba_All_Bus_Data.csv",
        "Punjab": "Punjab_All_Bus_Data.csv",
    }

    all_data_list = []

    for state_name, file_name in datasets.items():
        df = pd.read_csv(file_name)
        df["state"] = state_name
        all_data_list.append(df)

    all_data = pd.concat(all_data_list, ignore_index=True)

    # Remove unnamed columns
    all_data = all_data.loc[:, ~all_data.columns.str.contains("^Unnamed")]

    # Clean column names
    all_data.columns = all_data.columns.str.strip().str.lower()

    # Clean price and rating
    all_data["price"] = (
        all_data["price"].astype(str)
        .str.replace("₹", "", regex=True)
        .str.replace(",", "", regex=True)
    )
    all_data["price"] = pd.to_numeric(all_data["price"], errors="coerce").fillna(0)

    try:
        all_data["star_rating"] = all_data["star_rating"].astype(float)
    except:
        all_data["star_rating"] = 0.0

    # Strip strings and lowercase for consistency
    for col in ["bus_route", "bus_type", "bus_name"]:
        if col in all_data.columns:
            all_data[col] = all_data[col].astype(str).str.strip().str.lower()

    return all_data

all_data = load_data()

# ---------------- Sidebar Filters ----------------
st.sidebar.title("🚌 Bus Data Filter Options")

# State selection
state = st.sidebar.selectbox("Select State", sorted(all_data["state"].unique()))

state_data = all_data[all_data["state"] == state]

# Route selection with "All" option
routes = sorted(state_data["bus_route"].dropna().unique())
routes = ["All"] + routes
route = st.sidebar.selectbox("Select Route", routes)

# Bus type selection with "All" option
bus_types = sorted(state_data["bus_type"].dropna().unique())
bus_types = ["All"] + bus_types
bus_type = st.sidebar.selectbox("Select Bus Type", bus_types)

# Star rating slider
star_rating = st.sidebar.slider(
    "Select Star Rating", 0.0, 5.0, (0.0, 5.0)
)

# Price slider
price_min = int(all_data["price"].min())
price_max = int(all_data["price"].max())
price_range = st.sidebar.slider(
    "Select Price Range", price_min, price_max, (price_min, price_max)
)

# ---------------- Data Filtering ----------------
filtered_data = state_data[
    (state_data["star_rating"].between(star_rating[0], star_rating[1]))
    & (state_data["price"].between(price_range[0], price_range[1]))
]

if route != "All":
    filtered_data = filtered_data[filtered_data["bus_route"] == route]

if bus_type != "All":
    filtered_data = filtered_data[filtered_data["bus_type"] == bus_type]

# ---------------- Display Results ----------------
st.title("🚌 Bus Timings Data Dashboard")
st.subheader("Filtered Bus Data")

if filtered_data.empty:
    st.warning("⚠ No data available for the selected filters.")
else:
    st.dataframe(filtered_data)

    st.subheader("🕒 Bus Timings Details")
    selected_bus = filtered_data.iloc[0]

    st.markdown(f"*Bus Name:* {selected_bus['bus_name'].title()}")
    st.markdown(f"*Bus Type:* {selected_bus['bus_type'].title()}")
    st.markdown(f"*Departure Time:* {selected_bus['departing_time']}")
    st.markdown(f"*Arrival Time:* {selected_bus['reaching_time']}")
    st.markdown(f"*Duration:* {selected_bus['duration']}")
    st.markdown(f"*Seats Available:* {selected_bus['seat_available']}")
    st.markdown(f"*Star Rating:* ⭐ {selected_bus['star_rating']}")
    st.markdown(f"*Price:* ₹{int(selected_bus['price'])}")

st.success("✅ Data loaded successfully!")
