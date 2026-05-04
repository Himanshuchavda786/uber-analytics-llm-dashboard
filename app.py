import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
from groq import Groq

GROQ_API_KEY = ""

st.set_page_config(page_title="Uber Analytics",layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("Uber.csv")

    # -------------------------
    # 1. Standardize Column Names
    # -------------------------
    df.columns = df.columns.str.strip()

    # -------------------------
    # 2. Drop Duplicates
    # -------------------------
    df = df.drop_duplicates()

    # -------------------------
    # 3. Handle Missing Values
    # -------------------------
    df["Booking Value"] = pd.to_numeric(df["Booking Value"], errors="coerce")
    df["Ride Distance"] = pd.to_numeric(df["Ride Distance"], errors="coerce")
    df["Customer Rating"] = pd.to_numeric(df["Customer Rating"], errors="coerce")

    # Fill missing numeric values
    df["Booking Value"].fillna(0, inplace=True)
    df["Ride Distance"].fillna(df["Ride Distance"].median(), inplace=True)
    df["Customer Rating"].fillna(df["Customer Rating"].mean(), inplace=True)

    # Fill categorical
    df["Payment Method"].fillna("Unknown", inplace=True)
    df["Vehicle Type"].fillna("Unknown", inplace=True)

    # -------------------------
    # 4. Fix Data Types
    # -------------------------
    df["Booking Status"] = df["Booking Status"].astype("category")
    df["Vehicle Type"] = df["Vehicle Type"].astype("category")
    df["Payment Method"] = df["Payment Method"].astype("category")

    # -------------------------
    # 5. Remove Invalid Data
    # -------------------------
    df = df[df["Ride Distance"] > 0]
    df = df[df["Booking Value"] >= 0]

    # -------------------------
    # 6. Feature Engineering
    # -------------------------
    df["Revenue_per_km"] = df["Booking Value"] / df["Ride Distance"]

    # -------------------------
    # 7. Outlier Handling (IQR Method)
    # -------------------------
    Q1 = df["Booking Value"].quantile(0.25)
    Q3 = df["Booking Value"].quantile(0.75)
    IQR = Q3 - Q1

    df = df[
        (df["Booking Value"] >= Q1 - 1.5 * IQR) &
        (df["Booking Value"] <= Q3 + 1.5 * IQR)
    ]

    return df

df = load_data()

params = st.query_params.to_dict()

if "page" not in params:
    params["page"] = "Dataset"

current_page = params["page"]

st.markdown("""
<style>

/* =========================
   SIDEBAR GLASS BACKGROUND
========================= */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* =========================
   OPTION MENU BASE STYLE
========================= */
.nav-link {
    color: #cbd5f5 !important;
    font-size: 15px !important;
    padding: 12px 14px !important;
    margin: 6px 10px !important;
    border-radius: 10px !important;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.3s ease !important;
}

/* =========================
   ICON STYLE
========================= */
.nav-link i {
    color: #94a3b8 !important;
    font-size: 18px !important;
    transition: all 0.3s ease;
}

/* =========================
   HOVER STATE
========================= */
.nav-link:hover {
    background: rgba(37, 99, 235, 0.15) !important;
    color: #ffffff !important;
    transform: translateX(4px);
}

.nav-link:hover i {
    color: #38BDF8 !important;
}

/* =========================
   ACTIVE STATE (SELECTED)
========================= */
.nav-link.active {
    background: rgba(37, 99, 235, 0.25) !important;
    color: #ffffff !important;
    border-left: 4px solid #2563EB !important;
}

/* Active icon */
.nav-link.active i {
    color: #38BDF8 !important;
}

/* =========================
   REMOVE STREAMLIT DEFAULT RED
========================= */
.nav-pills .nav-link.active {
    background-color: rgba(37, 99, 235, 0.25) !important;
}

/* =========================
   SIDEBAR TITLE (OPTIONAL)
========================= */
.sidebar-title {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    padding: 10px 14px;
}

/* =========================
   SMOOTH SCROLLBAR
========================= */
section[data-testid="stSidebar"]::-webkit-scrollbar {
    width: 6px;
}

section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background: rgba(148,163,184,0.3);
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

with st.sidebar:

    st.markdown("""
    <div class="sidebar-title">
        🚗 Uber Analytics
    </div>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=[
            "Dataset",
            "Overview",
            "Ride Analytics",
            "Data Assistant",
            "Chatbot",
            "Dashboard"
        ],
        icons=[
            "table",
            "bar-chart",
            "graph-up",
            "robot",
            "chat-dots",
            "speedometer2"
        ],
        default_index=1,

        styles={

            # =========================
            # 🧊 FULL GLASS CONTAINER (FIXED)
            # =========================
            "container": {
                "padding": "6px",
                "background-color": "rgba(255,255,255,0.02)",  # ultra transparent
                "border": "1px solid rgba(255,255,255,0.08)",  # ONLY white border
                "border-radius": "12px",
                "backdrop-filter": "blur(18px)"
            },

            # =========================
            # ICON STYLE
            # =========================
            "icon": {
                "font-size": "18px",
                "color": "#94a3b8"
            },

            # =========================
            # NORMAL ITEM
            # =========================
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "6px",
                "padding": "10px 12px",
                "border-radius": "10px",
                "color": "#cbd5f5",
                "--hover-color": "rgba(37,99,235,0.15)"
            },

            # =========================
            # ACTIVE ITEM
            # =========================
            "nav-link-selected": {
                "background-color": "rgba(37,99,235,0.25)",
                "color": "white",
                "border-left": "3px solid #2563EB"
            }
        }
    )

if current_page != selected:
    st.query_params["page"] = selected
    st.rerun()

st.markdown("""
<style>

/* =====================================================
   🎨 DESIGN TOKENS (SYSTEM CORE)
===================================================== */
:root {
    --bg-main: radial-gradient(circle at top left, #111c33 0%, #0b1220 40%, #050816 100%);
    --sidebar-bg: rgba(8, 12, 24, 0.88);

    --card-glass: rgba(30, 41, 59, 0.45);
    --card-dark: #0a0f1a;

    --primary: #2563EB;
    --accent: #38BDF8;

    --text: #ffffff;
    --muted: #94a3b8;

    --radius: 14px;
    --transition: 0.25s ease;
}

/* =====================================================
   🌌 MAIN BACKGROUND
===================================================== */
[data-testid="stAppViewContainer"] {
    background: var(--bg-main);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

/* =====================================================
   📌 SIDEBAR
===================================================== */
section[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* =====================================================
   🧠 GLOBAL TEXT
===================================================== */
h1, h2, h3, h4, h5 {
    color: var(--text) !important;
}

/* =====================================================
   📏 DIVIDER
===================================================== */
.divider {
    height: 1px;
    background: linear-gradient(to right, transparent, #334155, transparent);
    margin: 18px 0;
}

/* =====================================================
   🎯 KPI CARDS (GLASS)
===================================================== */
.kpi-card {
    background: var(--card-glass);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-radius: var(--radius);
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    transition: var(--transition);
    
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;   /* ✅ center horizontally */
    text-align: center;    /* ✅ center text */
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 45px rgba(0,0,0,0.55);
}

.kpi-title {
    font-size: 13px;
    color: var(--muted);
}

.kpi-value {
    font-size: 26px;
    font-weight: 600;
    color: var(--text);
    margin-top: 6px;
}

/* =====================================================
   📊 CHART CARDS (DARK)
===================================================== */
.chart-card {
    background: var(--card-dark);
    border-radius: var(--radius);
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 14px 35px rgba(0,0,0,0.6);
}

/* =====================================================
   🔘 BUTTONS
===================================================== */
.stButton > button {
    background: var(--primary);
    color: white;
    border-radius: 10px;
    padding: 8px 14px;
    border: none;
    transition: var(--transition);
}

.stButton > button:hover {
    background: #1d4ed8;
}

/* =====================================================
   🧾 INPUTS
===================================================== */
input, textarea {
    background: rgba(15, 23, 42, 0.7) !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* =====================================================
   📊 DATAFRAME
===================================================== */
[data-testid="stDataFrame"] {
    background: rgba(30, 41, 59, 0.35);
    border-radius: 12px;
}

/* =====================================================
   🏷️ TITLES
===================================================== */
.exec-title {
    font-size: 30px;
    font-weight: 700;
    color: var(--text);
}

.exec-subtitle {
    font-size: 14px;
    color: var(--muted);
}

/* =====================================================
   💬 CHAT UI (CLEAN INTEGRATION - NO CONFLICTS)
===================================================== */

/* remove default chat background */
[data-testid="stChatMessage"] {
    background: transparent !important;
}

/* user message */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background: rgba(37, 99, 235, 0.18);
    border-radius: var(--radius);
    padding: 10px 14px;
    margin: 10px 0;
}

/* assistant message */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(15, 23, 42, 0.6);
    border-radius: var(--radius);
    padding: 10px 14px;
    margin: 10px 0;
    border: 1px solid rgba(255,255,255,0.06);
}

/* chat input bar */
section[data-testid="stChatInput"] {
    background: rgba(8, 12, 24, 0.9);
    border-top: 1px solid rgba(255,255,255,0.08);
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)

if current_page == "Dataset":

    # =========================
    # TITLE
    # =========================
    st.markdown("""
    <h1>📊 Dataset Explorer</h1>
    <p style='color:#94a3b8;'>Explore, filter, and analyze operational data</p>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    # =========================
    # KPI SECTION (GLASS)
    # =========================
    k1, k2, k3 = st.columns(3)

    k1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Rows</div>
        <div class="kpi-value">{df.shape[0]:,}</div>
    </div>
    """, unsafe_allow_html=True)

    k2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Columns</div>
        <div class="kpi-value">{df.shape[1]}</div>
    </div>
    """, unsafe_allow_html=True)

    k3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Missing Values</div>
        <div class="kpi-value">{df.isna().sum().sum():,}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =========================
    # CONTROL PANEL (GLASS SECTION)
    # =========================
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.subheader("🎛 Data Controls")

    selected_columns = st.multiselect(
        "Choose Columns",
        df.columns,
        default=df.columns
    )

    filtered_df = df[selected_columns]

    search_value = st.text_input("🔍 Search Dataset")

    if search_value:
        filtered_df = filtered_df[
            filtered_df.astype(str).apply(
                lambda row: row.str.contains(search_value, case=False).any(),
                axis=1
            )
        ]

    col1, col2 = st.columns(2)

    with col1:
        filter_column = st.selectbox("Filter Column", filtered_df.columns)

    with col2:
        filter_value = st.selectbox(
            "Filter Value",
            filtered_df[filter_column].dropna().unique()
        )

    if st.button("Apply Filter"):
        filtered_df = filtered_df[
            filtered_df[filter_column] == filter_value
        ]

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =========================
    # TABLE SECTION (DARK CARD)
    # =========================
    st.subheader("📋 Dataset Table")

    row_limit = st.slider("Rows to display", 10, len(filtered_df), 100)

    st.dataframe(
        filtered_df.head(row_limit),
        use_container_width=True
    )

    if st.checkbox("Show Full Dataset"):
        st.dataframe(df, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =========================
    # STATISTICS SECTION
    # =========================
    st.subheader("📊 Column Statistics")

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    if len(numeric_cols) > 0:
        selected_col = st.selectbox("Select Column", numeric_cols)
        st.dataframe(filtered_df[selected_col].describe())

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =========================
    # EXPORT SECTION (GLASS)
    # =========================
    st.subheader("⬇ Export Data")

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Filtered Dataset",
        csv,
        "filtered_dataset.csv",
        "text/csv"
    )

    st.markdown('</div>', unsafe_allow_html=True)

if current_page == "Overview":

    # =========================
    # HEADER
    # =========================
    st.markdown("""
    <div class="exec-title">📊 Uber Operations Dashboard</div>
    <div class="exec-subtitle">Real-time operational & financial intelligence</div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    # =========================
    # KPI CALCULATIONS
    # =========================
    total_ride = len(df)
    completed_ride = df[df["Booking Status"] == "Completed"]

    total_revenue = completed_ride["Booking Value"].sum()
    avg_distance = completed_ride["Ride Distance"].mean()
    success_rate = (len(completed_ride) / total_ride) * 100 if total_ride > 0 else 0
    avg_rating = completed_ride["Customer Rating"].dropna().mean()

    # =========================
    # KPI SECTION
    # =========================
    k1, k2, k3, k4 = st.columns(4)

    k1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Revenue</div>
        <div class="kpi-value">₹{total_revenue:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    k2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Fulfillment Rate</div>
        <div class="kpi-value">{success_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    k3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Avg Distance</div>
        <div class="kpi-value">{avg_distance:.2f} km</div>
    </div>
    """, unsafe_allow_html=True)

    k4.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Customer Rating</div>
        <div class="kpi-value">{avg_rating:.1f} ⭐</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =========================
    # BUSINESS UNIT PERFORMANCE
    # =========================
    st.subheader("Business Unit Performance")

    bu_metrics = df.groupby("Vehicle Type").agg(
        Total_Booking=("Booking ID", "count"),
        Revenue=("Booking Value", "sum"),
        Avg_Distance=("Ride Distance", "mean"),
        Avg_Rating=("Customer Rating", "mean")
    )

    st.dataframe(bu_metrics.style.format({
        "Revenue": "₹{:.0f}",
        "Avg_Distance": "{:.2f} km",
        "Avg_Rating": "{:.1f}"
    }), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =========================
    # OPERATIONAL + CANCELLATION
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Operational Efficiency")

        eff_df = df.groupby("Vehicle Type")[["Avg VTAT", "Avg CTAT"]].mean()

        st.dataframe(eff_df.style.format("{:.1f}"), use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("Cancellation Audit")

        status_count = df["Booking Status"].value_counts().to_frame("Count")
        status_count["%"] = (status_count["Count"] / total_ride) * 100

        st.dataframe(status_count.style.format({"%": "{:.1f}%"}), use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =========================
    # FINANCIAL DEEP DIVE
    # =========================
    st.subheader("Financial Deep Dive")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Payment Preference**")
        pay_summary = completed_ride["Payment Method"].value_counts(normalize=True) * 100
        st.dataframe(pay_summary.rename("Usage %").to_frame().style.format("{:.1f}%"))

    with c2:
        st.markdown("**Cancellation Triggers**")

        cust = df["Reason for cancelling by Customer"].dropna().value_counts().head(3)
        drv = df["Driver Cancellation Reason"].dropna().value_counts().head(3)

        cust.index = "Customer: " + cust.index
        drv.index = "Driver: " + drv.index

        reason_df = pd.concat([cust, drv]).to_frame("Count")

        st.dataframe(reason_df)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =========================
    # DATA AUDIT
    # =========================
    with st.expander("🔍 Data Quality & Audit Logs"):

        c1, c2 = st.columns(2)

        c1.write(f"Duplicate Records: {df.duplicated().sum()}")
        c2.write(f"Missing Booking Value: {df['Booking Value'].isna().sum()}")

        st.info("Missing values are expected for cancelled rides")
        st.success("Executive Dashboard Rendered Successfully")

if current_page == "Ride Analytics":

    # =========================
    # PAGE HEADER
    # =========================
    st.markdown("""
    <div class="exec-title">🚗 Ride Intelligence Dashboard</div>
    <div class="exec-subtitle">Advanced operational flow and revenue analytics</div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    completed = df[df["Booking Status"] == "Completed"]

    COLOR_PALETTE = [
        "#38BDF8",  # sky blue
        "#FBBF24",  # amber
        "#34D399",  # green
        "#F472B6",  # pink
        "#A78BFA",  # purple
        "#F87171",  # red soft
        "#60A5FA"  # light blue
    ]

    # =====================================================
    # 🟦 SUNBURST CHART (CHART CARD)
    # =====================================================
    st.subheader("Revenue Hierarchy")

    fig1 = px.sunburst(
        completed,
        path=["Vehicle Type", "Payment Method"],
        values="Booking Value",
        color="Booking Value",
        color_continuous_scale=["#0b1220", "#38BDF8", "#FBBF24", "#34D399"]
    )

    fig1.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =====================================================
    # 🟦 TREEMAP CHART
    # =====================================================
    st.subheader("Revenue Distribution")

    fig2 = px.treemap(
        completed,
        path=["Vehicle Type", "Payment Method"],
        values="Booking Value",
        color="Booking Value",
        color_continuous_scale=["#0b1220", "#A78BFA", "#38BDF8", "#FBBF24"]
    )

    fig2.update_layout(
        margin=dict(t=10, l=0, r=0, b=0),
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =====================================================
    # 🟦 BOX PLOT CHART
    # =====================================================
    st.subheader("Customer Rating Spread")

    fig3 = px.box(
        completed,
        x="Vehicle Type",
        y="Customer Rating",
        color="Vehicle Type",
        color_discrete_sequence=COLOR_PALETTE
    )

    fig3.update_layout(
        showlegend=False,
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =====================================================
    # 🟦 SANKEY FLOW CHART
    # =====================================================
    st.subheader("Ride Flow Analysis")

    flow = df.groupby(["Vehicle Type", "Booking Status"]).size().reset_index(name="count")

    source_labels = flow["Vehicle Type"].unique().tolist()
    target_labels = flow["Booking Status"].unique().tolist()

    labels = source_labels + target_labels

    source = flow["Vehicle Type"].apply(lambda x: labels.index(x)).tolist()
    target = flow["Booking Status"].apply(lambda x: labels.index(x)).tolist()
    value = flow["count"].tolist()

    import plotly.graph_objects as go

    node_colors = ["#2563eb"] * len(source_labels) + ["#38bdf8"] * len(target_labels)

    link_colors = [
        "rgba(56,189,248,0.4)" if status == "Completed"
        else "rgba(148,163,184,0.25)"
        for status in flow["Booking Status"]
    ]

    fig4 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=18,
            line=dict(color="rgba(255,255,255,0.1)", width=0.5),
            label=labels,
            color=node_colors[:len(labels)]
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors
        )
    )])

    fig4.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if current_page == "Data Assistant":

    # =========================
    # PAGE TITLE (SAAS STYLE)
    # =========================
    st.markdown("""
    <div class="exec-title">🤖 Data Assistant</div>
    <div class="exec-subtitle">Ask questions and get instant analytics insights</div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    # =========================
    # INPUT CARD
    # =========================
    user_question = st.text_input("Ask Your Question")

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # LOGIC START
    # =========================
    if user_question:

        q = user_question.lower()
        completed = df[df["Booking Status"] == "Completed"]

        # =====================================================
        # 🚗 TOTAL RIDES
        # =====================================================
        if "total rides" in q:

            total = len(df)

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Rides</div>
                <div class="kpi-value">{total}</div>
            </div>
            """, unsafe_allow_html=True)

            user = st.checkbox("Show Visualization")

            if user:
                status = df["Booking Status"].value_counts()

                fig = px.bar(
                    x=status.index,
                    y=status.values,
                    labels={"x": "Booking Status", "y": "Ride Counts"},
                    title="Ride Distribution by Status"
                )

                st.markdown('<div class="divider">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # 💰 REVENUE
        # =====================================================
        elif "revenue" in q:

            revenue = completed.groupby("Vehicle Type")["Booking Value"].sum()

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Revenue</div>
                <div class="kpi-value">₹{revenue.sum():,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

            user = st.checkbox("Show Visualization")

            if user:
                fig = px.bar(
                    x=revenue.index,
                    y=revenue.values,
                    title="Revenue by Vehicle Type",
                    labels={"x": "Vehicle Type", "y": "Revenue"}
                )

                st.markdown('<div class="divider">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # 🚗 VEHICLE USAGE
        # =====================================================
        elif "vehicle" in q:

            vehicle = df["Vehicle Type"].value_counts()

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Most Used Vehicle</div>
                <div class="kpi-value">{vehicle.idxmax()}</div>
            </div>
            """, unsafe_allow_html=True)

            user = st.checkbox("Show Visualization")

            if user:
                fig = px.pie(
                    names=vehicle.index,
                    values=vehicle.values,
                    title="Vehicle Usage Distribution"
                )

                st.markdown('<div class="divider">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # 💳 PAYMENT ANALYSIS
        # =====================================================
        elif "payment" in q:

            payment = completed["Payment Method"].value_counts()

            user = st.checkbox("Show Visualization")

            if user:
                fig = px.pie(
                    names=payment.index,
                    values=payment.values,
                    title="Payment Method Distribution"
                )

                st.markdown('<div class="divider">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # ❌ CANCELLATION
        # =====================================================
        elif "cancel" in q:

            cancel = df["Booking Status"].value_counts()

            user = st.checkbox("Show Visualization")

            if user:
                fig = px.bar(
                    x=cancel.index,
                    y=cancel.values,
                    title="Ride Status Distribution",
                    labels={"x": "Status", "y": "Count"}
                )

                st.markdown('<div class="divider">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # ⭐ RATING
        # =====================================================
        elif "rating" in q:

            avg_rating = completed["Customer Rating"].mean()

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Average Rating</div>
                <div class="kpi-value">{avg_rating:.2f} ⭐</div>
            </div>
            """, unsafe_allow_html=True)

            user = st.checkbox("Show Visualization")

            if user:
                fig = px.histogram(
                    completed,
                    x="Customer Rating",
                    nbins=10,
                    title="Customer Rating Distribution"
                )

                st.markdown('<div class="divider">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # 📏 DISTANCE
        # =====================================================
        elif "distance" in q:

            avg_distance = completed["Ride Distance"].mean()

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Average Distance</div>
                <div class="kpi-value">{avg_distance:.2f} km</div>
            </div>
            """, unsafe_allow_html=True)

            user = st.checkbox("Show Visualization")

            if user:
                fig = px.scatter(
                    completed,
                    x="Ride Distance",
                    y="Booking Value",
                    color="Vehicle Type",
                    title="Distance vs Revenue"
                )

                st.markdown('<div class="divider">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # ❗ DEFAULT
        # =====================================================
        else:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-title">Result</div>
                <div class="kpi-value">Question not recognized</div>
            </div>
            """, unsafe_allow_html=True)

            st.warning("Try asking: revenue, total rides, vehicle, payment, rating, distance")

if current_page == "Chatbot":

    # =========================
    # PAGE TITLE
    # =========================
    st.markdown("""
    <div class="exec-title">🚖 AI Data Chatbot</div>
    <div class="exec-subtitle">Ask insights about Uber operations in natural language</div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    # =========================
    # SIDEBAR CONTROLS
    # =========================
    with st.sidebar:
        st.markdown("### 🤖 Chat Controls")

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # =========================
    # API CHECK
    # =========================
    if not GROQ_API_KEY:
        st.error("Add your Groq API Key")
        st.stop()

    client = Groq(api_key=GROQ_API_KEY)

    # =========================
    # DATA CONTEXT
    # =========================
    completed = df[df["Booking Status"] == "Completed"]

    data_summary = f"""
Uber Business Overview:

Total Rides: {len(df)}
Completed Rides: {len(completed)}
Revenue: ₹{completed["Booking Value"].sum():,.2f}
Avg Distance: {completed["Ride Distance"].mean():.2f} km
Avg Rating: {completed["Customer Rating"].mean():.2f}/5
"""

    # =========================
    # SYSTEM PROMPT
    # =========================
    SYSTEM_PROMPT = {
        "role": "system",
        "content": f"""
You are a smart Uber data analyst.

Rules:
- No code
- Simple human explanation
- Short answers
- Always give insight (WHY)

Data:
{data_summary}
"""
    }

    # =========================
    # SESSION MEMORY INIT
    # =========================
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # =========================
    # CHAT HISTORY DISPLAY
    # =========================
    for msg in st.session_state.messages:
        with st.chat_message(
            msg["role"],
            avatar="🧑" if msg["role"] == "user" else "🤖"
        ):
            st.markdown(msg["content"])

    # =========================
    # USER INPUT
    # =========================
    prompt = st.chat_input("Ask about Uber data...")

    if prompt:

        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        # =========================
        # AI RESPONSE
        # =========================
        with st.chat_message("assistant", avatar="🤖"):
            try:
                chat_history = [SYSTEM_PROMPT] + st.session_state.messages[-8:]

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=chat_history,
                    temperature=0.7,
                    max_tokens=400,
                    stream=True
                )

                placeholder = st.empty()
                full_response = ""

                for chunk in response:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        placeholder.markdown(full_response)

                # Save AI response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

            except Exception as e:
                st.error(f"Error: {e}")

if current_page == "Dashboard":

    st.markdown("""
    <div class="exec-title">📊 User Data Analytics Dashboard</div>
    <div class="exec-subtitle">Business performance, revenue flow & operational intelligence</div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    completed = df[df["Booking Status"] == "Completed"]

    c1,c2 = st.columns([5,5])

    # =====================================================
    # 📦 VEHICLE BOOKINGS
    # =====================================================
    with c1:
        total_booking = completed["Vehicle Type"].value_counts()

        fig = px.bar(
            x=total_booking.index,
            y=total_booking.values,
            title="Vehicle Type By Total Bookings",
            labels={"x": "Vehicle Type", "y": "Total Booking"},
            color=total_booking.values,
            color_continuous_scale=["#0a0f1a", "#1e3a8a", "#2563eb"]
        )

        fig.update_layout(
            paper_bgcolor="#0a0f1a",
            plot_bgcolor="#0a0f1a",
            font_color="white",
            margin=dict(l=10, r=10, t=40, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # 📊 STATUS DISTRIBUTION
    # =====================================================
    with c2:
        status = df["Booking Status"].value_counts()

        fig = px.pie(
            names=status.index,
            values=status.values,
            title="Booking Status Distribution",
            color=status.index,
            color_discrete_map={
                "Completed": "#2ecc71",
                "Cancelled": "#e74c3c",
                "Cancelled by Customer": "#f1c40f",
                "Cancelled by Driver": "#e67e22",
                "No Driver": "#95a5a6"
            }
        )

        fig.update_layout(
            paper_bgcolor="#0a0f1a",
            font_color="white"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)

    # =====================================================
    # 💰 REVENUE BY VEHICLE
    # =====================================================
    with c3:
        revenue = completed.groupby("Vehicle Type")["Booking Value"].sum().sort_values(ascending=True)

        fig = px.bar(
            x=revenue.values,
            y=revenue.index,
            title="Revenue by Vehicle Type",
            orientation='h',
            color=revenue.values,
            color_continuous_scale=["#0a0f1a", "#ffb74d", "#ef6c00"]
        )

        fig.update_layout(
            paper_bgcolor="#0a0f1a",
            plot_bgcolor="#0a0f1a",
            font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # 💳 PAYMENT METHOD
    # =====================================================
    with c4:
        pay = (completed["Payment Method"].value_counts(normalize=True) * 100)

        fig = px.pie(
            names=pay.index,
            values=pay.values,
            hole=0.4,
            title="Payment Method Usage"
        )

        fig.update_layout(
            paper_bgcolor="#0a0f1a",
            font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =====================================================
    # 📍 SCATTER: DISTANCE vs VALUE
    # =====================================================
    fig = px.scatter(
        completed,
        x="Ride Distance",
        y="Booking Value",
        color="Vehicle Type",
        title="Ride Distance vs Booking Values",
        color_discrete_map={
            "Mini": "#2563eb",
            "Bike": "#38bdf8",
            "Auto": "#1e3a8a",
            "Sedan": "#60a5fa",
            "Uber XL": "#93c5fd"
        }
    )

    fig.update_traces(
        marker=dict(opacity=0.85, line=dict(width=0.6, color="white"))
    )

    fig.update_layout(
        paper_bgcolor="#0a0f1a",
        plot_bgcolor="#0a0f1a",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    c5, c6 = st.columns(2)

    # =====================================================
    # ⭐ RATING DISTRIBUTION
    # =====================================================
    with c5:
        fig = px.histogram(
            completed,
            x="Customer Rating",
            nbins=10,
            title="Customer Rating Distribution",
            color_discrete_sequence=["#2ecc71"]
        )

        fig.update_layout(
            paper_bgcolor="#0a0f1a",
            plot_bgcolor="#0a0f1a",
            font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # 📏 DISTANCE ANALYSIS
    # =====================================================
    with c6:
        distance = df.groupby("Vehicle Type")["Ride Distance"].mean()

        fig = px.bar(
            x=distance.index,
            y=distance.values,
            title="Average Distance by Vehicle Type",
            color=distance.values,
            color_continuous_scale=["#0a0f1a", "#66bb6a", "#1b5e20"]
        )

        fig.update_layout(
            paper_bgcolor="#0a0f1a",
            plot_bgcolor="#0a0f1a",
            font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =====================================================
    # ❌ CANCELLATION ANALYSIS
    # =====================================================
    cust_reason = df["Reason for cancelling by Customer"].dropna().value_counts().head(4)
    drv_reason = df["Driver Cancellation Reason"].dropna().value_counts().head(4)
    reason = pd.concat([cust_reason, drv_reason])

    fig = px.bar(
        x=reason.values,
        y=reason.index,
        orientation='h',
        title="Cancellation Reasons Analysis",
        color=reason.index
    )

    fig.update_layout(
        paper_bgcolor="#0a0f1a",
        plot_bgcolor="#0a0f1a",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =====================================================
    # 💵 BOOKING VALUE DISTRIBUTION
    # =====================================================
    fig = px.histogram(
        completed,
        x="Booking Value",
        nbins=12,
        title="Booking Value Distribution",
        color_discrete_sequence=["#ff7f0e"]
    )

    fig.update_layout(
        paper_bgcolor="#0a0f1a",
        plot_bgcolor="#0a0f1a",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # =====================================================
    # ⚙️ OPERATIONAL EFFICIENCY
    # =====================================================
    eff = df.groupby("Vehicle Type")[["Avg VTAT", "Avg CTAT"]].mean().reset_index()

    fig = px.scatter(
        eff,
        x="Avg VTAT",
        y="Avg CTAT",
        size="Avg CTAT",
        color="Vehicle Type",
        title="Operational Efficiency (VTAT vs CTAT)"
    )

    fig.update_layout(
        paper_bgcolor="#0a0f1a",
        plot_bgcolor="#0a0f1a",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
