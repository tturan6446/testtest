import streamlit as st
import pandas as pd

# Excel dosyasını yükleme
@st.cache
def load_data(file_path):
    return pd.read_excel(file_path)

file_path = 'kampanya analiz.xlsx'
data = load_data(file_path)

# Ağırlıklar için kaydırıcılar
st.sidebar.header("Ağırlıklar")
weight_orders = st.sidebar.slider("Toplam Siparişler Ağırlığı", 0.0, 1.0, 0.2)
weight_revenue = st.sidebar.slider("Toplam Gelir Ağırlığı", 0.0, 1.0, 0.3)
weight_customers = st.sidebar.slider("Toplam Müşteriler Ağırlığı", 0.0, 1.0, 0.2)
weight_avg_order = st.sidebar.slider("Ortalama Sipariş Değeri Ağırlığı", 0.0, 1.0, 0.1)
weight_new_customers = st.sidebar.slider("Yeni Müşteriler Ağırlığı", 0.0, 1.0, 0.1)
weight_product_count = st.sidebar.slider("Kampanyalı Ürün Sayısı Ağırlığı", 0.0, 1.0, 0.1)

# Kampanya performansını hesaplama
def calculate_performance(data):
    data['total_orders'] = data.groupby('KAMPANYA_ID')['ORDER_ID'].transform('nunique')
    data['total_revenue'] = data.groupby('KAMPANYA_ID')['URUN_CIRO_TL'].transform('sum')
    data['total_customers'] = data.groupby('KAMPANYA_ID')['CUSTOMER_ID'].transform('nunique')
    data['avg_order_value'] = data.groupby('KAMPANYA_ID')['URUN_CIRO_TL'].transform('mean')
    data['new_customers'] = data.groupby('KAMPANYA_ID')['YENI_MUSTERI_FTB'].transform('sum')
    data['campaign_product_count'] = data.groupby('KAMPANYA_ID')['KAMPANYALI_URUN_SAYISI'].transform('sum')
    
    return data.drop_duplicates('KAMPANYA_ID')

# Performansı normalize etme ve puan hesaplama
def calculate_scores(data):
    data['norm_orders'] = data['total_orders'] / data['total_orders'].max()
    data['norm_revenue'] = data['total_revenue'] / data['total_revenue'].max()
    data['norm_customers'] = data['total_customers'] / data['total_customers'].max()
    data['norm_avg_order_value'] = data['avg_order_value'] / data['avg_order_value'].max()
    data['norm_new_customers'] = data['new_customers'] / data['new_customers'].max()
    data['norm_campaign_product_count'] = data['campaign_product_count'] / data['campaign_product_count'].max()

    data['total_score'] = (
        data['norm_orders'] * weight_orders +
        data['norm_revenue'] * weight_revenue +
        data['norm_customers'] * weight_customers +
        data['norm_avg_order_value'] * weight_avg_order +
        data['norm_new_customers'] * weight_new_customers +
        data['norm_campaign_product_count'] * weight_product_count
    )
    return data

performance_data = calculate_performance(data)
scored_data = calculate_scores(performance_data)

top_campaigns = scored_data.nlargest(5, 'total_score')

st.title("En İyi Kampanyalar")
st.write(top_campaigns[['KAMPANYA_ID', 'total_score']])

st.header("Kampanya Performans Detayları")
st.write(top_campaigns)
