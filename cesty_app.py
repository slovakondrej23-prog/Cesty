import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Evidence jízd", page_icon="🚐")

# Propojení s Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAČÍTÁNÍ DAT ---
def nacti_data():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["Datum", "Auto", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"])

# --- SEZNAM LIDÍ (Můžete si upravit) ---
SEZNAM_LIDI = ["Ondra", "Jonáš", "Vojta", "Míček", "Pinďa", "Kevin","Verča","Marie"]

st.title("🚐 Evidence jízd (Trvalá)")

# --- BOČNÍ PANEL ---
with st.sidebar:
    st.header("Nová jízda")
    auto = st.selectbox("Auto:", ["Auto Ondra", "Auto Jonáš"])
    datum = st.date_input("Datum:", datetime.now())
    cena_celkem = st.number_input("Cena celkem (Kč):", min_value=0, value=2500)
    
    st.write("**Kdo jel?**")
    vybrani_lidi = [osoba for osoba in SEZNAM_LIDI if st.checkbox(osoba, key=f"n_{osoba}")]

# --- HLAVNÍ ČÁST - ZÁPIS ---
if vybrani_lidi:
    pocet = len(vybrani_lidi)
    cena_os = round(cena_celkem / pocet, 2)
    st.info(f"Výpočet: **{cena_os} Kč / osoba**")
    
    if st.button("✅ ULOŽIT JÍZDU DO TABULKY"):
        df_stare = nacti_data()
        novy_radek = pd.DataFrame([{
            "Datum": str(datum),
            "Auto": auto,
            "Celkova_Cena": cena_celkem,
            "Pocet_Lidi": pocet,
            "Cena_na_osobu": cena_os,
            "Jmena": ", ".join(vybrani_lidi)
        }])
        df_vse = pd.concat([df_stare, novy_radek], ignore_index=True)
        conn.update(data=df_vse)
        st.success("Uloženo do Google Sheets!")
        st.balloons()
        st.rerun()

# --- HISTORIE A VYÚČTOVÁNÍ ---
st.divider()
hist = nacti_data()

if not hist.empty:
    tab1, tab2 = st.tabs(["📋 Seznam jízd", "💰 Vyúčtování"])
    
    with tab1:
        st.dataframe(hist, use_container_width=True)
        if st.button("⬅️ Smazat poslední záznam"):
            conn.update(data=hist.drop(hist.index[-1]))
            st.rerun()
            
    with tab2:
        st.subheader("Vyber jízdy k proplacení")
        hist['Datum'] = pd.to_datetime(hist['Datum']).dt.date
        d_od = st.date_input("Od:", hist['Datum'].min())
        d_do = st.date_input("Do:", hist['Datum'].max())
        
        # Filtrovaný výběr
        mask = (hist['Datum'] >= d_od) & (hist['Datum'] <= d_do)
        filtrovana_data = hist.loc[mask].copy()
        filtrovana_data.insert(0, "Vybrat", True)
        
        editovana_data = st.data_editor(filtrovana_data, hide_index=True)
        vyber = editovana_data[editovana_data["Vybrat"] == True]
        
        if not vyber.empty:
            seznam = []
            for _, r in vyber.iterrows():
                for clovek in str(r["Jmena"]).split(", "):
                    if clovek: seznam.append({"Jméno": clovek, "Částka": r["Cena_na_osobu"]})
            
            st.write("### Celkem k vybrání:")
            st.table(pd.DataFrame(seznam).groupby("Jméno")["Částka"].sum().reset_index())
