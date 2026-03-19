import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Dodávka s historií", page_icon="🚐")

st.title("🚐 Evidence s uložením do Google Sheets")

# Propojení s tabulkou
conn = st.connection("gsheets", type=GSheetsConnection)

# Vstupy
with st.sidebar:
    st.header("Nová jízda")
    datum = st.date_input("Datum", datetime.now())
    celkova_cena = st.number_input("Celková cena (Kč)", min_value=0, value=2500)
    jmena_vstup = st.text_area("Jména (oddělená čárkou)")

pasazeri = [p.strip() for p in jmena_vstup.replace('\n', ',').split(',') if p.strip()]

if pasazeri:
    pocet = len(pasazeri)
    cena_osoba = round(celkova_cena / pocet, 2)
    
    st.metric("Cena na osobu", f"{cena_osoba} Kč")
    
    if st.button("✅ Uložit jízdu do historie"):
        # Příprava dat pro zápis
        nova_data = pd.DataFrame([{
            "Datum": str(datum),
            "Celkova_Cena": celkova_cena,
            "Pocet_Lidi": pocet,
            "Cena_na_osobu": cena_osoba,
            "Jmena": ", ".join(pasazeri)
        }])
        
        # Načtení stávajících dat a přidání nových
        stary_df = conn.read()
        aktualizovany_df = pd.concat([stary_df, nova_data], ignore_index=True)
        
        # Zápis zpět do Google Sheet
        conn.update(data=aktualizovany_df)
        st.success("Uloženo do Google Tabulky!")

# Zobrazení historie
st.divider()
st.subheader("📜 Historie jízd")
try:
    historie = conn.read()
    st.dataframe(historie, use_container_width=True)
except:
    st.write("Zatím žádná historie k zobrazení.")
