import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Brooklyn Property Projections", layout="wide")

# ---------------------------------------------------------------------------
# Property data extracted from Toursheet_client.pdf
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
# Helper functions
# ---------------------------------------------------------------------------


def monthly_mortgage(principal: float, annual_rate_pct: float, years: int) -> float:
    """Standard amortization formula."""
    if annual_rate_pct == 0:
        return principal / (years * 12)
    r = annual_rate_pct / 100 / 12
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def amortization_schedule(principal: float, annual_rate_pct: float, years: int):
    """Return month-by-month amortization arrays."""
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
    """Return monthly property values under constant appreciation."""
    monthly_r = (1 + annual_pct / 100) ** (1 / 12) - 1
    return [price * (1 + monthly_r) ** m for m in range(years * 12 + 1)]


# ---------------------------------------------------------------------------
# Sidebar – global inputs
# ---------------------------------------------------------------------------

st.sidebar.title("Mortgage & Market Settings")

interest_rate = st.sidebar.slider("Interest Rate (%)", 3.0, 10.0, 6.75, 0.125)
loan_term = st.sidebar.selectbox("Loan Term (years)", [30, 25, 20, 15], index=0)
appreciation_rate = st.sidebar.slider("Annual Appreciation (%)", -5.0, 10.0, 3.0, 0.25)
projection_years = st.sidebar.slider("Projection Horizon (years)", 5, 30, 10, 1)

st.sidebar.markdown("---")
st.sidebar.subheader("Per-Property Down Payment")
down_pcts = {}
for name, prop in PROPERTIES.items():
    default = max(prop["min_down_pct"], 20)
    down_pcts[name] = st.sidebar.slider(
        f"{name} – Down %",
        min_value=prop["min_down_pct"],
        max_value=100,
        value=default,
        step=1,
        key=f"down_{name}",
    )

st.sidebar.markdown("---")
show_amort = st.sidebar.toggle("Show Amortization Breakdown", value=True)
show_comparison = st.sidebar.toggle("Show Side-by-Side Comparison", value=True)

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------

st.title("Brooklyn Condo Investment Projections")
st.caption("Data from Compass toursheet – 319 Schermerhorn 11B · 906 Bergen 1A · 365 Bridge 23B")

# ---------------------------------------------------------------------------
# Property cards
# ---------------------------------------------------------------------------

cols = st.columns(3)
for idx, (name, prop) in enumerate(PROPERTIES.items()):
    with cols[idx]:
        st.image(prop["image"], use_container_width=True)
        st.subheader(prop["address"])
        st.markdown(f"**{prop['neighborhood']}** · {prop['beds']}BR / {prop['baths']}BA · {prop['sqft']:,} SF")
        st.markdown(f"**Asking Price:** ${prop['price']:,.0f} · **$/SF:** ${prop['price']/prop['sqft']:,.0f}")
        st.markdown(f"Year Built: {prop['year_built']} · {prop['type']}")
        st.markdown(f"[View on StreetEasy]({prop['streeteasy']})")
        if prop.get("tax_abatement_note"):
            st.success(prop["tax_abatement_note"])

# ---------------------------------------------------------------------------
# Per-property detailed tabs
# ---------------------------------------------------------------------------

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

        # ---- Image + link header ----
        img_col, detail_col = st.columns([1, 2])
        with img_col:
            st.image(prop["image"], use_container_width=True)
            st.markdown(f"[View on StreetEasy]({prop['streeteasy']})")
        with detail_col:
            st.markdown(f"### {prop['address']}")
            st.markdown(f"**{prop['neighborhood']}** · {prop['beds']}BR / {prop['baths']}BA · {prop['sqft']:,} SF · Built {prop['year_built']}")
            st.markdown(f"**Amenities:** {prop['amenities']}")

        # ---- Summary metrics ----
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Down Payment", f"${down_payment:,.0f}", f"{down_pct}%")
        c2.metric("Loan Amount", f"${loan_amount:,.0f}")
        c3.metric("Monthly Mortgage", f"${monthly_pmt:,.0f}")
        c4.metric("Total Monthly", f"${total_monthly:,.0f}", f"Tax ${taxes} + HOA ${hoa:,}")

        st.markdown(f"**Carrying cost breakdown:** Mortgage ${monthly_pmt:,.0f} + Taxes ${taxes:,} + Common charges ${hoa:,} = **${total_monthly:,.0f}/mo** (${total_monthly*12:,.0f}/yr)")

        # ---- Appreciation projection ----
        st.markdown("---")
        st.subheader("Property Value & Equity Projection")

        values = appreciation_series(price, appreciation_rate, projection_years)
        balances, _, _, equity_from_payments = amortization_schedule(
            loan_amount, interest_rate, loan_term
        )

        months = list(range(projection_years * 12 + 1))
        # Pad balances if projection < loan term or trim if projection > loan term
        bal_padded = [loan_amount] + balances[: projection_years * 12]
        while len(bal_padded) < len(months):
            bal_padded.append(0)

        total_equity = [v - b for v, b in zip(values, bal_padded)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[m / 12 for m in months], y=values,
            name="Property Value", line=dict(width=3),
        ))
        fig.add_trace(go.Scatter(
            x=[m / 12 for m in months], y=bal_padded,
            name="Loan Balance", line=dict(width=2, dash="dash"),
        ))
        fig.add_trace(go.Scatter(
            x=[m / 12 for m in months], y=total_equity,
            name="Total Equity", fill="tozeroy", opacity=0.3,
        ))
        fig.update_layout(
            xaxis_title="Years", yaxis_title="USD ($)",
            yaxis_tickformat="$,.0f",
            height=420, template="plotly_white",
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Key milestones
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

        # ---- Amortization breakdown ----
        if show_amort:
            st.markdown("---")
            st.subheader("Monthly Payment Breakdown (Amortization)")

            _, princ_arr, int_arr, _ = amortization_schedule(
                loan_amount, interest_rate, loan_term
            )
            amort_months = list(range(1, min(projection_years * 12, len(princ_arr)) + 1))

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=[m / 12 for m in amort_months],
                y=[int_arr[m - 1] for m in amort_months],
                name="Interest",
            ))
            fig2.add_trace(go.Bar(
                x=[m / 12 for m in amort_months],
                y=[princ_arr[m - 1] for m in amort_months],
                name="Principal",
            ))
            fig2.update_layout(
                barmode="stack", xaxis_title="Years", yaxis_title="$/month",
                yaxis_tickformat="$,.0f",
                height=350, template="plotly_white",
                legend=dict(orientation="h", y=1.12),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ---- Price history ----
        st.markdown("---")
        st.subheader("Price History (from listing)")
        hist = prop["price_history"]
        hist_df = pd.DataFrame(hist, columns=["Date", "Price"])
        fig3 = go.Figure(go.Scatter(
            x=hist_df["Date"], y=hist_df["Price"],
            mode="lines+markers", line=dict(width=2),
        ))
        fig3.update_layout(
            yaxis_tickformat="$,.0f", height=280,
            template="plotly_white",
        )
        st.plotly_chart(fig3, use_container_width=True)

# ---------------------------------------------------------------------------
# Side-by-side comparison table
# ---------------------------------------------------------------------------

if show_comparison:
    st.markdown("---")
    st.header("Side-by-Side Comparison")

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
        eq5 = val5 - bal5
        eq10 = val10 - bal10

        total_paid_5yr = total * 60
        total_paid_10yr = total * 120

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
            "Equity @ 5yr": f"${eq5:,.0f}",
            "Value @ 10yr": f"${val10:,.0f}",
            "Equity @ 10yr": f"${eq10:,.0f}",
            "Total Paid 5yr": f"${total_paid_5yr:,.0f}",
            "Total Paid 10yr": f"${total_paid_10yr:,.0f}",
        })

    df = pd.DataFrame(rows).set_index("Property").T
    st.dataframe(df, use_container_width=True, height=620)

    # ---- Overlay comparison chart ----
    st.subheader("Value Appreciation Overlay")
    fig_comp = go.Figure()
    for name, prop in PROPERTIES.items():
        vals = appreciation_series(prop["price"], appreciation_rate, projection_years)
        fig_comp.add_trace(go.Scatter(
            x=[m / 12 for m in range(len(vals))],
            y=vals,
            name=prop["address"],
            line=dict(width=2),
        ))
    fig_comp.update_layout(
        xaxis_title="Years", yaxis_title="Property Value ($)",
        yaxis_tickformat="$,.0f",
        height=400, template="plotly_white",
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # ---- Equity comparison chart ----
    st.subheader("Total Equity Comparison")
    fig_eq = go.Figure()
    for name, prop in PROPERTIES.items():
        price = prop["price"]
        dp = down_pcts[name]
        loan = price - price * dp / 100
        vals = appreciation_series(price, appreciation_rate, projection_years)
        bals = [loan] + list(amortization_schedule(loan, interest_rate, loan_term)[0][: projection_years * 12])
        while len(bals) < len(vals):
            bals.append(0)
        eq = [v - b for v, b in zip(vals, bals)]
        fig_eq.add_trace(go.Scatter(
            x=[m / 12 for m in range(len(eq))],
            y=eq,
            name=prop["address"],
            line=dict(width=2),
        ))
    fig_eq.update_layout(
        xaxis_title="Years", yaxis_title="Equity ($)",
        yaxis_tickformat="$,.0f",
        height=400, template="plotly_white",
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig_eq, use_container_width=True)
