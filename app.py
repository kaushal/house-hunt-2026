import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="House Hunt 2026",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Color palette & chart theme
# ---------------------------------------------------------------------------

COLORS = {
    "bg": "#0e1117",
    "card": "#1a1d23",
    "card_border": "#2a2d35",
    "accent": "#c9a962",
    "accent_dim": "#a08839",
    "text": "#e8e6e1",
    "text_muted": "#8a8780",
    "green": "#4ade80",
    "red": "#f87171",
    "blue": "#60a5fa",
    "purple": "#a78bfa",
    "orange": "#fb923c",
    "chart_bg": "rgba(0,0,0,0)",
    "grid": "#1f2229",
}

CHART_COLORS = [COLORS["accent"], COLORS["blue"], COLORS["purple"]]

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=COLORS["chart_bg"],
    plot_bgcolor=COLORS["chart_bg"],
    font=dict(family="Inter, system-ui, sans-serif", color=COLORS["text_muted"], size=12),
    xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
    yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], tickformat="$,.0f"),
    legend=dict(orientation="h", y=1.08, font=dict(size=11)),
    margin=dict(l=0, r=0, t=30, b=0),
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---- Global ---- */
html, body, .stApp {
    background: #0e1117;
    color: #e8e6e1;
    font-family: 'Inter', system-ui, sans-serif;
}

/* Kill streamlit defaults */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 1400px; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: #13161c !important;
    border-right: 1px solid #2a2d35 !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label {
    color: #8a8780 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.02em;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #c9a962 !important;
    font-weight: 600 !important;
}

/* ---- Slider tracks ---- */
div[data-testid="stSlider"] > div > div > div > div {
    background: #c9a962 !important;
}

/* ---- Cards ---- */
.prop-card {
    background: #1a1d23;
    border: 1px solid #2a2d35;
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.2s;
}
.prop-card:hover {
    border-color: #c9a962;
}
.prop-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}
.prop-card-body {
    padding: 1rem 1.2rem 1.2rem;
}
.prop-card-body h3 {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e8e6e1;
    margin: 0 0 0.3rem;
    line-height: 1.3;
}
.prop-card-body .neighborhood {
    font-size: 0.78rem;
    color: #c9a962;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
    margin-bottom: 0.6rem;
}
.prop-card-body .details {
    font-size: 0.85rem;
    color: #8a8780;
    line-height: 1.6;
}
.prop-card-body .price {
    font-size: 1.25rem;
    font-weight: 700;
    color: #e8e6e1;
    margin: 0.6rem 0 0.2rem;
}
.prop-card-body .ppsf {
    font-size: 0.78rem;
    color: #8a8780;
}
.prop-card-body .badge {
    display: inline-block;
    background: rgba(201,169,98,0.15);
    color: #c9a962;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 500;
    margin-top: 0.6rem;
}
.prop-card-body a.se-link {
    display: inline-block;
    margin-top: 0.7rem;
    font-size: 0.8rem;
    color: #60a5fa;
    text-decoration: none;
    font-weight: 500;
}
.prop-card-body a.se-link:hover {
    text-decoration: underline;
}

/* ---- Metric cards ---- */
div[data-testid="stMetric"] {
    background: #1a1d23;
    border: 1px solid #2a2d35;
    border-radius: 10px;
    padding: 0.9rem 1rem;
}
div[data-testid="stMetric"] label {
    color: #8a8780 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #e8e6e1 !important;
    font-weight: 600 !important;
    font-size: 1.15rem !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}

/* ---- Tabs ---- */
button[data-baseweb="tab"] {
    color: #8a8780 !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em;
    padding-bottom: 0.7rem !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #c9a962 !important;
    border-bottom-color: #c9a962 !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: #c9a962 !important;
}
div[data-baseweb="tab-border"] {
    background-color: #2a2d35 !important;
}

/* ---- Section headers ---- */
.section-head {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #8a8780;
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #2a2d35;
}

/* ---- Cost breakdown bar ---- */
.cost-bar {
    display: flex;
    border-radius: 6px;
    overflow: hidden;
    height: 28px;
    margin: 0.5rem 0 0.3rem;
    font-size: 0.7rem;
    font-weight: 500;
}
.cost-bar > div { display: flex; align-items: center; justify-content: center; color: #0e1117; }
.cost-mortgage { background: #c9a962; }
.cost-tax { background: #60a5fa; }
.cost-hoa { background: #a78bfa; }
.cost-legend {
    font-size: 0.75rem;
    color: #8a8780;
    margin-top: 0.15rem;
}

/* ---- Dataframe ---- */
div[data-testid="stDataFrame"] {
    border: 1px solid #2a2d35;
    border-radius: 10px;
    overflow: hidden;
}

/* ---- Dividers ---- */
hr { border-color: #2a2d35 !important; }

/* ---- Toggle ---- */
div[data-testid="stToggle"] label span {
    color: #8a8780 !important;
}

/* ---- Hide image fullscreen buttons ---- */
button[title="View fullscreen"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Property data
# ---------------------------------------------------------------------------

PROPERTIES = {
    "319 Schermerhorn St 11B": {
        "address": "319 Schermerhorn St, Unit 11B",
        "neighborhood": "Downtown Brooklyn",
        "price": 1_325_000,
        "beds": 2,
        "baths": 2,
        "sqft": 1_049,
        "year_built": 2017,
        "taxes_monthly": 424,
        "common_charges_monthly": 2_124,
        "min_down_pct": 20,
        "type": "Condo",
        "condition": "Excellent",
        "amenities": "Corner Unit, Doorman, Concierge, Gym, Roof Deck, W/D in Unit, Central AC",
        "price_history": [
            ("04/2018", 1_380_443),
            ("04/2018", 1_353_210),
            ("08/2025", 1_375_000),
            ("10/2025", 1_375_000),
            ("01/2026", 1_325_000),
        ],
        "tax_abatement_note": "7+ years remaining tax abatement",
        "image": "images/schermerhorn.png",
        "streeteasy": "https://streeteasy.com/building/the-nevins/11b",
    },
    "906 Bergen St 1A": {
        "address": "906 Bergen St, Unit 1A",
        "neighborhood": "Crown Heights",
        "price": 1_350_000,
        "beds": 2,
        "baths": 2,
        "sqft": 1_025,
        "year_built": 2021,
        "taxes_monthly": 1_548,
        "common_charges_monthly": 1_000,
        "min_down_pct": 0,
        "type": "Condo",
        "condition": "Excellent",
        "amenities": "Ground Floor, Patio, Concierge, Gym, Roof Deck, Elevator, Central AC, Playroom",
        "price_history": [
            ("04/2021", 1_295_000),
            ("09/2021", 1_295_000),
            ("11/2021", 1_295_000),
            ("01/2026", 1_350_000),
        ],
        "tax_abatement_note": None,
        "image": "images/bergen.png",
        "streeteasy": "https://streeteasy.com/building/906-bergen-street-brooklyn/1a",
    },
    "365 Bridge St 23B": {
        "address": "365 Bridge St, Unit 23B",
        "neighborhood": "Downtown Brooklyn",
        "price": 1_400_000,
        "beds": 2,
        "baths": 2,
        "sqft": 1_186,
        "year_built": 1929,
        "taxes_monthly": 1_575,
        "common_charges_monthly": 1_918,
        "min_down_pct": 10,
        "type": "Condo",
        "condition": "Excellent",
        "amenities": "Penthouse, Top Floor, Doorman, Concierge, Gym, Roof Deck, Yoga, Billiards, Landmark Art Deco",
        "price_history": [
            ("05/2014", 1_132_100),
            ("10/2020", 1_400_000),
            ("12/2020", 1_400_000),
            ("03/2021", 1_400_000),
            ("01/2026", 1_400_000),
        ],
        "tax_abatement_note": None,
        "image": "images/bridge.png",
        "streeteasy": "https://streeteasy.com/property/1440352-belltel-lofts-23b",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def monthly_mortgage(principal: float, annual_rate_pct: float, years: int) -> float:
    if annual_rate_pct == 0:
        return principal / (years * 12)
    r = annual_rate_pct / 100 / 12
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def amortization_schedule(principal: float, annual_rate_pct: float, years: int):
    r = annual_rate_pct / 100 / 12 if annual_rate_pct else 0
    n = years * 12
    payment = monthly_mortgage(principal, annual_rate_pct, years)
    balances, principals, interests, equity_list = [], [], [], []
    balance = principal
    for m in range(1, n + 1):
        interest = balance * r
        princ = payment - interest
        balance -= princ
        balances.append(max(balance, 0))
        principals.append(princ)
        interests.append(interest)
        equity_list.append(principal - max(balance, 0))
    return balances, principals, interests, equity_list


def appreciation_series(price: float, annual_pct: float, years: int):
    monthly_r = (1 + annual_pct / 100) ** (1 / 12) - 1
    return [price * (1 + monthly_r) ** m for m in range(years * 12 + 1)]


def styled_chart(fig, height=420):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    return fig


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1rem;">
        <span style="font-size:1.3rem;font-weight:700;color:#c9a962;letter-spacing:-0.02em;">House Hunt</span>
        <span style="font-size:0.75rem;color:#8a8780;margin-left:0.4rem;">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-head">Loan Parameters</div>', unsafe_allow_html=True)
    interest_rate = st.slider("Interest Rate (%)", 3.0, 10.0, 6.75, 0.125)
    loan_term = st.selectbox("Loan Term (years)", [30, 25, 20, 15], index=0)

    st.markdown('<div class="section-head">Market Assumptions</div>', unsafe_allow_html=True)
    appreciation_rate = st.slider("Annual Appreciation (%)", -5.0, 10.0, 3.0, 0.25)
    projection_years = st.slider("Projection Horizon (years)", 5, 30, 10, 1)

    st.markdown('<div class="section-head">Down Payment</div>', unsafe_allow_html=True)
    down_pcts = {}
    for name, prop in PROPERTIES.items():
        default = max(prop["min_down_pct"], 20)
        down_pcts[name] = st.slider(
            f"{name}",
            min_value=prop["min_down_pct"],
            max_value=100,
            value=default,
            step=1,
            format="%d%%",
            key=f"down_{name}",
        )

    st.markdown('<div class="section-head">Display</div>', unsafe_allow_html=True)
    show_amort = st.toggle("Amortization Breakdown", value=True)
    show_comparison = st.toggle("Side-by-Side Comparison", value=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("""
<div style="margin-bottom:1.8rem;">
    <h1 style="font-size:1.8rem;font-weight:700;color:#e8e6e1;margin:0;letter-spacing:-0.03em;">
        Brooklyn Condo Projections
    </h1>
    <p style="font-size:0.82rem;color:#8a8780;margin:0.25rem 0 0;">
        Comparing 3 units from today's tour &mdash; adjust rates & down payment in the sidebar
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Property cards (HTML)
# ---------------------------------------------------------------------------

card_cols = st.columns(3, gap="medium")
for idx, (name, prop) in enumerate(PROPERTIES.items()):
    with card_cols[idx]:
        badge_html = ""
        if prop.get("tax_abatement_note"):
            badge_html = f'<div class="badge">{prop["tax_abatement_note"]}</div>'
        st.markdown('<div class="prop-card">', unsafe_allow_html=True)
        st.image(prop["image"], use_container_width=True)
        st.markdown(f"""
        <div class="prop-card-body">
            <div class="neighborhood">{prop['neighborhood']}</div>
            <h3>{prop['address']}</h3>
            <div class="details">
                {prop['beds']} bed &middot; {prop['baths']} bath &middot; {prop['sqft']:,} SF &middot; Built {prop['year_built']}
            </div>
            <div class="price">${prop['price']:,.0f}</div>
            <div class="ppsf">${prop['price']/prop['sqft']:,.0f} / SF</div>
            {badge_html}
        </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"[View on StreetEasy →]({prop['streeteasy']})")

# ---------------------------------------------------------------------------
# Per-property tabs
# ---------------------------------------------------------------------------

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
tabs = st.tabs([name for name in PROPERTIES])

for tab, (name, prop) in zip(tabs, PROPERTIES.items()):
    with tab:
        price = prop["price"]
        down_pct = down_pcts[name]
        down_payment = price * down_pct / 100
        loan_amount = price - down_payment
        monthly_pmt = monthly_mortgage(loan_amount, interest_rate, loan_term)
        taxes = prop["taxes_monthly"]
        hoa = prop["common_charges_monthly"]
        total_monthly = monthly_pmt + taxes + hoa

        # ---- Header row with image ----
        img_col, detail_col = st.columns([1, 2], gap="large")
        with img_col:
            st.image(prop["image"], use_container_width=True)
            st.markdown(f"[StreetEasy Listing →]({prop['streeteasy']})")
        with detail_col:
            st.markdown(f"""
            <div style="margin-top:0.3rem;">
                <div style="font-size:0.72rem;color:#c9a962;text-transform:uppercase;letter-spacing:0.08em;font-weight:500;">
                    {prop['neighborhood']}
                </div>
                <h2 style="font-size:1.3rem;font-weight:700;color:#e8e6e1;margin:0.2rem 0 0.4rem;letter-spacing:-0.02em;">
                    {prop['address']}
                </h2>
                <p style="font-size:0.85rem;color:#8a8780;line-height:1.6;margin:0;">
                    {prop['beds']} bed &middot; {prop['baths']} bath &middot; {prop['sqft']:,} SF &middot; Built {prop['year_built']}<br/>
                    {prop['amenities']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # ---- Metrics ----
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Down Payment", f"${down_payment:,.0f}", f"{down_pct}%")
        c2.metric("Loan Amount", f"${loan_amount:,.0f}")
        c3.metric("Monthly Mortgage", f"${monthly_pmt:,.0f}")
        c4.metric("Total Monthly", f"${total_monthly:,.0f}")

        # ---- Cost breakdown bar ----
        mort_pct = monthly_pmt / total_monthly * 100
        tax_pct = taxes / total_monthly * 100
        hoa_pct = hoa / total_monthly * 100
        st.markdown(f"""
        <div class="cost-bar">
            <div class="cost-mortgage" style="width:{mort_pct:.1f}%">Mortgage ${monthly_pmt:,.0f}</div>
            <div class="cost-tax" style="width:{tax_pct:.1f}%">Tax ${taxes:,}</div>
            <div class="cost-hoa" style="width:{hoa_pct:.1f}%">HOA ${hoa:,}</div>
        </div>
        <div class="cost-legend">
            ${total_monthly:,.0f}/mo &middot; ${total_monthly*12:,.0f}/yr
        </div>
        """, unsafe_allow_html=True)

        # ---- Appreciation projection ----
        st.markdown('<div class="section-head">Value & Equity Projection</div>', unsafe_allow_html=True)

        values = appreciation_series(price, appreciation_rate, projection_years)
        balances, _, _, _ = amortization_schedule(loan_amount, interest_rate, loan_term)
        months = list(range(projection_years * 12 + 1))
        bal_padded = [loan_amount] + balances[: projection_years * 12]
        while len(bal_padded) < len(months):
            bal_padded.append(0)
        total_equity = [v - b for v, b in zip(values, bal_padded)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[m / 12 for m in months], y=values,
            name="Property Value", line=dict(width=2.5, color=COLORS["accent"]),
        ))
        fig.add_trace(go.Scatter(
            x=[m / 12 for m in months], y=bal_padded,
            name="Loan Balance", line=dict(width=1.5, dash="dash", color=COLORS["red"]),
        ))
        fig.add_trace(go.Scatter(
            x=[m / 12 for m in months], y=total_equity,
            name="Total Equity",
            line=dict(width=0, color=COLORS["green"]),
            fill="tozeroy",
            fillcolor="rgba(74,222,128,0.12)",
        ))
        fig.update_layout(xaxis_title="Years")
        st.plotly_chart(styled_chart(fig, 400), use_container_width=True)

        # Milestones
        yr5_val = values[min(60, len(values) - 1)]
        yr10_val = values[min(120, len(values) - 1)]
        yr5_eq = total_equity[min(60, len(total_equity) - 1)]
        yr10_eq = total_equity[min(120, len(total_equity) - 1)]

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Value @ 5yr", f"${yr5_val:,.0f}", f"{(yr5_val/price - 1)*100:+.1f}%")
        mc2.metric("Equity @ 5yr", f"${yr5_eq:,.0f}")
        if projection_years >= 10:
            mc3.metric("Value @ 10yr", f"${yr10_val:,.0f}", f"{(yr10_val/price - 1)*100:+.1f}%")
            mc4.metric("Equity @ 10yr", f"${yr10_eq:,.0f}")

        # ---- Amortization ----
        if show_amort:
            st.markdown('<div class="section-head">Amortization Breakdown</div>', unsafe_allow_html=True)
            _, princ_arr, int_arr, _ = amortization_schedule(loan_amount, interest_rate, loan_term)
            amort_months = list(range(1, min(projection_years * 12, len(princ_arr)) + 1))

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=[m / 12 for m in amort_months],
                y=[int_arr[m - 1] for m in amort_months],
                name="Interest", marker_color=COLORS["red"],
            ))
            fig2.add_trace(go.Bar(
                x=[m / 12 for m in amort_months],
                y=[princ_arr[m - 1] for m in amort_months],
                name="Principal", marker_color=COLORS["green"],
            ))
            fig2.update_layout(barmode="stack", xaxis_title="Years", yaxis_title="$/month")
            st.plotly_chart(styled_chart(fig2, 320), use_container_width=True)

        # ---- Price history ----
        st.markdown('<div class="section-head">Listing Price History</div>', unsafe_allow_html=True)
        hist = prop["price_history"]
        hist_df = pd.DataFrame(hist, columns=["Date", "Price"])
        fig3 = go.Figure(go.Scatter(
            x=hist_df["Date"], y=hist_df["Price"],
            mode="lines+markers",
            line=dict(width=2, color=COLORS["accent"]),
            marker=dict(size=7, color=COLORS["accent"]),
        ))
        st.plotly_chart(styled_chart(fig3, 260), use_container_width=True)

# ---------------------------------------------------------------------------
# Side-by-side comparison
# ---------------------------------------------------------------------------

if show_comparison:
    st.markdown('<div class="section-head" style="margin-top:2rem;">Side-by-Side Comparison</div>', unsafe_allow_html=True)

    rows = []
    for name, prop in PROPERTIES.items():
        price = prop["price"]
        dp = down_pcts[name]
        down = price * dp / 100
        loan = price - down
        mpmt = monthly_mortgage(loan, interest_rate, loan_term)
        taxes = prop["taxes_monthly"]
        hoa = prop["common_charges_monthly"]
        total = mpmt + taxes + hoa
        val5 = appreciation_series(price, appreciation_rate, 5)[60]
        val10 = appreciation_series(price, appreciation_rate, 10)[120]
        bal5 = amortization_schedule(loan, interest_rate, loan_term)[0][min(59, loan_term * 12 - 1)]
        bal10 = amortization_schedule(loan, interest_rate, loan_term)[0][min(119, loan_term * 12 - 1)]

        rows.append({
            "Property": prop["address"],
            "Neighborhood": prop["neighborhood"],
            "Price": f"${price:,.0f}",
            "$/SF": f"${price/prop['sqft']:,.0f}",
            "Down Payment": f"${down:,.0f} ({dp}%)",
            "Monthly Mortgage": f"${mpmt:,.0f}",
            "Taxes/mo": f"${taxes:,}",
            "HOA/mo": f"${hoa:,}",
            "Total Monthly": f"${total:,.0f}",
            "Total Annual": f"${total*12:,.0f}",
            "Value @ 5yr": f"${val5:,.0f}",
            "Equity @ 5yr": f"${val5-bal5:,.0f}",
            "Value @ 10yr": f"${val10:,.0f}",
            "Equity @ 10yr": f"${val10-bal10:,.0f}",
            "Total Paid 5yr": f"${total*60:,.0f}",
            "Total Paid 10yr": f"${total*120:,.0f}",
        })

    df = pd.DataFrame(rows).set_index("Property").T
    st.dataframe(df, use_container_width=True, height=620)

    # ---- Overlay charts ----
    chart_cols = st.columns(2, gap="large")

    with chart_cols[0]:
        st.markdown('<div class="section-head">Value Appreciation</div>', unsafe_allow_html=True)
        fig_comp = go.Figure()
        for i, (name, prop) in enumerate(PROPERTIES.items()):
            vals = appreciation_series(prop["price"], appreciation_rate, projection_years)
            fig_comp.add_trace(go.Scatter(
                x=[m / 12 for m in range(len(vals))], y=vals,
                name=name, line=dict(width=2, color=CHART_COLORS[i]),
            ))
        fig_comp.update_layout(xaxis_title="Years")
        st.plotly_chart(styled_chart(fig_comp, 380), use_container_width=True)

    with chart_cols[1]:
        st.markdown('<div class="section-head">Total Equity</div>', unsafe_allow_html=True)
        fig_eq = go.Figure()
        for i, (name, prop) in enumerate(PROPERTIES.items()):
            price = prop["price"]
            dp = down_pcts[name]
            loan = price - price * dp / 100
            vals = appreciation_series(price, appreciation_rate, projection_years)
            bals = [loan] + list(amortization_schedule(loan, interest_rate, loan_term)[0][: projection_years * 12])
            while len(bals) < len(vals):
                bals.append(0)
            eq = [v - b for v, b in zip(vals, bals)]
            fig_eq.add_trace(go.Scatter(
                x=[m / 12 for m in range(len(eq))], y=eq,
                name=name, line=dict(width=2, color=CHART_COLORS[i]),
            ))
        fig_eq.update_layout(xaxis_title="Years")
        st.plotly_chart(styled_chart(fig_eq, 380), use_container_width=True)
