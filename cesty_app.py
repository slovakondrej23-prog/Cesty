import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Evidence jizd", page_icon="🚐")

DATA_FILE = "historie_jizd.csv"

def nacti_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["Datum", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"])
    return pd.DataFrame(columns=["Datum", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"])

st.title("🚐 Evidence jízd dodávkou")

# --- BOČNÍ PANEL (VSTUPY A MAZÁNÍ) ---
with st.sidebar:
    st.header("Nová jízda")
    datum = st.date_input("Datum", datetime.now())
    celkova_cena = st.number_input("Celková cena (Kč)", min_value=0, value=2500)
    jmena_vstup = st.text_area("Jména (oddělená čárkou)")
    
    st.divider()
    st.header("🛠️ Správa historie")
    
    df = nacti_data()
    
    if not df.empty:
        # 1. Tlačítko pro smazání úplně posledního řádku
        if st.button("⬅️ Smazat poslední jízdu"):
            df = df.drop(df.index[-1])
            df.to_csv(DATA_FILE, index=False)
            st.warning("Poslední jízda byla smazána.")
            st.rerun()
            
        st.divider()
        # 2. Výběr konkrétní jízdy ke smazání
        index_ke_smazani = st.number_input("Smazat jízdu č. (dle tabulky):", min_value=0, max_value=len(df)-1, step=1)
        if st.button("🗑️ Smazat vybranou jízdu"):
            df = df.drop(df.index[index_ke_smazani])
            df.to_csv(DATA_FILE, index=False)
            st.error(f"Jízda č. {index_ke_smazani} byla smazána.")
            st.rerun()

# --- HLAVNÍ PLOCHA (VÝPOČET) ---
pasazeri = [p.strip() for p in jmena_vstup.replace('\n', ',').split(',') if p.strip()]

if pasazeri:
    pocet = len(pasazeri)
    cena_osoba = round(celkova_cena / pocet, 2)
    st.metric("Cena na osobu", f"{cena_osoba} Kč")
    
    if st.button("✅ Uložit do historie"):
        df_aktualni = nacti_data()
        novy_radek = pd.DataFrame([{
            "Datum": str(datum),
            "Celkova_Cena": celkova_cena,
            "Pocet_Lidi": pocet,
            "Cena_na_osobu": cena_osoba,
            "Jmena": ", ".join(pasazeri)
        }])
        df_aktualni = pd.concat([df_aktualni, novy_radek], ignore_index=True)
        df_aktualni.to_csv(DATA_FILE, index=False)
        st.success("Uloženo!")
        st.rerun()

# --- ZOBRAZENÍ TABULKY ---
st.divider()
st.subheader("📜 Historie jízd")
historie = nacti_data()

if not historie.empty:
    # Zobrazíme tabulku i s indexy (čísly řádků), aby uživatel věděl, co mazat
    st.dataframe(historie, use_container_width=True)
    
    csv = historie.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Stáhnout historii (CSV)",
        data=csv,
        file_name=f"historie_dodavka.csv",
        mime="text/csv",
    )
else:
    st.info("Zatím nemáte uloženy žádné jízdy.")
