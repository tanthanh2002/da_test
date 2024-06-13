import pandas as pd
import plotly.express as px
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Transaction Performance Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded",
)

alt.themes.enable("dark")
df = pd.read_csv("cleaned_data.csv")

df.Date = pd.to_datetime(df.Date)
df.First_tran_date = pd.to_datetime(df.First_tran_date)


st.title("Performance Dashboard")

with st.sidebar:
    st.title("Please filter the data")

    year_list = list(df.Date.dt.year.unique())[::-1]

    selected_year = st.selectbox("Select a year", year_list)

    month_list = list(sorted(df.Date.dt.month.unique()))

    selected_month = st.selectbox("Select a month", month_list)
st.markdown("#### Overview of monthly")
col = st.columns((2, 2, 2, 2), gap="medium")


# convert to currency vnđ
def currency(x):
    return f"{x:,.2f}"


with col[0]:

    month_revenue = df[df.Date.dt.month == selected_month].Revenue.sum()
    previous_month_revenue = df[df.Date.dt.month == selected_month - 1].Revenue.sum()

    try:
        percentage_change = (
            (float(month_revenue) - float(previous_month_revenue))
            / float(previous_month_revenue)
            * 100
        )
        delta = f"{percentage_change:.2f}%"
    except ZeroDivisionError:
        delta = "N/A"

    st.metric(
        label="Revenue (VND)",
        value=currency(month_revenue),
        delta=delta,
    )


with col[1]:
    delta_transaction = (
        "N/A"
        if selected_month == 1
        else df[df.Date.dt.month == selected_month].order_id.nunique()
        - df[df.Date.dt.month == selected_month - 1].order_id.nunique()
    )

    st.metric(
        label="Transactions",
        value=df[df.Date.dt.month == selected_month].order_id.nunique(),
        delta=delta_transaction,
    )


with col[2]:
    new_users_count = df[
        (df["Type_user"] == "New") & (df["Date"].dt.month == selected_month)
    ]["user_id"].nunique()

    delta_user_count = (
        "N/A"
        if selected_month == 1
        else int(
            new_users_count
            - df[
                (df["Type_user"] == "New")
                & (df["Date"].dt.month == (selected_month - 1))
            ]["user_id"].nunique()
        )
    )

    st.metric(
        label="New Users",
        value=new_users_count,
        delta=delta_user_count,
    )


with col[3]:
    # Top of Telco
    st.markdown("#### Top TelCo by Revenue")
    df_by_telco = (
        df[df.Date.dt.month == selected_month]
        .groupby("Merchant_name")
        .Revenue.sum()
        .reset_index()
    )
    sorted_df = df_by_telco.sort_values("Revenue", ascending=False)
    sorted_df["Revenue"] = sorted_df["Revenue"].apply(currency)
    st.dataframe(
        sorted_df,
        column_order=("Merchant_name", "Revenue"),
        hide_index=True,
        width=None,
        column_config={
            "Merchant_name": st.column_config.TextColumn(
                "Merchant_name",
            ),
            "Revenue": st.column_config.TextColumn(
                "Revenue",
                # format="%f",
                # min_value=0,
                # max_value=max(sorted_df.population),
            ),
        },
    )

st.markdown("---")
st.markdown("#### Overview of yearly")
col = st.columns((4.5, 4.5), gap="medium")

with col[0]:

    # col1, col2 = st.columns(2)

    # col1.metric(
    #     label="Total Revenue",
    #     value=currency(df[df.Date.dt.year == selected_year].Revenue.sum()),
    # )

    # col2.metric(
    #     label="Total Transactions",
    #     value=df[df.Date.dt.year == selected_year].order_id.nunique(),
    # )

    df_year = df[df.Date.dt.year == selected_year]
    df_year["Month"] = df_year.Date.dt.month
    df_year_agg = df_year.groupby("Month").Revenue.sum().reset_index()

    fig = px.bar(
        df_year_agg,
        x="Month",
        y="Revenue",
        title="Revenue by Month",
        labels={"Revenue": "Revenue (VND)"},
    )

    st.plotly_chart(fig)

    # draw histogram
    fig = px.box(
        df,
        x="Gender",
        y="Amount",
        title="Amount Distribution",
        labels={"Amount": "Amount (VND)"},
    )

    df_age_group = df.groupby("Age")["Revenue"].sum().reset_index()

    st.plotly_chart(fig)
    fig_age_gender = px.bar(
        df_age_group,
        x="Age",
        y="Revenue",
        title="Age Distribution",
        labels={"Revenue": "Revenue (VND)"},
        barmode="group",
    )

    st.plotly_chart(fig_age_gender)


with col[1]:

    df_market_share = (
        df[df.Date.dt.year == selected_year]
        .groupby("Merchant_name")
        .Revenue.sum()
        .reset_index()
    )

    fig = px.pie(
        df_market_share,
        values="Revenue",
        names="Merchant_name",
        title="Market Share",
    )

    st.plotly_chart(fig)

    df_gender = (
        df[df.Date.dt.year == selected_year]
        .groupby("Gender")
        .Revenue.sum()
        .reset_index()
    )

    fig = px.pie(
        df_gender,
        values="Revenue",
        names="Gender",
        title="Revenue ratio by gender",
    )

    st.plotly_chart(fig)

    df_new_user = df[df["Type_user"] == "New"]
    df_new_user["Month"] = df_new_user.Date.dt.month

    new_users_per_month = (
        df_new_user[df_new_user["Type_user"] == "New"]
        .groupby("Month")["user_id"]
        .nunique()
        .reset_index()
    )

    new_users_per_month.columns = ["Month", "New_Users"]

    fig = px.line(
        new_users_per_month,
        x="Month",
        y="New_Users",
        title="Monthly New User Count",
        labels={"New_Users": "Number of New Users"},
    )

    fig.update_traces(line=dict(color="#ff6361"))
    st.plotly_chart(fig)

# st.markdown("---")
st.dataframe(df)
