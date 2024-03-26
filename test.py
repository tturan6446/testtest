import streamlit as st
import pandas as pd
import requests
from io import BytesIO

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
    havuz_personel_listesi = []

    for personel, gunler in personel_programi.items():
        saat_dilimleri = sorted(list(set([saat for gun in gunler.values() for saat in gun])))
        data = {'Personel': personel, 'Gün': [], **{saat: [] for saat in saat_dilimleri}}
        toplam_saat = sum(len(saatler) for saatler in gunler.values())
        toplam_calisma_saatleri.append({'Personel': personel, 'Toplam Çalışma Saati': toplam_saat})

        eksik_saat = max(0, 63 - toplam_saat)
        if toplam_saat < 63:
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
        pd.DataFrame(havuz_personel_listesi).to_excel(writer, index=False, sheet_name='Havuz Personelleri')

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

        # GitHub'dan Excel dosyasını okuma
        url = 'https://raw.githubusercontent.com/tturan6446/testtest/main/7_gunluk_vardiya_plani.xlsx'
        response = requests.get(url)
        data = BytesIO(response.content)
        df_vardiya_plani = pd.read_excel(data, header=2, index_col=0)
                df_vardiya_plani.columns = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'] 
                st.success('7 günlük vardiya planı dosyası başarıyla okundu.')
                st.dataframe(df_vardiya_plani)
                st.write(df_vardiya_plani.index)
                st.write(df_vardiya_plani.columns)
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
                st.error('7 günlük vardiya planı dosyası bulunamadı.')
    else:
        st.session_state['login_successful'] = False
        st.error('Giriş başarısız. Lütfen tekrar deneyin.')
