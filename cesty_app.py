import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Evidence jizd", page_icon="🚐")

# Název souboru, kde budou data uložena přímo na serveru
DATA_FILE = "historie_jizd.csv"

# Funkce pro načtení dat ze souboru
def nacti_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["Datum", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"])
    return pd.DataFrame(columns=["Datum", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"])

st.title("🚐 Evidence jízd dodávkou")

# Vstupy v bočním panelu
with st.sidebar:
    st.header("Nová jízda")
    datum = st.date_input("Datum", datetime.now())
    celkova_cena = st.number_input("Celková cena (Kč)", min_value=0, value=2500)
    jmena_vstup = st.text_area("Jména (oddělená čárkou nebo novým řádkem)")

# Zpracování jmen
pasazeri = [p.strip() for p in jmena_vstup.replace('\n', ',').split(',') if p.strip()]

if pasazeri:
    pocet = len(pasazeri)
    cena_osoba = round(celkova_cena / pocet, 2)
    st.metric("Cena na osobu", f"{cena_osoba} Kč")
    
    if st.button("✅ Uložit do historie"):
        df = nacti_data()
        novy_radek = pd.DataFrame([{
            "Datum": str(datum),
            "Celkova_Cena": celkova_cena,
            "Pocet_Lidi": pocet,
            "Cena_na_osobu": cena_osoba,
            "Jmena": ", ".join(pasazeri)
        }])
        df = pd.concat([df, novy_radek], ignore_index=True)
        # Uložíme soubor přímo do úložiště aplikace
        df.to_csv(DATA_FILE, index=False)
        st.success("Uloženo do paměti!")
        st.balloons()
        st.rerun()

# Zobrazení historie
st.divider()
st.subheader("📜 Historie jízd")
historie = nacti_data()

if not historie.empty:
    st.dataframe(historie, use_container_width=True)
    # Tlačítko pro stažení zálohy
    csv = historie.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Stáhnout historii do Excelu (CSV)",
        data=csv,
        file_name=f"historie_dodavka_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )
else:
    st.info("Zatím nemáte uloženy žádné jízdy.")
