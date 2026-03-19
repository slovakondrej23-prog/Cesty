import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Evidence jizd", page_icon="🚐")

DATA_FILE = "historie_jizd.csv"

def nacti_data():
    columns = ["Datum", "Auto", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Pokud v souboru chybí sloupec Auto (ze starších verzí), přidáme ho
            if "Auto" not in df.columns:
                df.insert(1, "Auto", "Neznámé")
            return df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

st.title("🚐 Evidence jízd dodávkou")

# --- BOČNÍ PANEL ---
with st.sidebar:
    st.header("Nastavení jízdy")
    
    # VÝBĚR AUTA
    auto = st.selectbox("Vyber auto:", ["Dodávka 1 (Bílá)", "Dodávka 2 (Modrá)"])
    
    datum = st.date_input("Datum", datetime.now())
    celkova_cena = st.number_input("Celková cena (Kč)", min_value=0, value=2500)
    jmena_vstup = st.text_area("Jména (oddělená čárkou)")
    
    st.divider()
    st.header("🛠️ Správa historie")
    df = nacti_data()
    
    if not df.empty:
        if st.button("⬅️ Smazat poslední jízdu"):
            df = df.drop(df.index[-1])
            df.to_csv(DATA_FILE, index=False)
            st.warning("Poslední jízda smazána.")
            st.rerun()
            
        index_ke_smazani = st.number_input("Smazat jízdu č.:", min_value=0, max_value=len(df)-1, step=1)
        if st.button("🗑️ Smazat vybranou"):
            df = df.drop(df.index[index_ke_smazani])
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- VÝPOČET ---
pasazeri = [p.strip() for p in jmena_vstup.replace('\n', ',').split(',') if p.strip()]

if pasazeri:
    pocet = len(pasazeri)
    cena_osoba = round(celkova_cena / pocet, 2)
    st.metric(f"Cena na osobu ({auto})", f"{cena_osoba} Kč")
    
    if st.button("✅ Uložit do historie"):
        df_aktualni = nacti_data()
        novy_radek = pd.DataFrame([{
            "Datum": str(datum),
            "Auto": auto,
            "Celkova_Cena": celkova_cena,
            "Pocet_Lidi": pocet,
            "Cena_na_osobu": cena_osoba,
            "Jmena": ", ".join(pasazeri)
        }])
        df_aktualni = pd.concat([df_aktualni, novy_radek], ignore_index=True)
        df_aktualni.to_csv(DATA_FILE, index=False)
        st.success(f"Uloženo pro {auto}!")
        st.rerun()

# --- FILTR A TABULKA ---
st.divider()
st.subheader("📜 Historie jízd")
historie = nacti_data()

if not historie.empty:
    # FILTR V TABULCE
    filtr_auto = st.multiselect("Zobrazit jen auta:", options=historie["Auto"].unique(), default=historie["Auto"].unique())
    zobrazena_data = historie[historie["Auto"].isin(filtr_auto)]
    
    st.dataframe(zobrazena_data, use_container_width=True)
    
    csv = zobrazena_data.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Stáhnout tento výběr (CSV)", data=csv, file_name="export_jizd.csv")
else:
    st.info("Zatím žádné jízdy.")
