import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import io

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Logistics Pickup Tracker",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #0d0f14;
    --surface: #141720;
    --surface2: #1c2030;
    --border: #252a3a;
    --accent: #3b82f6;
    --accent2: #f59e0b;
    --danger: #ef4444;
    --success: #22c55e;
    --text: #e2e8f0;
    --muted: #64748b;
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    padding: 1.5rem 2rem 3rem 2rem;
    max-width: 1400px;
}

/* Header */
.ops-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px 0 24px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
}
.ops-header-icon {
    font-size: 32px;
    line-height: 1;
}
.ops-header-title {
    font-family: var(--mono) !important;
    font-size: 22px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.ops-header-sub {
    font-size: 12px;
    color: var(--muted);
    font-family: var(--mono) !important;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Metric Cards */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
}
.metric-card.warn::before { background: var(--accent2); }
.metric-card.danger::before { background: var(--danger); }
.metric-card.ok::before { background: var(--success); }
.metric-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--muted);
    font-family: var(--mono) !important;
    margin-bottom: 8px;
}
.metric-value {
    font-family: var(--mono) !important;
    font-size: 28px;
    font-weight: 600;
    color: var(--text);
    line-height: 1;
}
.metric-sub {
    font-size: 11px;
    color: var(--muted);
    margin-top: 4px;
}

/* Section headers */
.section-label {
    font-family: var(--mono) !important;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--muted);
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}

/* Form */
.stForm {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 24px !important;
}

/* Inputs */
.stSelectbox > div > div,
.stDateInput > div > div,
.stNumberInput > div > div,
.stTextInput > div > div,
.stTextArea > div > div {
    background-color: var(--surface2) !important;
    border-color: var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
    margin-bottom: 24px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 6px !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

/* Tables */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    padding: 8px 20px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.85 !important;
}

/* Success/Error messages */
.stSuccess { background: #052e16 !important; border: 1px solid #166534 !important; border-radius: 6px !important; }
.stError { background: #1f0b0b !important; border: 1px solid #7f1d1d !important; border-radius: 6px !important; }
.stWarning { background: #1c1500 !important; border: 1px solid #92400e !important; border-radius: 6px !important; }

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
}

/* Filter bar */
.filter-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 20px;
}

/* Tag badge */
.tag {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-family: var(--mono) !important;
    color: var(--muted);
    margin: 2px;
}

/* scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ─────────────────────────────────────────────────────────────────
SELLERS = sorted([
    "swastiks", "sapphire_dry_nuts", "vrd_masale", "bolas", "hugs", "candyfun",
    "bakemate", "zoff_foods", "suruchi_spices", "kesarco", "chuk_de", "somnath",
    "go_desi", "z_magnetism", "sugandh", "kirana_bazaar", "farmkin", "archita",
    "charliee", "sanjeevani", "meera_foods", "tata", "nutraj", "annai",
    "apsara_tea", "pansari", "chaivik", "cookme", "soothe", "sarkar_spices",
    "upl", "mangalam", "savour", "daylight_fargo_manpasand", "maharani",
    "tattvam_luxury_incense", "vimaan", "kc_punji_rewards",
    "kiranaclub_loyalty_rewards", "mantra", "harnik", "rsb_super_stockist",
    "hansha", "hans", "parimal", "gongloo", "yumms", "karnavati_tea_company",
    "blg", "derby", "continental_coffee", "broomify", "milan_supari", "dnv",
    "pickwick", "famis_spices", "desik", "ruby", "chotiwale", "mona", "klaw",
    "kalbavi", "rasna"
])

COURIERS = ["DelhiveryOne", "Ekart", "Shiprocket"]
SR_COURIERS = ["Ekart_SR", "Delhivery_SR", "Xpressbees_SR", "DTDC_SR"]
DB_PATH = "/tmp/logistics_data.db"

# ─── Database ──────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pickups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            seller TEXT NOT NULL,
            courier TEXT NOT NULL,
            shiprocket_courier TEXT,
            orders_ready INTEGER DEFAULT 0,
            orders_picked INTEGER DEFAULT 0,
            not_packed_on_time INTEGER DEFAULT 0,
            pickup_missed INTEGER DEFAULT 0,
            reason_for_delay TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_entry(data: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO pickups
            (entry_date, seller, courier, shiprocket_courier, orders_ready,
             orders_picked, not_packed_on_time, pickup_missed, reason_for_delay)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["entry_date"], data["seller"], data["courier"],
        data.get("shiprocket_courier"), data["orders_ready"],
        data["orders_picked"], data["not_packed_on_time"],
        1 if data["pickup_missed"] else 0, data["reason_for_delay"]
    ))
    conn.commit()
    conn.close()

def load_data() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM pickups ORDER BY entry_date DESC, id DESC", conn)
    conn.close()
    if not df.empty:
        df["entry_date"] = pd.to_datetime(df["entry_date"])
        df["pending_pickup"] = df["orders_ready"] - df["orders_picked"]
    return df

def delete_entry(entry_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM pickups WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

# ─── Init ──────────────────────────────────────────────────────────────────────
init_db()

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ops-header">
    <div class="ops-header-icon">📦</div>
    <div>
        <div class="ops-header-title">Logistics Pickup Tracker</div>
        <div class="ops-header-sub">Operations Control Dashboard · Seller Performance & Courier Monitoring</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋  DAILY DATA ENTRY", "📊  RESULTS DASHBOARD"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA ENTRY
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_form, col_recent = st.columns([1.1, 1], gap="large")

    with col_form:
        st.markdown('<div class="section-label">New Entry</div>', unsafe_allow_html=True)

        with st.form("entry_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                entry_date = st.date_input("📅 Date", value=date.today())
            with c2:
                seller = st.selectbox("🏪 Seller", SELLERS)

            courier = st.selectbox("🚚 Courier", COURIERS)
            sr_courier = None
            if courier == "Shiprocket":
                sr_courier = st.selectbox("↳ Shiprocket Courier", SR_COURIERS)

            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                orders_ready = st.number_input("📦 Orders Ready", min_value=0, step=1, value=0)
                not_packed = st.number_input("⚠️ Not Packed On Time", min_value=0, step=1, value=0)
            with c4:
                orders_picked = st.number_input("✅ Orders Picked Up", min_value=0, step=1, value=0)
                pickup_missed = st.selectbox("❌ Pickup Missed", ["No", "Yes"])

            reason = st.text_area("📝 Reason for Delay", placeholder="Describe the reason (optional)...", height=80)

            submitted = st.form_submit_button("💾  SAVE ENTRY", use_container_width=True)

        if submitted:
            if orders_picked > orders_ready:
                st.error("❌ Orders Picked cannot exceed Orders Ready.")
            else:
                insert_entry({
                    "entry_date": str(entry_date),
                    "seller": seller,
                    "courier": courier,
                    "shiprocket_courier": sr_courier,
                    "orders_ready": orders_ready,
                    "orders_picked": orders_picked,
                    "not_packed_on_time": not_packed,
                    "pickup_missed": pickup_missed == "Yes",
                    "reason_for_delay": reason.strip() if reason.strip() else None
                })
                st.success(f"✅ Entry saved — {seller} · {courier} · {entry_date}")
                st.rerun()

    with col_recent:
        st.markdown('<div class="section-label">Recent Entries (Last 20)</div>', unsafe_allow_html=True)
        df_all = load_data()
        if df_all.empty:
            st.info("No entries yet. Submit your first record on the left.")
        else:
            recent = df_all.head(20)[["id","entry_date","seller","courier","orders_ready","orders_picked","pending_pickup","pickup_missed"]].copy()
            recent["entry_date"] = recent["entry_date"].dt.strftime("%d %b")
            recent["pickup_missed"] = recent["pickup_missed"].map({1:"🔴 Yes", 0:"✅ No"})
            recent.columns = ["ID","Date","Seller","Courier","Ready","Picked","Pending","Missed"]
            st.dataframe(recent, use_container_width=True, hide_index=True, height=420)

        # Delete entry
        if not df_all.empty:
            with st.expander("🗑️ Delete an entry by ID"):
                del_id = st.number_input("Entry ID to delete", min_value=1, step=1, value=int(df_all["id"].iloc[0]))
                if st.button("Delete Entry"):
                    delete_entry(del_id)
                    st.success(f"Deleted entry ID {del_id}")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RESULTS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    df = load_data()

    if df.empty:
        st.info("No data yet. Add entries in the Daily Data Entry tab to see analytics here.")
        st.stop()

    # ── Filters ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Filters</div>', unsafe_allow_html=True)
    with st.container():
        fc1, fc2, fc3, fc4 = st.columns([1.2, 1, 1, 0.8])
        with fc1:
            min_d = df["entry_date"].min().date()
            max_d = df["entry_date"].max().date()
            date_range = st.date_input("Date Range", value=(min_d, max_d), key="filter_date")
        with fc2:
            seller_opts = ["All"] + sorted(df["seller"].unique().tolist())
            filter_seller = st.selectbox("Seller", seller_opts, key="filter_seller")
        with fc3:
            courier_opts = ["All"] + sorted(df["courier"].unique().tolist())
            filter_courier = st.selectbox("Courier", courier_opts, key="filter_courier")
        with fc4:
            st.markdown("<br>", unsafe_allow_html=True)
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, index=False)
            st.download_button("⬇ Export CSV", data=csv_buf.getvalue(),
                               file_name=f"logistics_{date.today()}.csv",
                               mime="text/csv", use_container_width=True)

    # Apply filters
    fdf = df.copy()
    if len(date_range) == 2:
        fdf = fdf[(fdf["entry_date"].dt.date >= date_range[0]) & (fdf["entry_date"].dt.date <= date_range[1])]
    if filter_seller != "All":
        fdf = fdf[fdf["seller"] == filter_seller]
    if filter_courier != "All":
        fdf = fdf[fdf["courier"] == filter_courier]

    if fdf.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    total_ready = int(fdf["orders_ready"].sum())
    total_picked = int(fdf["orders_picked"].sum())
    total_pending = int(fdf["pending_pickup"].sum())
    total_missed = int(fdf["pickup_missed"].sum())
    total_not_packed = int(fdf["not_packed_on_time"].sum())
    pickup_rate = round(total_picked / total_ready * 100, 1) if total_ready > 0 else 0

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card ok">
            <div class="metric-label">Total Orders Ready</div>
            <div class="metric-value">{total_ready:,}</div>
            <div class="metric-sub">across {fdf['seller'].nunique()} sellers</div>
        </div>
        <div class="metric-card ok">
            <div class="metric-label">Orders Picked Up</div>
            <div class="metric-value">{total_picked:,}</div>
            <div class="metric-sub">{pickup_rate}% pickup rate</div>
        </div>
        <div class="metric-card warn">
            <div class="metric-label">Pending Pickup</div>
            <div class="metric-value">{total_pending:,}</div>
            <div class="metric-sub">orders not yet collected</div>
        </div>
        <div class="metric-card danger">
            <div class="metric-label">Missed Pickups</div>
            <div class="metric-value">{total_missed}</div>
            <div class="metric-sub">{total_not_packed} packing delays</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts Row 1 ──────────────────────────────────────────────────────────
    ch1, ch2 = st.columns(2, gap="medium")

    with ch1:
        st.markdown('<div class="section-label">Seller-wise Pending Pickup</div>', unsafe_allow_html=True)
        seller_pending = fdf.groupby("seller")["pending_pickup"].sum().reset_index()
        seller_pending = seller_pending[seller_pending["pending_pickup"] > 0].sort_values("pending_pickup", ascending=False).head(20)
        if not seller_pending.empty:
            fig = px.bar(seller_pending, x="seller", y="pending_pickup",
                         color="pending_pickup", color_continuous_scale=["#1e3a5f","#3b82f6","#93c5fd"],
                         labels={"seller": "", "pending_pickup": "Pending Orders"})
            fig.update_layout(
                plot_bgcolor="#141720", paper_bgcolor="#141720",
                font=dict(family="IBM Plex Mono", color="#94a3b8", size=10),
                coloraxis_showscale=False,
                xaxis=dict(tickangle=-40, gridcolor="#252a3a"),
                yaxis=dict(gridcolor="#252a3a"),
                margin=dict(l=0, r=0, t=10, b=60),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No pending pickups in filtered range.")

    with ch2:
        st.markdown('<div class="section-label">Courier-wise Missed Pickups</div>', unsafe_allow_html=True)
        courier_missed = fdf.groupby("courier")["pickup_missed"].sum().reset_index()
        courier_missed.columns = ["courier", "missed"]
        if courier_missed["missed"].sum() > 0:
            fig2 = px.pie(courier_missed, names="courier", values="missed",
                          color_discrete_sequence=["#3b82f6","#f59e0b","#ef4444","#22c55e"])
            fig2.update_layout(
                plot_bgcolor="#141720", paper_bgcolor="#141720",
                font=dict(family="IBM Plex Mono", color="#94a3b8", size=11),
                legend=dict(bgcolor="#141720", bordercolor="#252a3a"),
                margin=dict(l=0, r=0, t=10, b=10),
                height=300
            )
            fig2.update_traces(textposition="inside", textfont_size=12)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.success("🎉 No missed pickups in the selected range!")

    # ── Charts Row 2 ──────────────────────────────────────────────────────────
    ch3, ch4 = st.columns(2, gap="medium")

    with ch3:
        st.markdown('<div class="section-label">Packing Delays by Seller</div>', unsafe_allow_html=True)
        pack_delays = fdf.groupby("seller")["not_packed_on_time"].sum().reset_index()
        pack_delays = pack_delays[pack_delays["not_packed_on_time"] > 0].sort_values("not_packed_on_time", ascending=True).tail(15)
        if not pack_delays.empty:
            fig3 = px.bar(pack_delays, x="not_packed_on_time", y="seller",
                          orientation="h",
                          color="not_packed_on_time",
                          color_continuous_scale=["#451a03","#f59e0b","#fef3c7"],
                          labels={"not_packed_on_time": "Orders Not Packed On Time", "seller": ""})
            fig3.update_layout(
                plot_bgcolor="#141720", paper_bgcolor="#141720",
                font=dict(family="IBM Plex Mono", color="#94a3b8", size=10),
                coloraxis_showscale=False,
                xaxis=dict(gridcolor="#252a3a"),
                yaxis=dict(gridcolor="#252a3a"),
                margin=dict(l=0, r=0, t=10, b=20),
                height=300
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.success("✅ No packing delays in the selected range.")

    with ch4:
        st.markdown('<div class="section-label">Daily Pending Pickup Trend</div>', unsafe_allow_html=True)
        daily_trend = fdf.groupby("entry_date")[["orders_ready","orders_picked","pending_pickup"]].sum().reset_index()
        daily_trend = daily_trend.sort_values("entry_date")
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=daily_trend["entry_date"], y=daily_trend["orders_ready"],
            name="Ready", line=dict(color="#3b82f6", width=2), mode="lines+markers"
        ))
        fig4.add_trace(go.Scatter(
            x=daily_trend["entry_date"], y=daily_trend["orders_picked"],
            name="Picked", line=dict(color="#22c55e", width=2), mode="lines+markers"
        ))
        fig4.add_trace(go.Scatter(
            x=daily_trend["entry_date"], y=daily_trend["pending_pickup"],
            name="Pending", line=dict(color="#ef4444", width=2, dash="dot"), mode="lines+markers",
            fill="tozeroy", fillcolor="rgba(239,68,68,0.08)"
        ))
        fig4.update_layout(
            plot_bgcolor="#141720", paper_bgcolor="#141720",
            font=dict(family="IBM Plex Mono", color="#94a3b8", size=10),
            legend=dict(bgcolor="#141720", bordercolor="#252a3a", orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(gridcolor="#252a3a"),
            yaxis=dict(gridcolor="#252a3a"),
            margin=dict(l=0, r=0, t=30, b=10),
            height=300
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Tables ────────────────────────────────────────────────────────────────
    t1, t2 = st.columns(2, gap="medium")

    with t1:
        st.markdown('<div class="section-label">Seller Performance Table</div>', unsafe_allow_html=True)
        seller_perf = fdf.groupby("seller").agg(
            Total_Ready=("orders_ready", "sum"),
            Total_Picked=("orders_picked", "sum"),
            Packing_Delays=("not_packed_on_time", "sum"),
            Missed_Pickups=("pickup_missed", "sum"),
        ).reset_index()
        seller_perf["Pending"] = seller_perf["Total_Ready"] - seller_perf["Total_Picked"]
        seller_perf["Pickup_%"] = (seller_perf["Total_Picked"] / seller_perf["Total_Ready"].replace(0, 1) * 100).round(1)
        seller_perf = seller_perf.sort_values("Pending", ascending=False)
        seller_perf.columns = ["Seller","Ready","Picked","Pack Delays","Missed","Pending","Pickup %"]
        st.dataframe(seller_perf, use_container_width=True, hide_index=True, height=320)

    with t2:
        st.markdown('<div class="section-label">Courier Performance Table</div>', unsafe_allow_html=True)
        courier_perf = fdf.groupby("courier").agg(
            Total_Orders=("orders_ready", "sum"),
            Orders_Picked=("orders_picked", "sum"),
            Missed_Pickups=("pickup_missed", "sum"),
            Packing_Delays=("not_packed_on_time", "sum"),
        ).reset_index()
        courier_perf["Pending"] = courier_perf["Total_Orders"] - courier_perf["Orders_Picked"]
        courier_perf["Miss_Rate_%"] = (courier_perf["Missed_Pickups"] / len(fdf) * 100).round(1)
        courier_perf.columns = ["Courier","Total Orders","Picked","Missed","Pack Delays","Pending","Miss Rate %"]
        st.dataframe(courier_perf, use_container_width=True, hide_index=True, height=220)

        # Shiprocket breakdown
        sr_data = fdf[fdf["courier"] == "Shiprocket"]
        if not sr_data.empty and "shiprocket_courier" in sr_data.columns:
            st.markdown('<div class="section-label" style="margin-top:16px">Shiprocket Sub-courier Breakdown</div>', unsafe_allow_html=True)
            sr_breakdown = sr_data.groupby("shiprocket_courier").agg(
                Orders=("orders_ready", "sum"),
                Missed=("pickup_missed", "sum")
            ).reset_index()
            sr_breakdown.columns = ["SR Courier", "Orders", "Missed"]
            st.dataframe(sr_breakdown, use_container_width=True, hide_index=True)

    # ── Root Cause Analysis ───────────────────────────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:8px">Root Cause Analysis — Delay Reasons</div>', unsafe_allow_html=True)
    reasons = fdf[fdf["reason_for_delay"].notna() & (fdf["reason_for_delay"].str.strip() != "")]["reason_for_delay"]
    if not reasons.empty:
        reason_counts = reasons.value_counts().reset_index()
        reason_counts.columns = ["Reason", "Count"]

        rc1, rc2 = st.columns([1, 1.5], gap="medium")
        with rc1:
            st.dataframe(reason_counts, use_container_width=True, hide_index=True)
        with rc2:
            fig5 = px.bar(reason_counts.head(10), x="Count", y="Reason", orientation="h",
                          color="Count", color_continuous_scale=["#1e1b4b","#818cf8","#c7d2fe"],
                          labels={"Reason": "", "Count": "Occurrences"})
            fig5.update_layout(
                plot_bgcolor="#141720", paper_bgcolor="#141720",
                font=dict(family="IBM Plex Mono", color="#94a3b8", size=10),
                coloraxis_showscale=False,
                xaxis=dict(gridcolor="#252a3a"),
                yaxis=dict(gridcolor="#252a3a"),
                margin=dict(l=0, r=0, t=10, b=10),
                height=250
            )
            st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No delay reasons recorded yet.")

    # ── Raw Data ──────────────────────────────────────────────────────────────
    with st.expander("📄 View Raw Data"):
        display_df = fdf.copy()
        display_df["entry_date"] = display_df["entry_date"].dt.strftime("%Y-%m-%d")
        display_df["pickup_missed"] = display_df["pickup_missed"].map({1:"Yes", 0:"No"})
        st.dataframe(display_df.drop(columns=["created_at"], errors="ignore"),
                     use_container_width=True, hide_index=True)
