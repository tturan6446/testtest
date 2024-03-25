import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import PolynomialFeatures, LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score

# İlk kısım: Veri işleme ve model eğitimi
# Not: Bu, örnek bir veri seti ve basit bir model eğitim sürecidir. Gerçek verilerinizle değiştirmeniz gerekecektir.
data = {
    'Gün': ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'],
    'Çalışan Sayısı': [10, 12, 14, 11, 13, 15, 9],  # Gerçek değerler
    'Tahmin': [9, 12, 13, 11, 14, 15, 10]  # Tahmin edilen değerler
}
df = pd.DataFrame(data)

# Veri setini hafızada bir Excel dosyasına kaydetme
output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Vardiya Planı')
    writer.save()
pivot_excel_data = output.getvalue()

# İkinci kısım: Streamlit uygulaması
def atama_yap(df):
    # Örnek atama işlemi
    # Burada kendi atama mantığınızı uygulayın
    atamalar = df.copy()
    atamalar['Atama'] = 'Evet'  # Basit bir atama örneği
    return atamalar

def sonuclari_excel_olarak_indir(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
        writer.save()
    return output.getvalue()

def streamlit_app(pivot_excel_data):
    st.title('Smart Shift Planner')

    user = st.text_input('Kullanıcı Adı')
    password = st.text_input('Şifre', type='password')

    if st.button('Giriş Yap'):
        if user == 'admin' and password == '12345':
            st.success('Giriş başarılı!')
            
            if pivot_excel_data:
                df_uploaded = pd.read_excel(BytesIO(pivot_excel_data))
                st.success('Vardiya planı başarıyla yüklendi.')
                st.dataframe(df_uploaded)

                # Atama işlemi
                atamalar_df = atama_yap(df_uploaded)
                st.write('Atama Sonuçları:')
                st.dataframe(atamalar_df)

                # Excel dosyası olarak sonuçları indir
                excel_data = sonuclari_excel_olarak_indir(atamalar_df)
                st.download_button(label="Atama Sonuçlarını Excel olarak indir",
                                   data=excel_data,
                                   file_name="atama_sonuclari.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.error('Vardiya planı bulunamadı.')
        else:
            st.error('Giriş başarısız. Lütfen tekrar deneyin.')

if __name__ == '__main__':
    streamlit_app(pivot_excel_data)
