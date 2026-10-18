import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(
    page_title='Indian Retail Intelligence Platform',
    page_icon='🛒',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ── Load data ──────────────────────────────────────────────────
@st.cache_data(ttl=3600)  # refresh every hour
def load_data():
    # Replace this string with your public dataset URL (e.g., S3 link, raw GitHub URL, etc.)
    PUBLIC_DATA_URL = 'https://raw.githubusercontent.com/Qenny-5/Retail-Price-Optimisation/main/data/processed/sample_data.csv'
    
    # Use the public URL directly inside read_csv
    df = pd.read_csv(PUBLIC_DATA_URL)
    df['Date']    = pd.to_datetime(df['Date'])
    df['Revenue'] = df['Quantity'] * df['Price']
    df['Year']    = df['Date'].dt.year
    df['Month']   = df['Date'].dt.month
    return df

@st.cache_data(ttl=1800)  # refresh every 30 min
def get_live_usd_inr():
    try:
        r = requests.get(
            'https://api.frankfurter.app/latest',
            params={'from': 'USD', 'to': 'INR'}, timeout=5)
        if r.status_code == 200:
            return r.json()['rates']['INR']
    except Exception:
        pass
    return None

df = load_data()

# ── Sidebar navigation ────────────────────────────────────────
st.sidebar.title('🛒 Retail Intelligence')
st.sidebar.markdown('**Indian E-Commerce Analytics Platform**')
page = st.sidebar.radio(
    'Navigate',
    ['📊 Overview', '📈 Demand Forecast',
     '💰 Price Optimisation', '🏙️ City Intelligence']
)

# Live data sidebar
st.sidebar.markdown('---')
st.sidebar.markdown('**Live Market Data**')
usd_inr = get_live_usd_inr()
if usd_inr:
    st.sidebar.metric('USD/INR Rate', f'₹{usd_inr:.2f}',
                       delta='Live')
st.sidebar.caption(
    f'Last updated: {datetime.now().strftime("%H:%M")}')

# ── Filters ───────────────────────────────────────────────────
st.sidebar.markdown('---')
st.sidebar.markdown('**Filters**')
selected_city = st.sidebar.multiselect(
    'Select Cities',
    df['City'].unique(),
    default=df['City'].unique()[:5]
)
selected_category = st.sidebar.selectbox(
    'Select Category',
    ['All'] + list(df['Category'].unique())
)
selected_year = st.sidebar.selectbox(
    'Select Year',
    sorted(df['Year'].unique(), reverse=True)
)

# Apply filters
filtered = df[
    (df['City'].isin(selected_city)) &
    (df['Year'] == selected_year)
]
if selected_category != 'All':
    filtered = filtered[
        filtered['Category'] == selected_category]

# ── PAGE 1: OVERVIEW ──────────────────────────────────────────
if page == '📊 Overview':
    st.title('📊 Indian Retail Market Overview')
    st.caption(f'Showing data for {selected_year} | '
               f'{len(filtered):,} transactions')

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Revenue',
                f'₹{filtered["Revenue"].sum()/1e7:.1f} Cr')
    col2.metric('Total Orders',
                f'{len(filtered):,}')
    col3.metric('Avg Order Value',
                f'₹{filtered["Revenue"].mean():.0f}')
    col4.metric('Cities Active',
                f'{filtered["City"].nunique()}')

    st.markdown('---')
    col1, col2 = st.columns(2)

    # Revenue by category
    with col1:
        cat_rev = (filtered.groupby('Category')['Revenue']
                   .sum().sort_values(ascending=True)
                   .reset_index())
        fig = px.bar(cat_rev, x='Revenue', y='Category',
                     orientation='h',
                     title='Revenue by Category',
                     color='Revenue',
                     color_continuous_scale='Blues')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Monthly trend
    with col2:
        monthly = (filtered.groupby('Month')['Revenue']
                   .sum().reset_index())
        monthly['Month_Name'] = pd.to_datetime(
            monthly['Month'], format='%m').dt.strftime('%b')
        fig = px.line(monthly, x='Month_Name', y='Revenue',
                      title='Monthly Revenue Trend',
                      markers=True)
        fig.update_traces(line_color='#E74C3C', line_width=3)
        st.plotly_chart(fig, use_container_width=True)

    # City performance
    city_perf = (filtered.groupby('City').agg(
        Revenue=('Revenue', 'sum'),
        Orders=('Quantity', 'count'),
        AvgOrderValue=('Revenue', 'mean')
    ).sort_values('Revenue', ascending=False)
     .head(10).reset_index())
    st.subheader('Top 10 Cities by Revenue')
    st.dataframe(
        city_perf.style.format({
            'Revenue': '₹{:,.0f}',
            'AvgOrderValue': '₹{:,.0f}'
        }),
        use_container_width=True
    )

# ── PAGE 2: DEMAND FORECAST ───────────────────────────────────
elif page == '📈 Demand Forecast':
    st.title('📈 Demand Forecasting Engine')
    st.caption('Prophet time-series model with Indian festival '
               'seasonality')

    forecast_cat = st.selectbox(
        'Select Category to Forecast',
        df['Category'].unique()
    )
    forecast_weeks = st.slider(
        'Forecast Horizon (weeks)', 4, 52, 26)

    if st.button('Generate Forecast', type='primary'):
        with st.spinner(f'Training Prophet model for '
                        f'{forecast_cat}...'):
            from prophet import Prophet
            import warnings
            warnings.filterwarnings('ignore')

            cat_data = (df[df['Category'] == forecast_cat]
                        .groupby(pd.Grouper(key='Date', freq='W'))
                        ['Revenue'].sum()
                        .reset_index())
            cat_data.columns = ['ds', 'y']
            cat_data = cat_data[cat_data['y'] > 0]

            # Add Diwali
            diwali = pd.DataFrame({
                'holiday': 'Diwali',
                'ds': pd.to_datetime([
                    '2024-11-01', '2025-10-20', '2026-11-08']),
                'lower_window': -7, 'upper_window': 3
            })

            model = Prophet(
                holidays=diwali,
                yearly_seasonality=True,
                weekly_seasonality=True,
                interval_width=0.95
            )
            model.fit(cat_data)

            future   = model.make_future_dataframe(
                periods=forecast_weeks, freq='W')
            forecast = model.predict(future)

        # Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cat_data['ds'], y=cat_data['y'],
            name='Actual Sales', line=dict(color='blue')))
        fig.add_trace(go.Scatter(
            x=forecast['ds'], y=forecast['yhat'],
            name='Forecast', line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter(
            x=forecast['ds'].tolist() +
              forecast['ds'].tolist()[::-1],
            y=forecast['yhat_upper'].tolist() +
              forecast['yhat_lower'].tolist()[::-1],
            fill='toself', fillcolor='rgba(255,0,0,0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval'))
        fig.update_layout(
            title=f'{forecast_cat} — Demand Forecast '
                  f'({forecast_weeks} weeks ahead)',
            xaxis_title='Date',
            yaxis_title='Weekly Revenue (₹)')
        st.plotly_chart(fig, use_container_width=True)

        # Forecast summary
        future_only = forecast[
            forecast['ds'] > cat_data['ds'].max()]
        st.metric(
            'Projected Revenue (next 4 weeks)',
            f'₹{future_only.head(4)["yhat"].sum():,.0f}')

# ── PAGE 3: PRICE OPTIMISATION ────────────────────────────────
elif page == '💰 Price Optimisation':
    st.title('💰 Price Optimisation Engine')
    st.caption('Elasticity-based optimal pricing recommendations')

    col1, col2 = st.columns(2)
    with col1:
        opt_category = st.selectbox(
            'Product Category', df['Category'].unique())
    with col2:
        current_price = st.number_input(
            'Current Price (₹)',
            min_value=10, max_value=100000,
            value=int(df[df['Category'] == opt_category]
                      ['Price'].mean()))

    if st.button('Calculate Optimal Price', type='primary'):
        # Quick elasticity calculation
        cat_df  = df[df['Category'] == opt_category].copy()
        weekly  = cat_df.groupby(
            pd.Grouper(key='Date', freq='W')
        ).agg(avg_price=('Price', 'mean'),
              total_quantity=('Quantity', 'sum')).reset_index()
        weekly  = weekly[
            (weekly['avg_price'] > 0) &
            (weekly['total_quantity'] > 0)]
        weekly['log_price']    = np.log(weekly['avg_price'])
        weekly['log_quantity'] = np.log(weekly['total_quantity'])

        import statsmodels.api as sm
        X = sm.add_constant(weekly['log_price'])
        result = sm.OLS(weekly['log_quantity'], X).fit()
        elasticity = result.params['log_price']

        # Price optimisation
        price_range  = np.linspace(
            current_price * 0.7, current_price * 1.3, 61)
        revenues     = []
        baseline_qty = 1000

        for p in price_range:
            pct_change   = (p - current_price) / current_price
            qty_change   = elasticity * pct_change
            new_qty      = baseline_qty * (1 + qty_change)
            new_qty      = max(0, new_qty)
            revenues.append(p * new_qty)

        optimal_idx   = np.argmax(revenues)
        optimal_price = price_range[optimal_idx]
        rev_change    = ((revenues[optimal_idx] -
                          current_price * baseline_qty)
                         / (current_price * baseline_qty)
                         * 100)

        # Display results
        c1, c2, c3 = st.columns(3)
        c1.metric('Current Price', f'₹{current_price:,.0f}')
        c2.metric('Optimal Price',
                  f'₹{optimal_price:,.0f}',
                  delta=f'{((optimal_price-current_price)/current_price*100):+.1f}%')
        c3.metric('Revenue Impact', f'{rev_change:+.1f}%',
                  delta='vs current')

        st.info(f'**Price Elasticity:** {elasticity:.3f} — '
                f'{"Elastic (price sensitive)" if abs(elasticity)>1 else "Inelastic (price insensitive)"}')

        # Revenue curve
        fig = px.line(
            x=price_range, y=revenues,
            labels={'x': 'Price (₹)', 'y': 'Projected Revenue'},
            title='Revenue Optimisation Curve')
        fig.add_vline(
            x=current_price,
            line_dash='dash', line_color='blue',
            annotation_text='Current Price')
        fig.add_vline(
            x=optimal_price,
            line_dash='dash', line_color='red',
            annotation_text='Optimal Price')
        st.plotly_chart(fig, use_container_width=True)

# ── PAGE 4: CITY INTELLIGENCE ─────────────────────────────────
elif page == '🏙️ City Intelligence':
    st.title('🏙️ City-Level Market Intelligence')

    # City tier performance
    tier_map = {
        'Mumbai': 'Tier 1', 'Delhi': 'Tier 1',
        'Bangalore': 'Tier 1', 'Hyderabad': 'Tier 1',
        'Chennai': 'Tier 1', 'Kolkata': 'Tier 1',
        'Pune': 'Tier 2', 'Ahmedabad': 'Tier 2',
        'Jaipur': 'Tier 2', 'Lucknow': 'Tier 2'
    }
    df['City_Tier'] = df['City'].map(tier_map).fillna('Tier 3')

    tier_perf = (df.groupby('City_Tier').agg(
        Total_Revenue=('Revenue', 'sum'),
        Avg_Order_Value=('Revenue', 'mean'),
        Total_Orders=('Quantity', 'count')
    ).reset_index())

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(tier_perf, values='Total_Revenue',
                     names='City_Tier',
                     title='Revenue Share by City Tier',
                     color_discrete_map={
                         'Tier 1': '#E74C3C',
                         'Tier 2': '#E67E22',
                         'Tier 3': '#2ECC71'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        city_rev = (df.groupby('City')['Revenue']
                    .sum().sort_values(ascending=False)
                    .head(15).reset_index())
        fig = px.bar(city_rev, x='City', y='Revenue',
                     title='Top 15 Cities by Revenue',
                     color='Revenue',
                     color_continuous_scale='Reds')
        fig.update_layout(
            xaxis_tickangle=45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Category preference by city
    st.subheader('Category Preference Heatmap by City')
    top_cities = (df.groupby('City')['Revenue']
                  .sum().nlargest(10).index)
    heatmap_data = (df[df['City'].isin(top_cities)]
                    .groupby(['City', 'Category'])['Revenue']
                    .sum().unstack(fill_value=0))
    # Normalise to percentage
    heatmap_pct = heatmap_data.div(
        heatmap_data.sum(axis=1), axis=0) * 100

    fig = px.imshow(heatmap_pct.round(1),
                    text_auto=True,
                    aspect='auto',
                    color_continuous_scale='RdYlGn',
                    title='Category Revenue Share (%) by City')
    st.plotly_chart(fig, use_container_width=True)
