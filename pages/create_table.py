import streamlit as st
import sqlite3

# Veritabanı oluşturma fonksiyonu
def create_database():
    conn = sqlite3.connect('db.sqlite3')
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
    cursor.execute('SELECT * FROM users')
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
