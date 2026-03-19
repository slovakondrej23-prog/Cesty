import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Evidence jizd", page_icon="🚐")

st.title("🚐 Evidence s uložením do Google Sheets")

# Propojení s tabulkou
conn = st.connection("gsheets", type=GSheetsConnection)

# Vstupy v bočním panelu
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
        try:
            # 1. Načteme aktuální data (pokud existují)
            try:
                stary_df = conn.read()
            except:
                stary_df = pd.DataFrame(columns=["Datum", "Celkova_Cena", "Pocet_Lidi", "Cena_na_osobu", "Jmena"])
            
            # 2. Připravíme nový řádek
            nova_data = pd.DataFrame([{
                "Datum": str(datum),
                "Celkova_Cena": celkova_cena,
                "Pocet_Lidi": pocet,
                "Cena_na_osobu": cena_osoba,
                "Jmena": ", ".join(pasazeri)
            }])
            
            # 3. Spojíme je
            aktualizovany_df = pd.concat([stary_df, nova_data], ignore_index=True)
            
            # 4. Zapíšeme zpět (použijeme metodu create pro jistotu)
            conn.create(data=aktualizovany_df)
            st.success("Uloženo do Google Tabulky!")
            st.balloons() # Malá oslava úspěchu!
        except Exception as e:
            st.error(f"Chyba při ukládání: {e}")

# Zobrazení historie pod čarou
st.divider()
st.subheader("📜 Historie jízd")
try:
    # Přidáme ttl=0, aby se historie po uložení hned obnovila
    historie = conn.read(ttl=0)
    st.dataframe(historie, use_container_width=True)
except Exception as e:
    st.write("Zatím žádná historie k zobrazení.")
