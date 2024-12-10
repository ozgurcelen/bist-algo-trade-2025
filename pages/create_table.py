import streamlit as st
import sqlite3

def create_database():
    # Veritabanını oluştur veya bağlan
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    # Örnek bir tablo oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()
    st.success("Veritabanı ve tablo başarıyla oluşturuldu!")

# Streamlit Arayüzü
st.title("Veritabanı Oluşturma Uygulaması")

if st.button("Veritabanı Oluştur"):
    create_database()

