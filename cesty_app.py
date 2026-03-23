import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Evidence dodávky", page_icon="🚐")

# PROPOJENÍ
conn = st.connection("gsheets", type=GSheetsConnection)

# FUNKCE
def nacti_data():
    return conn.read(ttl=0)

def nacti_lidi():
    # Seznam lidí si pro jednoduchost necháme v kódu, nebo ho dejte do druhého listu v tabulce
    return ["Petr", "Pavel", "Honza", "Lucka", "Marek"]

st.title("🚐 Trvalá evidence jízd")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Nastavení")
    lidi = nacti_lidi()
    vybrani_lidi = [clovek for clovek in lidi if st.checkbox(clovek, key=f"n_{clovek}")]
    
    st.divider()
    if st.button("⬅️ Smazat poslední řádek v Google tabulce"):
        df = nacti_data()
        if not df.empty:
            df = df.drop(df.index[-1])
            conn.update(data=df)
            st.rerun()

# --- FORMULÁŘ ---
col1, col2, col3 = st.columns(3)
with col1: auto = st.selectbox("Auto:", ["Auto Ondra", "Auto Jonáš"])
with col2: datum = st.date_input("Datum:", datetime.now())
with col3: cena_celkem = st.number_input("Cena (Kč):", min_value=0, value=2500)

if vybrani_lidi:
    cena_os = round(cena_celkem / len(vybrani_lidi), 2)
    st.info(f"Cena: {cena_os} Kč/osoba")
    if st.button("✅ ULOŽIT DO GOOGLE TABULKY"):
        df_old = nacti_data()
        novy_radek = pd.DataFrame([{"Datum": str(datum), "Auto": auto, "Celkova_Cena": cena_celkem, "Pocet_Lidi": len(vybrani_lidi), "Cena_na_osobu": cena_os, "Jmena": ", ".join(vybrani_lidi)}])
        df_final = pd.concat([df_old, novy_radek], ignore_index=True)
        conn.update(data=df_final)
        st.success("Zapsáno do tabulky!")
        st.balloons()
        st.rerun()

# --- VYÚČTOVÁNÍ ---
st.divider()
hist = nacti_data()
if not hist.empty:
    t1, t2 = st.tabs(["📋 Historie", "💰 Vyúčtování"])
    with t1: st.dataframe(hist, use_container_width=True)
    with t2:
        # Filtrované vyúčtování (stejné jako minule)
        d_od = st.date_input("Od:", pd.to_datetime(hist['Datum']).min())
        d_do = st.date_input("Do:", pd.to_datetime(hist['Datum']).max())
        hist['Datum_dt'] = pd.to_datetime(hist['Datum']).dt.date
        mask = (hist['Datum_dt'] >= d_od) & (hist['Datum_dt'] <= d_do)
        vyber = hist.loc[mask].copy()
        vyber.insert(0, "Vybrat", True)
        ed = st.data_editor(vyber, hide_index=True)
        final_vyber = ed[ed["Vybrat"] == True]
        
        dluhy = []
        for _, r in final_vyber.iterrows():
            for c in str(r["Jmena"]).split(", "):
                if c: dluhy.append({"Jméno": c, "Částka": r["Cena_na_osobu"]})
        if dluhy:
            st.table(pd.DataFrame(dluhy).groupby("Jméno")["Částka"].sum().reset_index())
