import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import requests

# Fonksiyon tanımlamaları
def atama_yap(vardiya_plani_df, personel_listesi):
    personel_programi = {personel: {'Pazartesi': [], 'Salı': [], 'Çarşamba': [], 'Perşembe': [], 'Cuma': [], 'Cumartesi': [], 'Pazar': []} for personel in personel_listesi}
    gunler = vardiya_plani_df.index.tolist()
    saatler = vardiya_plani_df.columns.tolist()

    for personel in personel_listesi:
        for gun in gunler:
            for saat in saatler:
                try:
                    if len(personel_programi[personel][gun]) < 9 and vardiya_plani_df.at[gun, saat] > 0:
                        personel_programi[personel][gun].append(saat)
                        vardiya_plani_df.at[gun, saat] -= 1
                except IndexError:
                    break
    return personel_programi

def sonuclari_excel_olarak_indir(personel_programi):
    # Bu fonksiyonun içeriği aynı kalıyor, detaylar atlandı

# Ana Streamlit uygulaması
    st.image("https://www.filmon.com.tr/wp-content/uploads/2022/01/divan-logo.png", width=200)
    st.title('Smart Shift Planner')

user = st.text_input('Kullanıcı Adı')
password = st.text_input('Şifre', type='password')

if 'login_successful' not in st.session_state:
    st.session_state['login_successful'] = False

if st.button('Giriş Yap') or st.session_state['login_successful']:
    if user == 'admin' and password == '12345':
        st.session_state['login_successful'] = True
        st.success('Giriş başarılı!')

        uploaded_personel_listesi = st.file_uploader("Çalışanların Excel dosyasını yükle", type=['xlsx'], key="personel_uploader")
        if uploaded_personel_listesi is not None:
            df_uploaded_personel = pd.read_excel(uploaded_personel_listesi, usecols=['Ad Soyad'])
            personel_listesi = df_uploaded_personel['Ad Soyad'].tolist()
            st.write('Yüklenen personel listesi başarıyla alındı.')
            st.dataframe(df_uploaded_personel)

            # GitHub'dan vardiya planı dosyasını okuma
            url = 'https://raw.githubusercontent.com/tturan6446/testtest/main/7_gunluk_vardiya_plani.xlsx'
            response = requests.get(url)
            data = BytesIO(response.content)
            df_vardiya_plani = pd.read_excel(data, header=2, index_col=0)
            df_vardiya_plani.columns = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
            st.success('7 günlük vardiya planı dosyası başarıyla okundu.')
            st.dataframe(df_vardiya_plani)

            # Atama fonksiyonunu çağır
            personel_programi = atama_yap(df_vardiya_plani, personel_listesi)

            # Excel dosyası olarak sonuçları indir
            excel_data = sonuclari_excel_olarak_indir(personel_programi)
            st.download_button(label="Atama Sonuçlarını Excel olarak indir",
                               data=excel_data,
                               file_name="vardiya_planı.xlsx",
                               mime="application/vnd.ms-excel")
        else:
            st.error('Lütfen bir personel listesi dosyası yükleyin
