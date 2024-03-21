import streamlit as st
import pandas as pd
import numpy as np
import boto3
from io import BytesIO
 
# AWS S3'ten dosya indirme fonksiyonu
def s3_dosya_indir(bucket_name, object_key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_name, Key=object_key)
    data = obj['Body'].read()
    return BytesIO(data)
 
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
    tum_personellerin_programi = pd.DataFrame()
    toplam_calisma_saatleri = []
 
    for personel, gunler in personel_programi.items():
        saat_dilimleri = sorted(list(set([saat for gun in gunler.values() for saat in gun])))
        data = {'Personel': personel, 'Gün': [], **{saat: [] for saat in saat_dilimleri}}
       
        toplam_saat = sum(len(saatler) for saatler in gunler.values())
        toplam_calisma_saatleri.append({'Personel': personel, 'Toplam Çalışma Saati': toplam_saat})
       
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
            df_uploaded_personel = pd.read_excel
            uploaded_personel_listesi, usecols=['Ad Soyad']
            personel_listesi = df_uploaded_personel['Ad Soyad'].tolist()
            st.write('Yüklenen personel listesi başarıyla alındı.')
            st.dataframe(df_uploaded_personel)
 
            # S3'ten vardiya planını indir
            bucket_name = 'testssp'
            object_key = '7_gunluk_vardiya_plani.xlsx'
           
            # S3'den dosyayı belleğe indir
            excel_io = s3_dosya_indir(bucket_name, object_key)
            df_vardiya_plani = pd.read_excel(excel_io, header=0, index_col=0)
            st.success('7 günlük vardiya planı dosyası başarıyla S3\'ten indirildi ve okundu.')
            # st.dataframe(df_vardiya_plani)
           
            # Atama fonksiyonunu çağır
            personel_programi = atama_yap(df_vardiya_plani, personel_listesi)
           
            # Excel dosyası olarak sonuçları indir
            excel_data = sonuclari_excel_olarak_indir(personel_programi)
            st.download_button(label="Atama Sonuçlarını Excel olarak indir",
                               data=excel_data,
                               file_name="7_gunluk_vardiya_plani.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error('Personel listesi yüklenmedi.')
    else:
        st.session_state['login_successful'] = False
        st.error('Giriş başarısız. Lütfen tekrar deneyin.')
