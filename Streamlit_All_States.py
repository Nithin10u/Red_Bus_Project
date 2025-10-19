import streamlit as st
import pandas as pd

st.set_page_config(page_title="India Bus Dashboard", layout="wide")

# ----------------------------
# STEP 1: Load all CSV files
# ----------------------------
@st.cache_data
def load_all_data():
    files = {
        "Andhra Pradesh": "AndhraPradesh_All_Bus_Data.csv",
        "Jodhpur": "Jodhpur_All_Bus_Data.csv",
        "Kerala": "Kerala_All_Bus_Data.csv",
        "Telangana": "Telangana_All_Bus_Data.csv",
        "Uttar Pradesh": "UttarPradesh_All_Bus_Data.csv",
    }
    
    all_dataframes = []
    for state, file_path in files.items():
        df = pd.read_csv(file_path)
        df["state"] = state
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # remove unnamed columns
        all_dataframes.append(df)
    
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    return combined_df

# Load data
data = load_all_data()

# ----------------------------
# STEP 2: Clean Columns
# ----------------------------
# Clean price column (remove ₹ and commas, convert to numeric)
data["price"] = data["price"].astype(str).str.replace("₹", "").str.replace(",", "")
data["price"] = pd.to_numeric(data["price"], errors="coerce").fillna(0)

# Ensure star_rating is numeric
data["star_rating"] = pd.to_numeric(data["star_rating"], errors="coerce").fillna(0)


# ----------------------------
# STEP 3: Sidebar Filters
# ----------------------------
st.sidebar.header("🚌 Filter Options")

# Select State
state = st.sidebar.selectbox("Select State", data["state"].unique())

# Filter by selected state
state_data = data[data["state"] == state]

# Route filter (use bus_route column)
routes = state_data["bus_route"].dropna().unique()
route = st.sidebar.selectbox("Select Route", sorted(routes))

# Filter by selected route
filtered_data = state_data[state_data["bus_route"] == route]

# Bus type filter
bus_types = filtered_data["bus_type"].dropna().unique()
bus_type = st.sidebar.selectbox("Select Bus Type", sorted(bus_types))

# Star rating & price filters
star_min, star_max = st.sidebar.slider(
    "Select Star Rating Range", 0.0, 5.0, (0.0, 5.0)
)
price_min, price_max = int(filtered_data["price"].min()), int(filtered_data["price"].max())
price_range = st.sidebar.slider(
    "Select Price Range", price_min, price_max, (price_min, price_max)
)

# ----------------------------
# STEP 4: Apply Filters
# ----------------------------
final_data = filtered_data[
    (filtered_data["bus_type"] == bus_type) &
    (filtered_data["star_rating"] >= star_min) &
    (filtered_data["star_rating"] <= star_max) &
    (filtered_data["price"] >= price_range[0]) &
    (filtered_data["price"] <= price_range[1])
]


# ----------------------------
# STEP 5: Display Results
# ----------------------------
st.title("🚌 All India Bus Data Dashboard")

if not final_data.empty:
    st.subheader(f"Available Buses in {state} ({route})")
    st.dataframe(final_data, use_container_width=True)

    st.markdown("### Example Bus Details")
    bus = final_data.iloc[0]
    st.markdown(f"*Bus Name:* {bus['bus_name']}")
    st.markdown(f"*Bus Type:* {bus['bus_type']}")
    st.markdown(f"*Departure:* {bus['departing_time']}")
    st.markdown(f"*Arrival:* {bus['reaching_time']}")
    st.markdown(f"*Duration:* {bus['duration']}")
    st.markdown(f"*Seats Available:* {bus['seat_available']}")
    st.markdown(f"*Star Rating:* ⭐ {bus['star_rating']}")
    st.markdown(f"*Price:* ₹{bus['price']}")
else:
    st.warning("No buses found for the selected filters.")

# Optional: show raw data
if st.checkbox("Show raw data"):
    st.dataframe(data)