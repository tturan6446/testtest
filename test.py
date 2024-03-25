import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO  # Excel dosyasını bellekte tutmak için
import requests
 
 
# GitHub'dan dosyayı indirme fonksiyonu

def github_dan_dosya_indir(url):
    try:
        # SSL Doğrulamasını devre dışı bırak
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            return pd.read_excel(BytesIO(response.content))
        else:
            return None
    except Exception as e:
        print(f"İstisna oluştu: {e}")
        return None
    
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)   
    
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
 
#Sabah 8 kısıtı eklenmeli
#Ek sayfada plan olacak
#Buraya off günleri belirtilmeli ya da off günleri buraya kısıt verilerek çıkarılmalı
#off planı Oktay Bey'den gelmeli
#Vardiya şekli böyle mi olmalı ?
#Hem çalışan hem de gün bazlı özet gösterim olmalı
#Sabah saatlerinde vardiya çıktısı çok doğru değil, kontrol edilmeli
def sonuclari_excel_olarak_indir(personel_programi):
    tum_personellerin_programi = pd.DataFrame()
    toplam_calisma_saatleri = []
    havuz_personel_listesi = []  # Havuz personel listesi

    for personel, gunler in personel_programi.items():
        saat_dilimleri = sorted(list(set([saat for gun in gunler.values() for saat in gun])))
        data = {'Personel': personel, 'Gün': [], **{saat: [] for saat in saat_dilimleri}}
        toplam_saat = sum(len(saatler) for saatler in gunler.values())
        toplam_calisma_saatleri.append({'Personel': personel, 'Toplam Çalışma Saati': toplam_saat})

        eksik_saat = max(0, 63 - toplam_saat)  # Eksik saat hesaplama
        if toplam_saat < 63:  # Haftalık 63 saat dolduramayanlar için kontrol
            havuz_personel_listesi.append({'Personel': personel, 'Durum': 'Havuz Personel', 'Eksik Saat': eksik_saat})

        for gun in ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']:
            data['Gün'].append(gun)
            for saat in saat_dilimleri:
                data[saat].append('X' if saat in gunler[gun] else '')
        
        personel_df = pd.DataFrame(data)
        tum_personellerin_programi = pd.concat([tum_personellerin_programi, personel_df, pd.DataFrame([['']*(len(saat_dilimleri)+2)], columns=['Personel', 'Gün', *saat_dilimleri])])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        tum_personellerin_programi.to_excel(writer, index=False, sheet_name='Vardiya Planı')
        pd.DataFrame(toplam_calisma_saatleri).to_excel(writer, index=False, sheet_name='Toplam Çalışma Saatleri')
        pd.DataFrame(havuz_personel_listesi).to_excel(writer, index=False, sheet_name='Havuz Personelleri')  # Havuz personelleri sayfasına 'Eksik Saat' sütunu ekle

    processed_data = output.getvalue()
    return processed_data


 
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
 
               # GitHub'dan vardiya planı dosyasını indir
            github_url = 'https://github.com/tturan6446/testtest/raw/main/7_gunluk_vardiya_plani.xlsx'
            df_vardiya_plani = github_dan_dosya_indir(github_url)
            if df_vardiya_plani is not None:
                st.success('GitHub üzerinden 7 günlük vardiya planı dosyası başarıyla indirildi ve okundu.')
                st.dataframe(df_vardiya_plani)
               
                # Atama fonksiyonunu çağır
                personel_programi = atama_yap(df_vardiya_plani, personel_listesi)
               
                # Excel dosyası olarak sonuçları indir
                excel_data = sonuclari_excel_olarak_indir(personel_programi)
                st.dataframe(personel_programi)
                
                st.download_button(label="Atama Sonuçlarını Excel olarak indir",
                                   data=excel_data,
                                   file_name="vardiya_planı.xlsx",
                                   mime="application/vnd.ms-excel")
            else:
                st.error('GitHub üzerinden dosya indirilemedi.  ')
    else:
        st.session_state['login_successful'] = False
        st.error('Giriş başarısız. Lütfen tekrar deneyin.')
