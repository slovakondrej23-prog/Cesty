import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Evidence jizd", page_icon="🚐")

DATA_FILE = "historie_jizd.csv"
PEOPLE_FILE = "seznam_lidi.txt"

# --- FUNKCE PRO NAČÍTÁNÍ ---
def nacti_data():
    columns = ["Datum", "Auto", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "Auto" not in df.columns: df.insert(1, "Auto", "Neznámé")
            return df
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def nacti_lidi():
    if os.path.exists(PEOPLE_FILE):
        with open(PEOPLE_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return ["Petr", "Pavel", "Jana"] # Výchozí seznam, pokud soubor neexistuje

st.title("🚐 Evidence jízd dodávkou")

# --- BOČNÍ PANEL ---
with st.sidebar:
    st.header("👥 Správa posádky")
    stávající_lidi = nacti_lidi()
    novy_seznam = st.text_area("Seznam lidí (každý na nový řádek):", value="\n".join(stávající_lidi))
    if st.button("💾 Uložit seznam lidí"):
        with open(PEOPLE_FILE, "w", encoding="utf-8") as f:
            f.write(novy_seznam)
        st.success("Seznam aktualizován!")
        st.rerun()

    st.divider()
    st.header("🛠️ Správa historie")
    df = nacti_data()
    if not df.empty:
        if st.button("⬅️ Smazat poslední jízdu"):
            df.drop(df.index[-1]).to_csv(DATA_FILE, index=False)
            st.rerun()

# --- HLAVNÍ FORMULÁŘ ---
st.subheader("📍 Nová jízda")
col1, col2 = st.columns(2)
with col1:
    auto = st.selectbox("Auto:", ["Auto Ondra", "Auto Jonáš"])
    datum = st.date_input("Datum:", datetime.now())
with col2:
    celkova_cena = st.number_input("Celková cena (Kč):", min_value=0, value=2500)

st.write("**Kdo jel? (zaškrtni):**")
seznam_pro_vyber = nacti_lidi()
# Vytvoření mřížky pro zaškrtávátka (3 sloupce)
cols = st.columns(3)
vybrani_lidi = []
for i, clovek in enumerate(seznam_pro_vyber):
    with cols[i % 3]:
        if st.checkbox(clovek, key=f"ch_{clovek}"):
            vybrani_lidi.append(clovek)

if vybrani_lidi:
    pocet = len(vybrani_lidi)
    cena_osoba = round(celkova_cena / pocet, 2)
    st.info(f"Jedou {pocet} lidé. Cena na osobu: **{cena_osoba} Kč**")
    
    if st.button("✅ ULOŽIT JÍZDU"):
        df_new = pd.concat([nacti_data(), pd.DataFrame([{
            "Datum": str(datum), "Auto": auto, "Celkova_Cena": celkova_cena, 
            "Pocet_Lidi": pocet, "Cena_na_osobu": cena_osoba, "Jmena": ", ".join(vybrani_lidi)
        }])], ignore_index=True)
        df_new.to_csv(DATA_FILE, index=False)
        st.success("Jízda uložena!")
        st.balloons()
        st.rerun()
else:
    st.warning("Vyberte alespoň jednoho pasažéra.")

# --- HISTORIE A VYÚČTOVÁNÍ ---
st.divider()
historie = nacti_data()
if not historie.empty:
    tab1, tab2 = st.tabs(["📋 Seznam jízd", "💰 Vyúčtování"])
    with tab1:
        st.dataframe(historie, use_container_width=True)
    with tab2:
        seznam_dluhu = []
        for _, radek in historie.iterrows():
            for clovek in str(radek["Jmena"]).split(", "):
                if clovek: seznam_dluhu.append({"Jméno": clovek, "Částka": radek["Cena_na_osobu"]})
        if seznam_dluhu:
            souhrn = pd.DataFrame(seznam_dluhu).groupby("Jméno")["Částka"].sum().reset_index()
            st.table(souhrn.sort_values(by="Částka", ascending=False).style.format({"Částka": "{:.2f} Kč"}))
