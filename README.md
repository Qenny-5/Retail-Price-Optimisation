# 🛒 Indian Retail Price Optimisation and Demand Forecasting Platform

## Business Problem
Indian e-commerce companies frequently lose revenue through suboptimal pricing strategies and inventory mismatches. This platform processes **1.1 million transaction records** spanning 20+ Indian cities and multiple product categories to optimize pricing, forecast demand, and provide real-time economic context.

## 🚀 Live Dashboard
[→ Open Live Platform](https://retail-price-optimisation-ambihzgjduyjfjtq4cksna.streamlit.app) 

---

## 🔑 Key Business Findings
- **Inelastic Demand in Electronics:** Electronics demonstrated an elasticity coefficient of `+0.133` (inelastic), indicating that consumers are not overly price-sensitive, allowing for data-backed price optimizations without risking volume loss.
- **High-Accuracy Demand Forecasting:** Trained Prophet models incorporating Indian festival seasonality (Diwali, Independence Day, Republic Day) achieved exceptional accuracy, with a **sub-4% MAPE** across all major categories (e.g., Electronics at `2.2%` and Home & Living at `2.5%`).
- **Revenue Uplift Potential:** Category-level price optimization curves indicate potential revenue uplifts ranging from `+16.5%` (Home Appliances) to `+41.0%` (Footwear) via optimal pricing adjustments.
- **Real-Time Macro Integration:** Integrated live macroeconomic and environmental feeds (OpenWeatherMap, World Bank CPI Inflation, Frankfurter FX USD/INR, and Alpha Vantage WTI Crude Oil) to capture real-time pricing pressure and supply chain cost signals.

---

## 🛠️ Technical Architecture
- **Data Engineering:** Python, Pandas, NumPy, Scikit-learn, Holidays API.
- **Machine Learning & Econometrics:** Meta Prophet (Time-Series Forecasting), Statsmodels OLS Regression (Log-Log Price Elasticity Modelling).
- **Live APIs:** OpenWeatherMap, World Bank, Frankfurter API, Alpha Vantage.
- **Web Application & Visualization:** Streamlit, Plotly Express & Graph Objects.

---

## 📊 Results Summary

| Category | Average Current Price (₹) | Optimal Recommended Price (₹) | Projected Revenue Impact (%) | Model MAPE |
| :--- | :--- | :--- | :--- | :--- |
| **Electronics** | ₹30,410 | ₹39,533 (+30.0%) | +35.2% | 2.2% |
| **Footwear** | ₹2,550 | ₹3,315 (+30.0%) | +41.0% | 3.1% |
| **Furniture** | ₹8,759 | ₹11,386 (+30.0%) | +38.3% | 2.6% |
| **Kitchen** | ₹3,102 | ₹4,033 (+30.0%) | +37.6% | 3.5% |
| **Accessories** | ₹1,574 | ₹2,046 (+30.0%) | +33.2% | 2.7% |
| **Clothing** | ₹2,103 | ₹2,733 (+30.0%) | +28.6% | 2.6% |
| **Home & Living** | ₹1,851 | ₹2,406 (+30.0%) | +24.0% | 2.5% |
| **Books** | ₹675 | ₹877 (+30.0%) | +23.4% | 3.7% |
| **Home Appliances** | ₹4,874 | ₹6,336 (+30.0%) | +16.5% | 2.7% |

---

## 👨‍💻 Author
Built as an end-to-end retail intelligence and dynamic pricing solution for the Indian e-commerce market.
