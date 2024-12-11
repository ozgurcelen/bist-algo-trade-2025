import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# get_hisse fonksiyonu
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
        return None

    df["Tarih"] = pd.to_datetime(df["t"], unit="s")
    df["Tarih"] = pd.to_datetime(df["Tarih"]).dt.strftime("%Y-%m-%d")
    df = df.drop(columns=["t", "s", "lastBar"], errors="ignore")
    df = df.rename(columns={"c": "Close", "o": "Open", "h": "High", "l": "Low", "v": "Hacim"})
    df["Hisse"] = hisse
    df = df[['Tarih', 'Hisse', 'Open', 'Close', 'High', 'Low', 'Hacim']]
    float_columns = df.select_dtypes(include=["float64", "float32"]).columns
    df[float_columns] = df[float_columns].round(2)
    return df

# Streamlit uygulaması
st.title("Bist Algo Trade")

# Kullanıcıdan giriş al
hisse = st.text_input("Hisse Kodu:", "KOZAL")
baslangic = st.date_input("Başlangıç Tarihi", datetime(2024, 1, 1))
bitis = st.date_input("Bitiş Tarihi", datetime(2024, 12, 10))
periyot = st.selectbox("Periyot", ["1", "5", "15", "30", "60", "D"], index=5)
bar = st.number_input("Çubuk Sayısı (Bar)", min_value=1, value=100)

# Butona tıklayınca veri çek
if st.button("Verileri Getir"):
    df = get_hisse(hisse, baslangic.strftime("%Y-%m-%d"), bitis.strftime("%Y-%m-%d"), periyot, bar)
    if df is not None:
        st.write("Hisse Verileri")
        st.dataframe(df)
    else:
        st.error("Veri çekilemedi. Lütfen tekrar deneyin.")

def example_metric():
    col1, col2, col3,col4,col5 = st.columns(5)

    col1.metric(label="Gain", value=5000, delta=1000)
    col2.metric(label="Loss", value=5000, delta=-1000)
    col3.metric(label="BIST", value=9350, delta=250)
    col4.metric(label="BIST30", value=13250, delta=511)
    col5.metric(label="STREND", value=11950, delta=1125)


example_metric()