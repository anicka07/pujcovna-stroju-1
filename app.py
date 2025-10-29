import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd

# ===== Nastavení databáze =====
DB_PATH = Path("pujcovna.db")

# Vytvoření a naplnění databáze při prvním spuštění
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabulka strojů
    c.execute("""CREATE TABLE IF NOT EXISTS stroje (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazev TEXT,
        popis TEXT,
        cena_za_den REAL,
        dostupnost INTEGER
    )""")

    # Tabulka klientů
    c.execute("""CREATE TABLE IF NOT EXISTS klienti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazev TEXT,
        adresa TEXT,
        ico TEXT,
        sleva REAL,
        kontakt TEXT
    )""")

    # Naplnit ukázkovými daty (jen pokud prázdné)
    c.execute("SELECT COUNT(*) FROM stroje")
    if c.fetchone()[0] == 0:
        data_stroje = [
            ("Bagr CAT 320", "Střední pásový bagr", 3500, 1),
            ("Nakladač JCB 3CX", "Kolový nakladač", 2800, 1),
            ("Vibrační deska Wacker", "Hutnící deska 200 kg", 900, 0),
            ("Míchačka Altrad 190L", "Míchačka betonu", 450, 1),
            ("Řezačka dlaždic Bosch GDC", "Elektrická řezačka", 250, 1),
            ("Vibrační pěch Bomag", "Ruční pěch", 700, 0),
            ("Minibagr Kubota U17", "Kompaktní bagr", 2600, 1),
            ("Lešení rámové 50 m²", "Sada rámového lešení", 1200, 1),
            ("Generátor Honda 5 kW", "Elektrocentrála", 1000, 0),
            ("Vysokotlaký čistič Kärcher", "Průmyslový čistič", 650, 1)
        ]
        c.executemany(
            "INSERT INTO stroje (nazev, popis, cena_za_den, dostupnost) VALUES (?, ?, ?, ?)", 
            data_stroje
        )

    c.execute("SELECT COUNT(*) FROM klienti")
    if c.fetchone()[0] == 0:
        data_klienti = [
            ("Stavby Praha s.r.o.", "Praha 5", "12345678", 10, "Jan Novák"),
            ("Beton CZ a.s.", "Brno", "87654321", 5, "Petra Malá"),
            ("StavInvest a.s.", "Plzeň", "23456789", 8, "Lukáš Černý")
        ]
        c.executemany(
            "INSERT INTO klienti (nazev, adresa, ico, sleva, kontakt) VALUES (?, ?, ?, ?, ?)", 
            data_klienti
        )

    conn.commit()
    conn.close()

init_db()

# ===== Streamlit aplikace =====
st.set_page_config(page_title="Půjčovna strojů", layout="wide", page_icon="🚜")
st.title("🚜 Půjčovna stavebních strojů")

# Načíst data
conn = sqlite3.connect(DB_PATH)
stroje = pd.read_sql("SELECT * FROM stroje", conn)
klienti = pd.read_sql("SELECT * FROM klienti", conn)
conn.close()

menu = st.sidebar.radio("Menu", ["Formulář", "Seznam strojů", "Seznam klientů"])

if menu == "Formulář":
    st.header("Výpočet půjčovného")

    klient = st.selectbox("Vyberte klienta", klienti["nazev"])
    stroj = st.selectbox("Vyberte stroj", stroje["nazev"])
    dny = st.number_input("Počet dní", min_value=1, value=1)

    sleva = klienti.loc[klienti["nazev"] == klient, "sleva"].values[0]
    cena_den = stroje.loc[stroje["nazev"] == stroj, "cena_za_den"].values[0]
    dostupnost = stroje.loc[stroje["nazev"] == stroj, "dostupnost"].values[0]

    if dostupnost == 1:
        st.success("Stroj je dostupný ✅")
        celkem = dny * cena_den * (1 - sleva / 100)
        st.metric("Celková cena (po slevě)", f"{celkem:,.0f} Kč")
    else:
        st.error("Tento stroj momentálně není dostupný ❌")

elif menu == "Seznam strojů":
    st.header("Seznam strojů")
    st.dataframe(stroje)

elif menu == "Seznam klientů":
    st.header("Seznam klientů")
    st.dataframe(klienti)
