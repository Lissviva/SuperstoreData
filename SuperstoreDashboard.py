import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración inicial
st.set_page_config(layout="wide", page_title="Superstore Dashboard")

# Carga de datos
df = pd.read_csv("superstore_cleandata.csv")
df.columns = df.columns.str.strip()  # Por si acaso hay espacios invisibles

# Recalcular columnas necesarias si no existen
if 'Discount (%)' not in df.columns:
    df['Discount (%)'] = df['Discount'] * 100

if 'Profit Margin (%)' not in df.columns:
    df['Profit Margin (%)'] = (df['Profit'] / df['Sales']) * 100

if 'Loss Risk' not in df.columns:
    df['Loss Risk'] = df['Discount (%)'] > df['Profit Margin (%)']

st.title("Superstore Sales & Profit Dashboard")
st.markdown("Visual summary to identify which products, regions, categories, and segments Superstore should prioritize or avoid.")

# Pestañas principales
tabs = st.tabs([
    "KPIs Overview",
    "Customer Segments",
    "Product Performance",
    "Discount Analysis",
    "Regional Insights",
    "Time Trends",
    "Top Products"
])

# ----------------------------- 1. KPIs Overview -----------------------------
with tabs[0]:
    st.header("General KPIs")
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_loss = df[df['Profit'] < 0]['Profit'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.0f}")
    col2.metric("Total Profit", f"${total_profit:,.0f}")
    col3.metric("Total Loss", f"${abs(total_loss):,.0f}")

    st.markdown("---")
    fig, ax = plt.subplots()
    sns.barplot(x=["Sales", "Profit", "Loss"], y=[total_sales, total_profit, abs(total_loss)], palette=["skyblue", "seagreen", "salmon"], ax=ax)
    ax.set_title("Sales, Profit, and Loss")
    st.pyplot(fig)

    st.markdown("> **Insight:** Despite strong revenue (2.3M dollars in sales), over 50% of the total profit (286K dollars) is offset by losses (156K dollars). Urgent pricing and discount strategy revisions are needed to improve margins.")

# ----------------------------- 2. Customer Segments -----------------------------
with tabs[1]:
    st.header("Profit by Segment and Product Quantity")

    # Gráfico 1: Profit by Segment
    profit_by_segment = df.groupby('Segment')['Profit'].sum().sort_values()
    fig, ax = plt.subplots()
    sns.barplot(x=profit_by_segment.values, y=profit_by_segment.index, palette='pastel', ax=ax)
    ax.set_title("Profit by Segment")
    st.pyplot(fig)

    st.markdown("---")

    quantity = df.groupby(['Segment', 'Category'])['Quantity'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=quantity, x='Category', y='Quantity', hue='Segment', palette='Set2', ax=ax)
    ax.set_title("Quantity Sold by Segment and Category")
    st.pyplot(fig)

    st.write("") 
    st.markdown("> **Recommendation:** Prioritize the *Consumer* segment, which generates the highest profit (nearly $140K) and consistently purchases the largest quantity of products, especially Office Supplies. This segment drives both volume and profitability.")

# ----------------------------- 3. Product Performance -----------------------------
with tabs[2]:
    st.header("Product Category & Subcategory Performance")

    profit_cat = df.groupby('Category')['Profit'].sum().sort_values()
    fig, ax = plt.subplots()
    sns.barplot(x=profit_cat.values, y=profit_cat.index, color='lightgreen', ax=ax)
    ax.set_title("Profit by Category")
    st.pyplot(fig)

    st.markdown("---")

    profit_sub = df.groupby('Sub-Category')['Profit'].sum().sort_values()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=profit_sub.values, y=profit_sub.index, palette='coolwarm', ax=ax)
    ax.set_title("Profit by Sub-Category")
    st.pyplot(fig)

    st.write("") 
    st.markdown("> **Insight:** Focus on profitable sub-categories like *Copiers*, *Phones*, and *Accessories*. Avoid or reassess underperformers such as *Tables*, *Bookcases*, and *Supplies*, which show consistent losses.")

# ----------------------------- 4. Discount Analysis -----------------------------
with tabs[3]:
    st.header("Discount Risk & Profitability")

    fig, ax = plt.subplots()
    sns.histplot(df['Discount (%)'], bins=30, color='steelblue', ax=ax)
    ax.set_title("Distribution of Discounts")
    st.pyplot(fig)

    df['Discount Range'] = (df['Discount (%)'] // 10) * 10
    discount_profit = df.groupby('Discount Range')['Profit'].mean()
    fig, ax = plt.subplots()
    sns.barplot(x=discount_profit.index.astype(str), y=discount_profit.values, palette='coolwarm', ax=ax)
    ax.set_title("Average Profit by Discount Range (%)")
    st.pyplot(fig)

    st.markdown("---")
    
    risk_counts = df['Loss Risk'].value_counts()
    labels = ['At Loss Risk', 'Safe']
    sizes = [risk_counts[True], risk_counts[False]]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['tomato', 'mediumseagreen'])
    ax.set_title("Products at Risk of Loss Due to Discount")
    st.pyplot(fig)
    
    
    st.write("") 
    st.markdown("> **Warning:** Discounts above 30% often exceed profit margins, leading to unsustainable losses. Over 33% of products are sold below cost. The 50% discount tier is the most damaging, averaging the worst losses. A discount cap is highly recommended.")

# ----------------------------- 5. Regional Insights -----------------------------
with tabs[4]:
    st.header("Profitability by Region & City")

    region_profit = df.groupby('Region')['Profit'].sum().sort_values()
    fig, ax = plt.subplots()
    sns.barplot(x=region_profit.values, y=region_profit.index, color='plum', ax=ax)
    ax.set_title("Profit by Region")
    st.pyplot(fig)

    st.markdown("---")

    city_summary = df.groupby('City').agg({'Sales': 'sum', 'Profit': 'sum'}).sort_values(by='Sales', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    city_summary[['Sales', 'Profit']].plot(kind='barh', ax=ax, color=['lightblue', 'salmon'])
    ax.set_title("Top 10 Cities by Sales and Profit")
    ax.invert_yaxis()
    st.pyplot(fig)
    
    st.write("") 
    st.markdown("> **Recommendation:** Invest in high-performing regions: *East* and *West*, especially in cities like *New York*, *Los Angeles*, and *Seattle*. Reevaluate pricing and product strategies in the *Central* region, where profitability is lowest.")

# ----------------------------- 6. Time Trends -----------------------------
with tabs[5]:
    st.header("Seasonality & Order Volume")

    orders_by_day = df['Order Day'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    fig, ax = plt.subplots()
    orders_by_day.plot(kind='bar', color='mediumpurple', ax=ax)
    ax.set_title("Orders by Day of the Week")
    st.pyplot(fig)
    
    st.write("")
    st.markdown("> **Insight:** Q4 (especially October and November) shows increased sales and profit. Mondays are the busiest day of the week. These trends should inform inventory planning and marketing campaigns.")

# ----------------------------- 7. Top Products -----------------------------
with tabs[6]:
    st.header("Best and Worst Performing Products")

    top_quantity = df.groupby('Product Name')['Quantity'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    top_quantity.plot(kind='barh', color='lightblue', ax=ax)
    ax.set_title("Top 10 Products by Quantity Sold")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.markdown("---")
    
    loss_products = df.groupby('Product Name')['Profit'].sum().sort_values().head(10)
    fig, ax = plt.subplots()
    loss_products.plot(kind='barh', color='salmon', ax=ax)
    ax.set_title("Top 10 Products with Highest Losses")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.write("")
    st.markdown("> **Insight:** Best-selling items like *Staples*, *Staple Envelopes*, and *Easy-Staple Paper* are in high demand and relatively profitable. However, products such as *Cubify 3D Printers*, *Lexmark Printers*, and *Conference Tables* drive major losses due to high discounts and low sales volume. These should be reviewed or removed.")