import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Evidence jizd", page_icon="🚐")

DATA_FILE = "historie_jizd.csv"
PEOPLE_FILE = "seznam_lidi.txt"

# --- NAČÍTÁNÍ ---
def nacti_data():
    columns = ["Datum", "Auto", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df['Datum'] = pd.to_datetime(df['Datum']).dt.date
            return df
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def nacti_lidi():
    if os.path.exists(PEOPLE_FILE):
        with open(PEOPLE_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return ["Petr", "Pavel"]

st.title("🚐 Evidence s výběrem vyúčtování")

# --- BOČNÍ PANEL (Zůstává stejný) ---
with st.sidebar:
    st.header("👥 Posádka")
    lidi = nacti_lidi()
    novy_seznam = st.text_area("Seznam lidí:", value="\n".join(lidi))
    if st.button("💾 Uložit lidi"):
        with open(PEOPLE_FILE, "w", encoding="utf-8") as f: f.write(novy_seznam)
        st.rerun()
    st.divider()
    if st.button("⬅️ Smazat poslední jízdu"):
        df = nacti_data()
        if not df.empty:
            df.drop(df.index[-1]).to_csv(DATA_FILE, index=False)
            st.rerun()

# --- FORMULÁŘ JÍZDY ---
st.subheader("📍 Nová jízda")
col1, col2, col3 = st.columns(3)
with col1: auto = st.selectbox("Auto:", ["Dodávka 1", "Dodávka 2"])
with col2: datum = st.date_input("Datum:", datetime.now())
with col3: celkova_cena = st.number_input("Cena (Kč):", min_value=0, value=2500)

vybrani_lidi = [c for c in lidi if st.sidebar.checkbox(c, key=f"n_{c}")] # Přesunuto do sidebar pro místo

if vybrani_lidi:
    cena_osoba = round(celkova_cena / len(vybrani_lidi), 2)
    st.info(f"Cena: **{cena_osoba} Kč/osoba**")
    if st.button("✅ ULOŽIT JÍZDU"):
        df_new = pd.concat([nacti_data(), pd.DataFrame([{"Datum": datum, "Auto": auto, "Celkova_Cena": celkova_cena, "Pocet_Lidi": len(vybrani_lidi), "Cena_na_osobu": cena_osoba, "Jmena": ", ".join(vybrani_lidi)}])], ignore_index=True)
        df_new.to_csv(DATA_FILE, index=False)
        st.success("Uloženo!")
        st.rerun()

# --- HISTORIE A FILTROVANÉ VYÚČTOVÁNÍ ---
st.divider()
historie = nacti_data()

if not historie.empty:
    tab1, tab2 = st.tabs(["📋 Všechny jízdy", "💰 Výběrové vyúčtování"])
    
    with tab1:
        st.dataframe(historie, use_container_width=True)
    
    with tab2:
        st.subheader("Vyber jízdy k proplacení")
        
        # 1. Filtr podle data
        col_f1, col_f2 = st.columns(2)
        with col_f1: d_od = st.date_input("Od:", historie['Datum'].min())
        with col_f2: d_do = st.date_input("Do:", historie['Datum'].max())
        
        # 2. Zobrazení tabulky s možností výběru řádků
        mask = (historie['Datum'] >= d_od) & (historie['Datum'] <= d_do)
        data_k_vyberu = historie.loc[mask].copy()
        
        # Přidáme sloupec pro zaškrtnutí přímo v tabulce
        data_k_vyberu.insert(0, "Vybrat", True)
        upravena_tabulka = st.data_editor(
            data_k_vyberu,
            column_config={"Vybrat": st.column_config.CheckboxColumn(default=True)},
            disabled=["Datum", "Auto", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"],
            hide_index=True,
        )
        
        # 3. Výpočet jen z vybraných řádků
        vybrane_jizdy = upravena_tabulka[upravena_tabulka["Vybrat"] == True]
        
        if not vybrane_jizdy.empty:
            seznam_dluhu = []
            for _, radek in vybrane_jizdy.iterrows():
                for clovek in str(radek["Jmena"]).split(", "):
                    if clovek: seznam_dluhu.append({"Jméno": clovek, "Částka": radek["Cena_na_osobu"]})
            
            st.write("### Celkem k zaplacení za vybrané období:")
            souhrn = pd.DataFrame(seznam_dluhu).groupby("Jméno")["Částka"].sum().reset_index()
            st.table(souhrn.sort_values(by="Částka", ascending=False).style.format({"Částka": "{:.2f} Kč"}))
        else:
            st.warning("Žádné jízdy nejsou vybrány.")
