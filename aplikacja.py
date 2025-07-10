import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# --- Konfiguracja Aplikacji ---
st.set_page_config(
    page_title="Nawyki Zespołowe",
    page_icon="✨",
    layout="wide"
)

# --- Połączenie z Bazą Danych (Google Sheets) ---
# Używamy wbudowanych sekretów Streamlit do bezpiecznego połączenia
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Funkcje do Danych (nowa wersja) ---
def load_data():
    try:
        zespol_df = conn.read(worksheet="Zespol", usecols=[0, 1], ttl=5)
        nawyki_df = conn.read(worksheet="Nawyki", usecols=[0, 1], ttl=5)
        wpisy_df = conn.read(worksheet="Wpisy", usecols=[0, 1, 2, 3], ttl=5)
        
        # Usuwamy puste wiersze, które mogą pojawić się w Google Sheets
        zespol_df.dropna(how="all", inplace=True)
        nawyki_df.dropna(how="all", inplace=True)
        wpisy_df.dropna(how="all", inplace=True)

    except Exception as e:
        st.error(f"Błąd wczytywania danych z Google Sheets: {e}")
        # Tworzymy puste ramki danych w razie błędu, aby aplikacja się nie zawiesiła
        zespol_df = pd.DataFrame(columns=['ID_Osoby', 'Imie'])
        nawyki_df = pd.DataFrame(columns=['ID_Nawyku', 'Opis'])
        wpisy_df = pd.DataFrame(columns=['Data', 'ID_Osoby', 'ID_Nawyku', 'Odpowiedz'])

    # Konwersja typów danych
    zespol_df['ID_Osoby'] = pd.to_numeric(zespol_df['ID_Osoby'])
    nawyki_df['ID_Nawyku'] = pd.to_numeric(nawyki_df['ID_Nawyku'])
    
    st.session_state['zespol_df'] = zespol_df
    st.session_state['nawyki_df'] = nawyki_df
    st.session_state['wpisy_df'] = wpisy_df

def save_data(data_frame, worksheet_name):
    """Zapisuje cały DataFrame do określonego arkusza, nadpisując go."""
    conn.write(worksheet=worksheet_name, data=data_frame)

def append_data(data_frame, worksheet_name):
    """Dopisuje nowe wiersze do określonego arkusza."""
    conn.append(worksheet=worksheet_name, data=data_frame)

def calculate_streak(series):
    streak = 0
    for val in reversed(series.tolist()):
        if val == 'Tak': streak += 1
        elif val == 'Nie': break
    return streak

# --- Style CSS (bez zmian) ---
# ... (cały blok CSS pozostaje taki sam jak w poprzedniej wersji) ...
KOLOR_TLA = '#FFFFFF'
KOLOR_TEKSTU = '#052852'
KOLOR_AKCENTU = '#00b6db'
KOLOR_ZIELONY = '#2ECC40'
KOLOR_CZERWONY = '#FF4136'
KOLOR_SZARY = '#AAAAAA'
css_content = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Unna:wght@400;700&display=swap');
    :root {{
        --primary-color: {KOLOR_AKCENTU};
        --background-color: {KOLOR_TLA};
        --secondary-background-color: #F0F2F6;
        --text-color: {KOLOR_TEKSTU};
        --font-heading: 'Unna', serif;
        --font-body: 'Poppins', sans-serif;
    }}
    .stApp, .stApp div, .stApp span, .stApp p {{ font-family: var(--font-body); color: var(--text-color); }}
    h1, h2, h3 {{ font-family: var(--font-heading); color: var(--text-color); font-weight: 700; }}
    .stApp {{ background-color: var(--background-color); }}
    .stButton>button {{ color: #FFFFFF; background-color: {KOLOR_AKCENTU}; border: 2px solid {KOLOR_AKCENTU}; border-radius: 8px; transition: all 0.2s; font-family: var(--font-body); font-weight: 600; }}
    .stButton>button:hover {{ background-color: '#008fb5'; border-color: '#008fb5'; color: #FFFFFF; }}
    .habit-tracker-table {{ width: 100%; border-collapse: collapse; margin-bottom: 2rem; }}
    .habit-tracker-table th, .habit-tracker-table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; min-width: 40px; }}
    .habit-tracker-table th:first-child, .habit-tracker-table td:first-child {{ text-align: left; width: 40%; }}
    .habit-tracker-table th {{ background-color: #f2f2f2; font-family: var(--font-body); font-weight: 600; }}
    .habit-square {{ display: inline-block; width: 20px; height: 20px; border-radius: 3px; }}
    .square-green {{ background-color: {KOLOR_ZIELONY}; }}
    .square-red {{ background-color: {KOLOR_CZERWONY}; }}
    .square-gray {{ background-color: {KOLOR_SZARY}; }}
    .square-empty {{ background-color: #f9f9f9; }}
    .plotly .g-ytitle {{ display: none; }}
</style>
"""
st.markdown(css_content, unsafe_allow_html=True)

# --- Główna Aplikacja ---
load_data()

st.title("✨ Nawyki Zespołowe")
with st.sidebar:
    st.markdown("""<style>[data-testid="stSidebar"] {background-color: #F0F2F6;}</style>""", unsafe_allow_html=True)
    st.title("Menu")
    strona = st.radio(
        "Wybierz, co chcesz zrobić:",
        ["Jak nam poszło?", "Nasze Postępy", "Ustawienia"],
        captions=["Rejestracja wyników", "Analiza i trendy", "Zarządzanie aplikacją"]
    )

if strona == "Nasze Postępy":
    st.header("Zobaczmy nasze postępy!")
    if st.session_state.wpisy_df.empty:
        st.info("Brak danych do analizy. Dodaj pierwszy wpis w sekcji 'Jak nam poszło?'.")
    else:
        # Reszta kodu dashboardu jest prawie identyczna
        dane = pd.merge(st.session_state.wpisy_df, st.session_state.zespol_df, on='ID_Osoby')
        dane = pd.merge(dane, st.session_state.nawyki_df, on='ID_Nawyku')
        dane['Data'] = pd.to_datetime(dane['Data'])
        # ... (cały kod dashboardu pozostaje bez zmian) ...
        with st.sidebar:
            st.header("Filtry")
            wszystkie_osoby = ['Wszyscy'] + sorted(dane['Imie'].unique().tolist())
            wybrane_osoby_filtr = st.multiselect("Pokaż wyniki dla:", wszystkie_osoby, default='Wszyscy')
            if 'Wszyscy' in wybrane_osoby_filtr: filtrowane_dane = dane
            else: filtrowane_dane = dane[dane['Imie'].isin(wybrane_osoby_filtr)]
        st.subheader("🗓️ Tracker nawyków")
        dni_do_pokazania = st.select_slider("Pokaż ostatnie dni:", options=[7, 14, 30, 60], value=14)
        data_koncowa = datetime.now()
        data_poczatkowa = data_koncowa - timedelta(days=dni_do_pokazania - 1)
        zakres_dat = pd.date_range(start=data_poczatkowa, end=data_koncowa, freq='D')
        dane_trackera = filtrowane_dane.copy()
        if dane_trackera.empty:
            st.info("Brak danych do wyświetlenia dla wybranych filtrów.")
        else:
            for osoba in sorted(dane_trackera['Imie'].unique()):
                st.markdown(f"#### Tracker dla: **{osoba}**")
                dane_osoby = dane_trackera[dane_trackera['Imie'] == osoba]
                pivot_table = dane_osoby.pivot_table(index='Opis', columns=dane_osoby['Data'].dt.date, values='Odpowiedz', aggfunc='first')
                pivot_table = pivot_table.reindex(columns=zakres_dat.date, fill_value=None)
                html_table = "<table class='habit-tracker-table'><thead><tr><th>Nawyk</th>"
                for data in pivot_table.columns:
                    html_table += f"<th>{data.strftime('%d/%m')}</th>"
                html_table += "<th>Streak</th></tr></thead><tbody>"
                mapowanie_css = {'Tak': 'square-green', 'Nie': 'square-red', 'Nie było takiej sytuacji': 'square-gray'}
                for nawyk, row in pivot_table.iterrows():
                    html_table += f"<tr><td>{nawyk}</td>"
                    for data, status in row.items():
                        css_class = mapowanie_css.get(status, 'square-empty')
                        html_table += f"<td><span class='habit-square {css_class}'></span></td>"
                    dane_nawyku_osoby = dane_osoby[dane_osoby['Opis'] == nawyk].sort_values('Data')
                    streak = calculate_streak(dane_nawyku_osoby['Odpowiedz'])
                    html_table += f"<td><strong>{streak}</strong></td></tr>"
                html_table += "</tbody></table>"
                st.markdown(html_table, unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("📊 Analiza Ogólna")
        if not filtrowane_dane.empty:
            st.markdown("##### Postęp poszczególnych nawyków w czasie")
            procenty_per_nawyk = filtrowane_dane.groupby([filtrowane_dane['Data'].dt.date, 'Opis'])['Odpowiedz'].apply(lambda x: (x == 'Tak').sum() / len(x) * 100 if len(x) > 0 else 0).reset_index(name='Procent Tak')
            fig1 = px.line(procenty_per_nawyk, x='Data', y='Procent Tak', color='Opis', markers=True, title='Procent realizacji nawyków w czasie')
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=KOLOR_TEKSTU, font_family='Poppins', title_font_family='Unna', legend_title_text='Nawyk')
            fig1.update_xaxes(tickformat='%d/%m/%Y')
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### Skuteczność nawyków")
            procenty_nawykow = filtrowane_dane.groupby('Opis')['Odpowiedz'].apply(lambda x: (x == 'Tak').sum() / (x != 'Nie było takiej sytuacji').sum() * 100 if (x != 'Nie było takiej sytuacji').sum() > 0 else 0).sort_values(ascending=False).reset_index(name='Procent Tak')
            fig2 = go.Figure(data=[go.Bar(y=procenty_nawykow['Opis'], x=procenty_nawykow['Procent Tak'], orientation='h', marker_color=KOLOR_AKCENTU)])
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=KOLOR_TEKSTU, font_family='Poppins', title_font_family='Unna', xaxis_title="Skuteczność (%)", yaxis_title="", yaxis_autorange="reversed")
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### Zaangażowanie w zespole")
            procenty_osob = filtrowane_dane.groupby('Imie')['Odpowiedz'].apply(lambda x: (x == 'Tak').sum() / (x != 'Nie było takiej sytuacji').sum() * 100 if (x != 'Nie było takiej sytuacji').sum() > 0 else 0).sort_values(ascending=False).reset_index(name='Procent Tak')
            fig3 = go.Figure(data=[go.Bar(y=procenty_osob['Imie'], x=procenty_osob['Procent Tak'], orientation='h', marker_color=KOLOR_TEKSTU)])
            fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=KOLOR_TEKSTU, font_family='Poppins', title_font_family='Unna', xaxis_title="Zaangażowanie (%)", yaxis_title="", yaxis_autorange="reversed")
            st.plotly_chart(fig3, use_container_width=True)


elif strona == "Jak nam poszło?":
    st.header("Jak nam poszło na ostatnim spotkaniu?")
    if st.session_state.zespol_df.empty or st.session_state.nawyki_df.empty:
        st.warning("Najpierw dodaj członków zespołu i nawyki w sekcji 'Ustawienia'.")
    else:
        imiona = st.session_state.zespol_df['Imie'].tolist()
        wybrane_imie = st.selectbox("Wybierz, kim jesteś:", imiona)
        id_osoby = st.session_state.zespol_df[st.session_state.zespol_df['Imie'] == wybrane_imie].iloc[0]['ID_Osoby']
        
        with st.form(f"rejestracja_form_{id_osoby}"):
            wybrana_data = st.date_input("Wybierz datę:", datetime.now())
            st.markdown("---")
            st.subheader(f"Nawyki dla: {wybrane_imie}")
            
            for idx, nawyk in st.session_state.nawyki_df.iterrows():
                st.write(nawyk['Opis'])
                klucz = f"nawyk_{id_osoby}_{nawyk['ID_Nawyku']}"
                st.radio("Odpowiedź:", ["Tak", "Nie", "Nie było takiej sytuacji"], key=klucz, horizontal=True, label_visibility="collapsed")
            
            submitted = st.form_submit_button("Gotowe! Zapisuję")
            if submitted:
                nowe_wpisy = []
                for idx, nawyk in st.session_state.nawyki_df.iterrows():
                    klucz = f"nawyk_{id_osoby}_{nawyk['ID_Nawyku']}"
                    odpowiedz = st.session_state[klucz]
                    nowy_wpis = {
                        'Data': wybrana_data.strftime('%Y-%m-%d'), 
                        'ID_Osoby': id_osoby, 
                        'ID_Nawyku': nawyk['ID_Nawyku'], 
                        'Odpowiedz': odpowiedz
                    }
                    nowe_wpisy.append(nowy_wpis)
                
                nowe_wpisy_df = pd.DataFrame(nowe_wpisy)
                append_data(nowe_wpisy_df, "Wpisy")
                st.success(f"Pomyślnie zapisano wyniki dla: {wybrane_imie}!")
                st.balloons()
                st.rerun()

elif strona == "Ustawienia":
    st.header("Ustawienia i zarządzanie aplikacją")
    
    with st.expander("Rozwiń, aby zarządzać zespołem"):
        with st.form("dodaj_osobe_form", clear_on_submit=True):
            nowe_imie = st.text_input("Wpisz imię nowej osoby:")
            if st.form_submit_button("Dodaj osobę") and nowe_imie:
                if nowe_imie not in st.session_state.zespol_df['Imie'].tolist():
                    nowe_id = st.session_state.zespol_df['ID_Osoby'].max() + 1 if not st.session_state.zespol_df.empty else 1
                    nowy_czlonek = pd.DataFrame([{'ID_Osoby': int(nowe_id), 'Imie': nowe_imie}])
                    updated_df = pd.concat([st.session_state.zespol_df, nowy_czlonek], ignore_index=True)
                    save_data(updated_df, "Zespol")
                    st.success(f"Dodano: {nowe_imie}!")
                    st.rerun()
                else:
                    st.error("Osoba o tym imieniu już istnieje.")
        st.write("---")
        st.write("**Aktualny Zespół:**")
        for index, row in st.session_state.zespol_df.iterrows():
            c1, c2 = st.columns([0.8, 0.2])
            c1.write(f"**{row['Imie']}**")
            if c2.button("Usuń", key=f"del_osoba_{row['ID_Osoby']}"):
                updated_df = st.session_state.zespol_df[st.session_state.zespol_df['ID_Osoby'] != row['ID_Osoby']]
                save_data(updated_df, "Zespol")
                st.rerun()

    with st.expander("Rozwiń, aby zarządzać nawykami"):
        with st.form("dodaj_nawyk_form", clear_on_submit=True):
            nowy_opis = st.text_area("Wpisz opis nowego nawyku:", height=100)
            if st.form_submit_button("Dodaj nawyk") and nowy_opis:
                nowe_id = st.session_state.nawyki_df['ID_Nawyku'].max() + 1 if not st.session_state.nawyki_df.empty else 1
                nowy_nawyk = pd.DataFrame([{'ID_Nawyku': int(nowe_id), 'Opis': nowy_opis}])
                updated_df = pd.concat([st.session_state.nawyki_df, nowy_nawyk], ignore_index=True)
                save_data(updated_df, "Nawyki")
                st.success(f"Dodano nowy nawyk!")
                st.rerun()
        st.write("---")
        st.write("**Aktualne Nawyki:**")
        for index, row in st.session_state.nawyki_df.iterrows():
            c1, c2 = st.columns([0.8, 0.2])
            c1.write(f"{row['Opis']}")
            if c2.button("Usuń", key=f"del_nawyk_{row['ID_Nawyku']}"):
                updated_df = st.session_state.nawyki_df[st.session_state.nawyki_df['ID_Nawyku'] != row['ID_Nawyku']]
                save_data(updated_df, "Nawyki")
                st.rerun()

    with st.expander("Rozwiń, aby zarządzać wpisami"):
        if st.session_state.wpisy_df.empty:
            st.info("Brak jakichkolwiek wpisów do wyświetlenia.")
        else:
            # ... (logika usuwania wpisów pozostaje taka sama, ale teraz operuje na nowej funkcji save_data) ...
            st.warning("Uwaga: Usunięcie wpisu z danego dnia jest nieodwracalne.")
            col1, col2 = st.columns(2)
            with col1:
                osoba_do_filtrowania = st.selectbox("Pokaż wpisy dla:", ["Wszystkich"] + st.session_state.zespol_df['Imie'].tolist(), key="filtr_osob_usun")
            with col2:
                data_do_filtrowania = st.date_input("Pokaż wpisy z dnia:", value=None, key="filtr_daty_usun")
            
            dane_wpisow = pd.merge(st.session_state.wpisy_df, st.session_state.zespol_df, on='ID_Osoby')
            dane_wpisow['Data_str'] = pd.to_datetime(dane_wpisow['Data']).dt.strftime('%Y-%m-%d')
            if osoba_do_filtrowania != "Wszystkich":
                dane_wpisow = dane_wpisow[dane_wpisow['Imie'] == osoba_do_filtrowania]
            if data_do_filtrowania:
                dane_wpisow = dane_wpisow[dane_wpisow['Data_str'] == data_do_filtrowania.strftime('%Y-%m-%d')]
            
            wpisy_pogrupowane = dane_wpisow.groupby(['Data_str', 'Imie', 'ID_Osoby']).size().reset_index(name='LiczbaNawykow')
            st.write(f"Znaleziono {len(wpisy_pogrupowane)} wpisów (sesji).")

            for index, row in wpisy_pogrupowane.iterrows():
                id_osoby = row['ID_Osoby']
                data_wpisu = row['Data_str']
                imie = row['Imie']
                
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"Wpis dla **{imie}** z dnia **{data_wpisu}**")
                
                if c2.button("Usuń cały wpis", key=f"del_submission_{id_osoby}_{data_wpisu}"):
                    wpisy_po_usunieciu = st.session_state.wpisy_df[
                        ~((st.session_state.wpisy_df['ID_Osoby'] == id_osoby) & (st.session_state.wpisy_df['Data'] == data_wpisu))
                    ]
                    save_data(wpisy_po_usunieciu, "Wpisy")
                    st.success(f"Usunięto wpis dla {imie} z dnia {data_wpisu}.")
                    st.rerun()