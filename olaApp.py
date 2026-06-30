import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import base64
import plotly.express as px
from pathlib import Path

# ── Loading CSS ────────────────────────────────────────────────────────────
def load_css(file_name: str):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"❌ Style Load Error: Could not find '{file_name}'.")

load_css("style.css")

st.set_page_config(
    page_title="OLA Ride Insights",
    page_icon="🚕",
    layout="wide"
)

# ── Data Cleaning - EDA  ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "data" / "OLA_DataSet.xlsx"
df = pd.read_excel(CSV_FILE)

df['V_TAT'] = df['V_TAT'].fillna(df['V_TAT'].mean())
df['C_TAT'] = df['C_TAT'].fillna(df['C_TAT'].mean())

# Fill categorical nulls
df['Canceled_Rides_by_Customer'] = df['Canceled_Rides_by_Customer'].fillna('No')
df['Canceled_Rides_by_Driver'] = df['Canceled_Rides_by_Driver'].fillna('No')
df['Incomplete_Rides'] = df['Incomplete_Rides'].fillna('No')
df['Incomplete_Rides_Reason'] = df['Incomplete_Rides_Reason'].fillna('Completed')
df['Payment_Method'] = df['Payment_Method'].fillna('Not Applicable')

# Fill ratings
df['Driver_Ratings'] = df['Driver_Ratings'].fillna(0)
df['Customer_Rating'] = df['Customer_Rating'].fillna(0)

# Drop image column
df = df.drop('Vehicle Images', axis=1)

# Convert Data Types
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')

# Derived Features
df['Ride_Hour'] = pd.to_datetime(df['Time']).dt.hour
df['Ride_Day'] = df['Date'].dt.day_name()
df['Ride_Month'] = df['Date'].dt.month_name()
df['Is_Weekend'] = df['Date'].dt.dayofweek >= 5

df.to_csv(BASE_DIR / "data" / "OLA_Cleaned_DataSet.csv", index=False)

# ── PostgreSQL connection details ────────────────────────────────────────────────────────────
DB_USER     = "postgres"
DB_PASSWORD = "india*123"
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "OLADB"
TABLE_NAME  = "OLA_Bookings"

# ── Create Engine ────────────────────────────────────────────────────────────
engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Table Insertion ────────────────────────────────────────────────────────────
CSV_FILE = BASE_DIR / "data" / "OLA_Cleaned_DataSet.csv"
if "db_initialized" not in st.session_state:
    print("Reading CSV...")

    df = pd.read_csv(CSV_FILE)

    print(f"Rows found: {len(df)}")

    print("Creating table and inserting data...")

    df.to_sql(
        name=TABLE_NAME,
        con=engine,
        if_exists="replace",   # Drops and recreates table
        index=False,
        chunksize=10000
    )

    print("Data Insertion Successful !")
    st.session_state.db_initialized = True

def execute_sql(query_string: str) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query(text(query_string), conn)

# ── Background image ─────────────────────────────────────────────────────────
def get_base64(img_path: str) -> str:
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img = get_base64(BASE_DIR / "images/olabg.png")

# ── Full-width Header ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ola-header">
    <div class="ola-ring" style="width:130px;height:130px;right:80px;top:10px;"></div>
    <div class="ola-ring" style="width:90px;height:90px;right:100px;top:30px;"></div>
    <div class="ola-ring" style="width:50px;height:50px;right:120px;top:50px;"></div>
    <div class="ola-logo-outer">
        <div class="ola-logo-mid">
            <div class="ola-logo-inner">
                <div class="ola-logo-dot"></div>
            </div>
        </div>
    </div>
    <div>
        <div class="ola-name">OLA</div>
        <div class="ola-underline"></div>
        <div class="ola-sub1">Ride Analytics</div>
        <div class="ola-sub2">Business Intelligence Dashboard</div>
    </div>
</div>
<div class="ola-road">
    <span class="ola-road-tagline">● ● ● OLA OUTSTATION · CAB THAT TAKES YOU PLACES ● ● ●</span>
</div>
""", unsafe_allow_html=True)

# ── Fake sidebar + main content using columns ─────────────────────────────────
col_sidebar, col_main = st.columns([1, 4])

with col_sidebar:
    st.markdown("""
    <div class="stSidebar">
        <div class="fake-sidebar-title">Business Intelligence Dashboard</div>
    </div>
    
    """, unsafe_allow_html=True)

    page = st.radio(
        " ",
        ["🏠 Home", "🚗 OLA Rides", "📊 Power BI"],
        label_visibility="collapsed"
    )

with col_main:

    if page == "🏠 Home":
        # st.title('Ola Ride Insights')
        try:
            df = execute_sql("""
                            SELECT
                                COUNT(*) AS total_bookings,

                                COUNT(CASE WHEN "Booking_Status" = 'Success' THEN 1 END) AS successful_bookings,

                                COUNT(CASE WHEN "Booking_Status" <> 'Success' THEN 1 END) AS cancelled_bookings,

                                ROUND(
                                    COUNT(CASE WHEN "Booking_Status" = 'Success' THEN 1 END) * 100.0
                                    / COUNT(*),
                                    2
                                ) AS success_rate,

                                ROUND(
                                    COUNT(CASE WHEN "Booking_Status" <> 'Success' THEN 1 END) * 100.0
                                    / COUNT(*),
                                    2
                                ) AS cancellation_rate

                            FROM "OLA_Bookings"
                            """)

        except Exception as e:
            total_bookings, successful_bookings, cancelled_bookings = 0, 0, 0
            success_rate, cancellation_rate = 0, 0

        total_bookings = int(df["total_bookings"].iloc[0])
        successful_bookings = int(df["successful_bookings"].iloc[0])
        cancelled_bookings = int(df["cancelled_bookings"].iloc[0])
        success_rate = float(df["success_rate"].iloc[0])
        cancellation_rate = float(df["cancellation_rate"].iloc[0])

        col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
        with col_kpi1:
            st.metric(label="📋 Total Bookings", value=f"{total_bookings:,}")
        with col_kpi2:
            st.metric(label="✅ Successful Bookings", value=f"{successful_bookings:,}")
        with col_kpi3:
            st.metric(label="❌ Cancelled Bookings", value=f"{cancelled_bookings:,}")
        with col_kpi4:
            st.metric(label="📈 Success Rate", value=f"{success_rate:.2f}%")
        with col_kpi5:
            st.metric(label="📉 Cancel Rate", value=f"{cancellation_rate:.2f}%")
    

        st.divider()

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1 :
            status_df = pd.DataFrame({
                "Status": ["Successful", "Cancelled"],
                "Bookings": [successful_bookings, cancelled_bookings]
            })

            fig = px.pie(
                status_df,
                names="Status",
                values="Bookings",
                hole=0.6,
                title="Booking Status Distribution",
                color_discrete_sequence=[
                    "#2D31A1",  # Green - Successful
                    "#C9352B",  # Red - Cancelled
                ]
            )
            st.plotly_chart(fig, width="stretch")

        with col_chart2 :
            df = execute_sql("""
            SELECT
                "Ride_Hour",
                COUNT(*) AS total_bookings
            FROM "OLA_Bookings"
            GROUP BY
                "Ride_Hour"
            ORDER BY
                "Ride_Hour";
            """)

            fig = px.line(
                df,
                x="Ride_Hour",
                y="total_bookings",
                markers=True,
                title="Hourly Booking Trend"
            )

            fig.update_layout(
                xaxis=dict(dtick=1),
                xaxis_title="Hour of Day",
                yaxis_title="Total Bookings"
            )

            st.plotly_chart(fig, width='stretch')

    elif page == "🚗 OLA Rides":
        st.markdown("""
            ### 📈 OLA Business Insights

            Select a query from the list below to analyze booking performance, 
                    ride cancellations, payment methods, ratings, and revenue. 
                    These analysis provide valuable insights into the operational efficiency of the OLA ride-sharing platform.
            """)
        st.divider()

        analytics_options = [
            "Select ...",
            "Q1: Retrieve all successful bookings",
            "Q2: Find the average ride distance for each vehicle type",
            "Q3: Get the total number of cancelled rides by customers",        
            "Q4: List the top 5 customers who booked the highest number of rides",  
            "Q5: Get the number of rides cancelled by drivers due to personal and car-related issues",      
            

            "Q6: Find the maximum and minimum driver ratings for Prime Sedan bookings",
            "Q7: Retrieve all rides where payment was made using UPI",
            "Q8: Find the average customer rating per vehicle type",
            "Q9: Calculate the total booking value of rides completed successfully",
            "Q10: List all incomplete rides along with the reason"

        ]

        chosen_question = st.selectbox(
            label="🔍 Select OLA  Query :",
            options=analytics_options,
            index=0
        )
        st.divider()

        output_container = st.container()

        with output_container:
            # if chosen_question == "Select ...":
            #     st.info("💡 Please choose an analytical reporting question from the selection box above to pull down live metrics.")

            # --- QUERY 1 ---
            if chosen_question.startswith("Q1:"):
                st.subheader("✅ Successful Bookings")
                sql = """
                    SELECT 
                        "Date",
                        "Time",
                        "Booking_ID" AS "Booking ID",
                        "Booking_Status" AS "Booking Status",
                        "Customer_ID" AS "Customer ID",
                        "Vehicle_Type" AS "Vehicle Type",
                        "Pickup_Location" AS "Pickup Location",
                        "Drop_Location" AS "Drop Location",
                        "V_TAT" AS "Vehicle Turn Around Time",
                        "C_TAT" AS "Customer Turn Around Time",
                        "Canceled_Rides_by_Customer" AS "Canceled Rides by Customer",
                        "Canceled_Rides_by_Driver" AS "Canceled Rides by Driver",
                        "Incomplete_Rides" AS "Incomplete Rides",
                        "Incomplete_Rides_Reason" AS "Incomplete Ride Reason",
                        "Booking_Value" AS "Booking Value",
                        "Payment_Method" AS "Payment Method",
                        "Ride_Distance" AS "Ride Distance",
                        "Driver_Ratings" AS "Driver Rating",
                        "Customer_Rating" AS "Customer Rating",
                        "Ride_Hour" AS "Ride Hour",
                        "Ride_Day" AS "Ride Day",
                        "Ride_Month" AS "Ride Month",
                        CASE WHEN "Is_Weekend" THEN 'Yes' ELSE 'No' END AS "Is Weekend"
                    FROM "OLA_Bookings"
                    WHERE "Booking_Status" = 'Success' 
                    ORDER BY "Date" DESC;
                """
                try:
                    df = execute_sql(sql)
                    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
                    df["Time"] = pd.to_datetime(df["Time"]).dt.strftime("%H:%M:%S")

                    st.dataframe(df,column_config={
                        "Customer ID" : None,
                        "Ride Hour": None,
                        "Ride Day": None,
                        "Ride Month": None,
                        "Is Weekend": None
                    } , width="stretch", hide_index=True)
                    st.success(f"""**Business Insight:** A higher number of successful bookings indicates better service reliability,
                        efficient driver allocation, and improved customer experience.""")
                except Exception as e:
                    st.error(f"Execution Error: {e}")

            # --- QUERY 2 ---
            elif chosen_question.startswith("Q2:"):
                st.subheader("🚗 Average Ride Distance by Vehicle Type")
                sql = """
                    SELECT
                        "Vehicle_Type" AS "Vehicle Type",
                        ROUND(AVG("Ride_Distance"),2) AS "Average Distance"
                    FROM "OLA_Bookings"
                    GROUP BY "Vehicle_Type"
                    ORDER BY "Average Distance" DESC;
                """
                try:
                    df = execute_sql(sql)
                    df["Average Distance"] = df["Average Distance"].astype(str)

                    st.dataframe(df, width="stretch", hide_index=True)
                    st.success(f"""
                        **Business Insight:** Vehicle categories with longer average trip distances generate
                            higher revenue potential and help optimize fleet deployment.
                        """)
                except Exception as e:
                    st.error(f"Execution Error: {e}")
            
            # --- QUERY 3 ---
            elif chosen_question.startswith("Q3:"):
                st.subheader("❌ Customer Cancelled Rides")
                sql = """
                    SELECT COUNT(*) AS "Canceled Rides By Customers"
                    FROM "OLA_Bookings"
                    WHERE "Canceled_Rides_by_Customer" <> 'No' ;
                """
                try:
                    df = execute_sql(sql)
                    df["Canceled Rides By Customers"] = df["Canceled Rides By Customers"].astype(str)

                    st.dataframe(df, width="stretch", hide_index=True)
                    st.success(f"""**Business Insight:** High customer cancellations may indicate long waiting times,
                    pricing concerns, or changes in customer plans.
                    Overall, reducing operational issues such as driver-initiated cancellations, 
                            delayed pickups, and vehicle maintenance problems can significantly improve ride completion rates, 
                            customer satisfaction, and overall platform reliability.""")
                except Exception as e:
                    st.error(f"Execution Error: {e}")

            # --- QUERY 4 ---
            elif chosen_question.startswith("Q4:"):
                st.subheader("🏆 Top 5 Loyal Customers")
                sql = """
                    SELECT
                        "Customer_ID" AS "Customer ID",
                        COUNT(*) AS "Number of Rides"
                    FROM "OLA_Bookings"
                    GROUP BY "Customer_ID"
                    ORDER BY "Number of Rides" DESC
                    LIMIT 5;
                """
                try:
                    df = execute_sql(sql)
                    df["Number of Rides"] = df["Number of Rides"].astype(str)

                    st.dataframe(df, width="stretch", hide_index=True)
                    st.success(f"""
                        **Business Insight:** Frequent riders can be targeted with loyalty programs,
                        discounts, and personalized offers to improve customer retention.
                        """)
                except Exception as e:
                    st.error(f"Execution Error: {e}")

            # --- QUERY 5 ---
            elif chosen_question.startswith("Q5:"):
                st.subheader("🚖 Driver Cancellation Analysis")
                sql = """
                    SELECT COUNT(*) AS "Canceled Rides By Driver"
                    FROM "OLA_Bookings"
                    WHERE "Canceled_Rides_by_Driver" = 'Personal & Car related issue' ;
                """
                try:
                    df = execute_sql(sql)
                    df["Canceled Rides By Driver"] = df["Canceled Rides By Driver"].astype(str)

                    st.dataframe(df, width="stretch", hide_index=True)
                    st.success(f"""**Business Insight:** Monitoring driver cancellation reasons helps improve
                        driver availability, fleet maintenance, and overall service quality.""")
                except Exception as e:
                    st.error(f"Execution Error: {e}")

            # --- QUERY 6 ---
            elif chosen_question.startswith("Q6:"):
                st.subheader("⭐ Prime Sedan Driver Ratings")
                sql = """
                    SELECT
                        MAX("Driver_Ratings") AS "Max Rating",
                        MIN("Driver_Ratings") AS "Min Rating"
                    FROM "OLA_Bookings"
                    WHERE "Vehicle_Type" = 'Prime Sedan';
                """
                try:
                    
                    df = execute_sql(sql)
                    
                    df["Max Rating"] = df["Max Rating"].astype(str)
                    df["Min Rating"] = df["Min Rating"].astype(str)
                    
                    st.dataframe(df, width="stretch", hide_index=True)
                    st.success(f"""
                        **Business Insight:** Identifying highly rated drivers helps recognize top performers,
                        while low ratings highlight opportunities for driver training and service improvement.
                        """)
                except Exception as e:
                    st.error(f"Execution Error: {e}")

            # --- QUERY 7 ---
            elif chosen_question.startswith("Q7:"):
                st.subheader("💳 UPI Payment Transactions")
                sql = """
                    SELECT 
                        "Date",
                        "Time",
                        "Booking_ID" AS "Booking ID",
                        "Booking_Status" AS "Booking Status",
                        "Customer_ID" AS "Customer ID",
                        "Vehicle_Type" AS "Vehicle Type",
                        "Pickup_Location" AS "Pickup Location",
                        "Drop_Location" AS "Drop Location",
                        "V_TAT" AS "Vehicle Turn Around Time",
                        "C_TAT" AS "Customer Turn Around Time",
                        "Canceled_Rides_by_Customer" AS "Canceled Rides by Customer",
                        "Canceled_Rides_by_Driver" AS "Canceled Rides by Driver",
                        "Incomplete_Rides" AS "Incomplete Rides",
                        "Incomplete_Rides_Reason" AS "Incomplete Ride Reason",
                        "Booking_Value" AS "Booking Value",
                        "Payment_Method" AS "Payment Method",
                        "Ride_Distance" AS "Ride Distance",
                        "Driver_Ratings" AS "Driver Rating",
                        "Customer_Rating" AS "Customer Rating",
                        "Ride_Hour" AS "Ride Hour",
                        "Ride_Day" AS "Ride Day",
                        "Ride_Month" AS "Ride Month",
                        CASE WHEN "Is_Weekend" THEN 'Yes' ELSE 'No' END AS "Is Weekend"
                    FROM "OLA_Bookings"
                    WHERE "Payment_Method" = 'UPI'
                    ORDER BY "Date" DESC;
                """
                try:
                    df = execute_sql(sql)
                    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
                    df["Time"] = pd.to_datetime(df["Time"]).dt.strftime("%H:%M:%S")

                    st.dataframe(df,column_config={
                        "Customer ID" : None,
                        "Ride Hour": None,
                        "Ride Day": None,
                        "Ride Month": None,
                        "Is Weekend": None
                    } , width="stretch", hide_index=True)
                
                    st.success(f"""
                        **Business Insight:** Understanding payment preferences enables better
                        digital payment strategies and promotional campaigns.
                        """)
                except Exception as e:
                    st.error(f"Execution Error: {e}")

            # --- QUERY 8 ---
            elif chosen_question.startswith("Q8:"):
                st.subheader("🌟 Customer Ratings by Vehicle Type")
                sql = """
                    SELECT
                        "Vehicle_Type" AS "Vehicle Type",
                        ROUND(
                            AVG("Customer_Rating")::numeric, 2
                        ) AS "Average Customer Rating"
                    FROM "OLA_Bookings"
                    GROUP BY "Vehicle Type";
                """
                try:
                    df = execute_sql(sql)
                    df["Average Customer Rating"] = df["Average Customer Rating"].astype(str)

                    st.dataframe(df, width="stretch", hide_index=True)
                    st.success(f"""
                        **Business Insight:** Vehicle types with consistently higher ratings indicate
                        better customer experiences and can guide quality improvement initiatives.
                        """)
                except Exception as e:
                    st.error(f"Execution Error: {e}")

            # --- QUERY 9 ---
            elif chosen_question.startswith("Q9:"):
                st.subheader("💰 Revenue from Successful Rides")
                sql = """
                    SELECT
                        ROUND(SUM("Booking_Value"),2) AS "Revenue"
                    FROM "OLA_Bookings"
                    WHERE "Booking_Status" = 'Success';
                """
                try:
                    df = execute_sql(sql)
                    df["Revenue"] = df["Revenue"].astype(str)

                    st.dataframe(df, width="stretch", hide_index=True)
                    st.success(f"""
                        **Business Insight:** Comparing successful ride revenue with cancellation trends
                        helps evaluate revenue loss and operational efficiency.
                        """)
                except Exception as e:
                    st.error(f"Execution Error: {e}")

            # --- QUERY 10 ---
            elif chosen_question.startswith("Q10:"):
                st.subheader("⚠️ Incomplete Rides")
                sql = """
                    SELECT
                        "Date",
                        "Time",
                        "Booking_ID" AS "Booking ID",
                        "Booking_Status" AS "Booking Status",
                        "Customer_ID" AS "Customer ID",
                        "Vehicle_Type" AS "Vehicle Type",
                        "Pickup_Location" AS "Pickup Location",
                        "Drop_Location" AS "Drop Location",
                        "V_TAT" AS "Vehicle Turn Around Time",
                        "C_TAT" AS "Customer Turn Around Time",
                        "Incomplete_Rides_Reason" AS "Incomplete Ride Reason",
                        "Booking_Value" AS "Booking Value",
                        "Payment_Method" AS "Payment Method",
                        "Ride_Distance" AS "Ride Distance",
                        "Driver_Ratings" AS "Driver Rating",
                        "Customer_Rating" AS "Customer Rating",
                        "Ride_Hour" AS "Ride Hour",
                        "Ride_Day" AS "Ride Day",
                        "Ride_Month" AS "Ride Month",
                        CASE WHEN "Is_Weekend" THEN 'Yes' ELSE 'No' END AS "Is Weekend"
                    FROM "OLA_Bookings"
                    WHERE "Incomplete_Rides" = 'Yes'
                    ORDER BY "Date" DESC;
                """
                try:
                    df = execute_sql(sql)
                    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
                    df["Time"] = pd.to_datetime(df["Time"]).dt.strftime("%H:%M:%S")

                    st.dataframe(df,column_config={
                        "Date" : None,
                        "Time" : None,
                        "Booking Status" : None,
                        "Customer ID" : None,
                        "Vehicle Turn Around Time" : None,
                        "Customer Turn Around Time" : None,
                        "Driver Rating" : None,
                        "Customer Rating" : None,
                        "Ride Hour": None,
                        "Ride Day": None,
                        "Ride Month": None,
                        "Is Weekend": None
                    } , width="stretch", hide_index=True)
                
                    st.success(f"""
                        **Business Insight:** Analyzing incomplete ride reasons helps reduce service disruptions,
                        improve driver performance, and enhance customer satisfaction.
                        """)
                except Exception as e:
                    st.error(f"Execution Error: {e}")
        
        
        
        