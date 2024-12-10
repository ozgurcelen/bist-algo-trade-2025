import streamlit as st
import sqlite3

# Veritabanından veri çekme fonksiyonu
def fetch_data():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Streamlit Arayüzü
st.title("Veritabanı İşlemleri")

# Veritabanı oluşturma butonu
if st.button("Veritabanı Oluştur"):
    data = fetch_data()
    if data:
        st.write("Tablodaki Veriler:")
        st.table(data)  # Veriyi tablo olarak gösterir
    else:
        st.warning("Veritabanında herhangi bir veri yok!")
