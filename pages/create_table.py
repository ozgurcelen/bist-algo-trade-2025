import streamlit as st
import sqlite3
import requests
import pandas as pd
from datetime import datetime
import warnings
from urllib import request
import ssl

# Veritabanı oluşturma fonksiyonu
def create_database():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT
        )
    ''')
    conn.commit()
    cursor.executemany('''
        INSERT INTO users (name, age, email)
        VALUES (?, ?, ?)
    ''', [
        ("Ali", 30, "ali@example.com"),
        ("Ayşe", 25, "ayse@example.com"),
        ("Veli", 35, "veli@example.com")
    ])
    conn.commit()
    conn.close()
    st.success("Veritabanı ve tablo başarıyla oluşturuldu!")

# Veritabanından veri çekme fonksiyonu
def fetch_data():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM BIST_DATA_G')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Streamlit Arayüzü
st.title("Veritabanı İşlemleri")

# Veritabanı oluşturma butonu
if st.button("Veritabanı Oluştur"):
    create_database()

# Veritabanından veri çekme butonu
if st.button("Verileri Göster"):
    data = fetch_data()
    if data:
        st.write("Tablodaki Veriler:")
        st.table(data)  # Veriyi tablo olarak gösterir
    else:
        st.warning("Veritabanında herhangi bir veri yok!")


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
baslangic = st.text_input("Başlangıç Tarihi", value="2020-01-01")
bitis = st.text_input("Bitiş Tarihi", value=gunun_tarihi())

# Güncelleme butonu
if st.button("Veritabanını Güncelle"):
    try:
        # Hisselerin listesini al
        df_hisse = Hisse_Temel_Veriler()
        hisse_liste = df_hisse['Kod'].values.tolist()

        # Veritabanını temizle
        #query_run(f"DELETE FROM {tablo_adi}")

        # Hisseler üzerinde döngü
        for x in hisse_liste:
            try:
                conn_f = sqlite3.connect(db)
                df = get_hisse(x, baslangic, bitis, periyot="1D", bar="5000")
                if not df.empty:
                    df.to_sql(tablo_adi, con=conn_f, if_exists='append', index=False)
                conn_f.commit()
                conn_f.close()
            except Exception as e:
                st.warning(f"{x} hissesinde hata oluştu: {e}")
        st.success("Veritabanı başarıyla güncellendi!")
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
