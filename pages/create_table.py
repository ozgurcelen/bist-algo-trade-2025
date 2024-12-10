import streamlit as st
import sqlite3
import requests
import pandas as pd
from datetime import datetime
import warnings
from urllib import request
import ssl

# Veritabanından veri çekme fonksiyonu
def fetch_data():
    conn = sqlite3.connect('db.sqlite3')
    df = pd.read_sql('SELECT * FROM BIST_DATA_G', conn)
    return df

# Streamlit Arayüzü
st.title("Veritabanı İşlemleri")

# Veritabanından veri çekme butonu
if st.button("Verileri Göster"):
    data = fetch_data()
    st.table(data)  # Veriyi tablo olarak gösterir


# Ayarlar
ssl._create_default_https_context = ssl._create_unverified_context
db = "db.sqlite3"
tablo_adi = "BIST_DATA_G"
warnings.filterwarnings("ignore")


def query_run(sorgu):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(sorgu)
    conn.commit()
    conn.close()


def gunun_tarihi():
    return datetime.now().strftime("%Y-%m-%d")


def get_hisse(hisse, baslangic, bitis, periyot, bar):
    dt_baslangic = int(datetime.strptime(baslangic, "%Y-%m-%d").timestamp())
    dt_bitis = int(datetime.strptime(bitis, "%Y-%m-%d").timestamp())
    url = f"https://www.borsadirekt.com/tv/graphdata/history.aspx?symbol={hisse}&resolution={periyot}&from={dt_baslangic}&to={dt_bitis}&countback={bar}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
    else:
        st.error(f"Veri çekme işlemi başarısız oldu. Hata kodu: {response.status_code}")
        return pd.DataFrame()

    df["Tarih"] = pd.to_datetime(df["t"], unit="s").dt.strftime("%Y-%m-%d")
    df = df.drop(columns=["t", "s", "lastBar"])
    df = df.rename(columns={"c": "Close", "o": "Open", "h": "High", "l": "Low", "v": "Hacim"})
    df["Hisse"] = hisse
    df = df[['Tarih', 'Hisse', 'Open', 'Close', 'High', 'Low', 'Hacim']]
    float_columns = df.select_dtypes(include=["float64", "float32"]).columns
    df[float_columns] = df[float_columns].round(2)
    return df


def Hisse_Temel_Veriler():
    url1 = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"
    context = ssl._create_unverified_context()
    response = request.urlopen(url1, context=context)
    url1 = response.read()
    df = pd.read_html(url1, decimal=',', thousands='.')  # Tüm Hisselerin Tablolarını Aktar
    df2 = df[6]
    return df2


# Streamlit Arayüzü
st.title("Borsa Veritabanı Güncelleme")

# Tarih seçimi
baslangic = st.text_input("Başlangıç Tarihi", value="2024-12-01")
bitis = st.text_input("Bitiş Tarihi", value=gunun_tarihi())

# Güncelleme butonu
if st.button("Veritabanını Güncelle"):
    try:
        # Hisselerin listesini al
        df_hisse = Hisse_Temel_Veriler()
        #hisse_liste = df_hisse['Kod'].values.tolist()
        hisse_liste = ['THYAO','ASELS','BIMAS','ENKAI']

        # Veritabanını temizle
        #query_run(f"DELETE FROM {tablo_adi}")

        # Hisseler üzerinde döngü
        for x in hisse_liste:
            try:
                conn_f = sqlite3.connect(db)
                df = get_hisse(x, baslangic, bitis, periyot="1D", bar="100")
                if not df.empty:
                    df.to_sql(tablo_adi, con=conn_f, if_exists='append', index=False)
                conn_f.commit()
                conn_f.close()
            except Exception as e:
                st.warning(f"{x} hissesinde hata oluştu: {e}")
        st.success("Veritabanı başarıyla güncellendi!")
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
