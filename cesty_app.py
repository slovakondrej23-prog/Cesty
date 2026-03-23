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
            if "Auto" not in df.columns:
                df.insert(1, "Auto", "Neznámé")
            return df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

st.title("🚐 Evidence jízd dodávkou")

# --- BOČNÍ PANEL ---
with st.sidebar:
    st.header("Nová jízda")
    auto = st.selectbox("Vyber auto:", ["Dodávka 1", "Dodávka 2"]) # Tady si upravte názvy
    datum = st.date_input("Datum", datetime.now())
    celkova_cena = st.number_input("Celková cena (Kč)", min_value=0, value=2500)
    jmena_vstup = st.text_area("Jména (oddělená čárkou)")
    
    st.divider()
    st.header("🛠️ Správa")
    df = nacti_data()
    if not df.empty:
        if st.button("⬅️ Smazat poslední jízdu"):
            df.drop(df.index[-1]).to_csv(DATA_FILE, index=False)
            st.rerun()

# --- VÝPOČET A ULOŽENÍ ---
pasazeri = [p.strip() for p in jmena_vstup.replace('\n', ',').split(',') if p.strip()]
if pasazeri:
    cena_osoba = round(celkova_cena / len(pasazeri), 2)
    st.metric(f"Cena na osobu", f"{cena_osoba} Kč")
    if st.button("✅ Uložit do historie"):
        df_new = pd.concat([nacti_data(), pd.DataFrame([{"Datum": str(datum), "Auto": auto, "Celkova_Cena": celkova_cena, "Pocet_Lidi": len(pasazeri), "Cena_na_osobu": cena_osoba, "Jmena": ", ".join(pasazeri)}])], ignore_index=True)
        df_new.to_csv(DATA_FILE, index=False)
        st.success("Uloženo!")
        st.rerun()

# --- HISTORIE A VYÚČTOVÁNÍ ---
st.divider()
historie = nacti_data()

if not historie.empty:
    tab1, tab2 = st.tabs(["📋 Seznam jízd", "💰 Vyúčtování osob"])
    
    with tab1:
        filtr_auto = st.multiselect("Filtr aut:", options=historie["Auto"].unique(), default=historie["Auto"].unique())
        st.dataframe(historie[historie["Auto"].isin(filtr_auto)], use_container_width=True)
    
    with tab2:
        st.subheader("Celkové částky podle jmen")
        # Výpočet sumy pro každého pasažéra
        seznam_dluhu = []
        for _, radek in historie.iterrows():
            lidi_v_jizde = [j.strip() for j in str(radek["Jmena"]).split(",")]
            for clovek in lidi_v_jizde:
                if clovek:
                    seznam_dluhu.append({"Jméno": clovek, "Částka": radek["Cena_na_osobu"]})
        
        if seznam_dluhu:
            df_dluhy = pd.DataFrame(seznam_dluhu)
            souhrn = df_dluhy.groupby("Jméno")["Částka"].sum().reset_index()
            souhrn = souhrn.sort_values(by="Částka", ascending=False)
            
            # Zobrazení výsledků
            st.table(souhrn.style.format({"Částka": "{:.2f} Kč"}))
            st.info("💡 Tip: Toto jsou celkové sumy za všechna auta a všechna data v historii.")
        else:
            st.write("Zatím žádná data.")
else:
    st.info("Zatím žádné jízdy k zobrazení.")
