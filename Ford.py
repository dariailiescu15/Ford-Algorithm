import streamlit as st                                          # importam libraria principala pt a face interfata web
import numpy as np                                              # desi aici folosim mai mult liste, e buna la casa omului
import pandas as pd                                             # libraria asta ne ajuta sa afisam tabelul de arce frumos

                                                                # CONFIGURARE PAGINA SI DESIGN CSS
st.set_page_config(page_title="Algoritmul Ford", layout="wide", page_icon="🗺️") # setam pagina pe tot ecranul si punem emoji in tab

st.markdown("""
    <style>
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 55px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .authors-box { color: #cc5200; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #e65c00; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #cc5200; line-height: 1.6; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)                                    # trebuie activat html-ul ca sa mearga css-ul de mai sus

def fmt(val):                                                   # functie salvatoare pt a scapa de zecimale inutile gen 25.0000 
    if pd.isna(val) or val is None: return ""                   # daca e gol, returnam string gol
    if val == float('inf'): return "\infty"                     # daca e infinit, dam textul de latex pt infinit matematic
    if isinstance(val, (np.floating, float, int)):
        return str(int(val)) if float(val).is_integer() else f"{val:.2f}" # lasa intreg daca e intreg, altfel 2 zecimale
    return str(val)

                                                                # =======================================================
                                                                # LOGICA MATEMATICA: ALGORITMUL FORD
                                                                # =======================================================

def executa_algoritmul_ford(arce_df, nod_start):                # functia care face toata munca iterativa
    # extragem lista unica de varfuri din coloanele tabelului
    noduri = set(arce_df['Nod Start (x_i)']).union(set(arce_df['Nod Destinație (x_j)']))
    noduri = sorted(list(noduri))
    
    # Iterația I_0: Initializam cu infinit peste tot, mai putin la start unde punem zero
    lambdas = {n: float('inf') for n in noduri}
    lambdas[nod_start] = 0
    
    istoric =[]                                                # aici salvez iterațiile ca sa le pot afisa ulterior pe ecran
    istoric.append({
        'iteratie': 0,
        'lambdas': lambdas.copy(),
        'modificari': {}
    })
    
    iteratie = 1
    max_iter = len(noduri) + 5                                  # protectie: nu rulam la infinit daca da rateu si face vreo bucla
    
    while iteratie < max_iter:
        modificat = False
        modificari_iteratie = {}
        lambdas_curente = lambdas.copy()
        
        # Parcurgem lista de arce rand cu rand, fix ca la curs (evaluam de fiecare data)
        for _, rand in arce_df.iterrows():
            i = rand['Nod Start (x_i)']
            j = rand['Nod Destinație (x_j)']
            f_ij = rand['Cost f(x_i, x_j)']
            
            # Condiția de aur a lui Ford: daca pe noul drum iesim mai ieftin, actualizam valoarea
            if lambdas_curente[i] != float('inf') and lambdas_curente[j] - lambdas_curente[i] > f_ij:
                lambdas_curente[j] = lambdas_curente[i] + f_ij
                modificat = True
                modificari_iteratie[j] = lambdas_curente[j]     # tinem minte cine s-a modificat la tura asta ca sa scriem dupa
        
        lambdas = lambdas_curente.copy()
        istoric.append({
            'iteratie': iteratie,
            'lambdas': lambdas.copy(),
            'modificari': modificari_iteratie
        })
        
        if not modificat:                                       # STOP JOC, s-a stabilizat rețeaua! Nu se mai modifica nimic
            break
        iteratie += 1
        
    return noduri, istoric

def reconstituie_drum_ford(istoric_lambdas, arce_df, nod_start, nod_destinatie): # refacem drumul mergand invers (de la final)
    lambdas = istoric_lambdas[-1]['lambdas']                    # luam etichetele finale din ultima iteratie
    
    if lambdas[nod_destinatie] == float('inf'):                 # daca a ramas infinit, clar n-avem pe unde sa ajungem
        return None, "Nu există drum de la sursă la destinație!"
        
    drum = [nod_destinatie]
    curent = nod_destinatie
    
    while curent != nod_start:
        gasit = False
        for _, rand in arce_df.iterrows():
            i = rand['Nod Start (x_i)']
            j = rand['Nod Destinație (x_j)']
            f_ij = rand['Cost f(x_i, x_j)']
            
            # Cautam arcele care indeplinesc fix relatia optima: lambda_j - lambda_i = f(xi, xj)
            if j == curent and abs(lambdas[j] - lambdas[i] - f_ij) < 1e-9:
                drum.append(i)
                curent = i
                gasit = True
                break
        
        if not gasit:                                           # masura de siguranta, daca da fail ceva ne oprim
            break
            
    return drum[::-1], lambdas[nod_destinatie]                  # returnam drumul pe fata (inversam lista) si costul lui

                                                                # =======================================================
                                                                # INTERFATA UI STREAMLIT (Aici construim vizualul app-ului)
                                                                # =======================================================

st.markdown('''
    <div class="title-box">
        <p class="title-text">🗺️ Teoria Grafurilor 🚗<br>📍 Algoritmul FORD 🚦</p>
    </div>
''', unsafe_allow_html=True)

st.markdown('''
    <div class="authors-box">
        <div class="authors-title">Facultatea de Științe Aplicate</div>
        <div class="authors-names">
            Dedu Anișoara-Nicoleta, 1333a<br>
            Dumitrescu Andreea Mihaela, 1333a<br>
            Iliescu Daria-Gabriela, 1333a<br>
            Lungu Ionela-Diana, 1333a
        </div>
    </div>
''', unsafe_allow_html=True)

st.markdown("<h3 style='color: #e65c00;'>📝 1. Datele Grafului (Lista de arce)</h3>", unsafe_allow_html=True)
st.write("Introduceți arcele grafului $G=(X,U)$ și funcția de valoare $f(x_i, x_j)$ pentru fiecare arc. Puteți adăuga rânduri noi trăgând de chenarul tabelului în jos.")

# AICI E SECRETUL: Salvam tabelul de date in memoria sesiunii ca sa nu il pierdem la fiecare click
# Am pus direct datele din exemplul de la curs, sa mearga teava
if "tabel_arce" not in st.session_state:
    date_initiale = [[1, 2, 10], [1, 9, 10],[2, 3, 15], [3, 4, 12],[4, 1, 7],[4, 6, 8], [4, 9, 9],[5, 1, 6],
        [5, 6, 20], [6, 7, 17],[6, 8, 13], [7, 1, 4],[7, 2, 6],[8, 9, 11],[9, 5, 5],[9, 6, 4]
    ]
    df_initial = pd.DataFrame(date_initiale, columns=["Nod Start (x_i)", "Nod Destinație (x_j)", "Cost f(x_i, x_j)"])
    st.session_state.tabel_arce = df_initial

# Parametrul "key" blocheaza resetarea tabelului gen cand editam vreo valoare din el
edited_df = st.data_editor(
    st.session_state.tabel_arce, 
    num_rows="dynamic",
    use_container_width=True,
    key="editor_arce"
)

# Aflam ce noduri avem prin tabel si facem meniurile dropdown din stanga si dreapta
noduri_disponibile = sorted(list(set(edited_df['Nod Start (x_i)']).union(set(edited_df['Nod Destinație (x_j)']))))
if len(noduri_disponibile) > 0:
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        nod_start = st.selectbox("📍 Vârful de start ($x_s$)", noduri_disponibile, index=0)
    with col2:
        nod_dest = st.selectbox("🏁 Vârful terminal ($x_t$)", noduri_disponibile, index=len(noduri_disponibile)-1 if len(noduri_disponibile)>5 else 0)

# Cand apasam butonul... BANG, incepe matematica
if st.button("🚀 Calculează Drumul Minim", type="primary", use_container_width=True):
    st.divider()
    
    # --------------------------------------------------------- PASUL 1: ITERATIILE FORD -----------------------
    st.markdown("<h3 style='color: #e65c00;'>⚙️ 2. Algoritmul FORD (Etape de rezolvare)</h3>", unsafe_allow_html=True)
    
    noduri, istoric = executa_algoritmul_ford(edited_df, nod_start)
    
    # Prezentam Iterația I_0 super academic
    st.markdown(r"#### 🟢 Iterația $I_0$")
    st.write(f"Se atribuie fiecărui vârf $x_i \in X$ o valoare $\lambda_i$ astfel încât $\lambda_{{{nod_start}}} = 0$ și restul sunt $\infty$.")
    
    # Folosesc direct text latex ca sa fac sirul ala lung de lambda-uri
    l0_text = ", ".join([rf"\lambda_{{{n}}} = {fmt(istoric[0]['lambdas'][n])}" for n in noduri])
    st.latex(l0_text)
    
    # Iteram prin restul de pasi din istoric
    for pas in istoric[1:]:
        st.markdown(r"---")
        st.markdown(rf"#### 🟡 Iterația $I_{{{pas['iteratie']}}}$")
        
        if len(pas['modificari']) == 0:
            st.success(rf"**Testul de optimalitate (TO):** Nu s-a făcut nicio modificare la parcurgerea listei de arce. $\Rightarrow$ **STOP**.")
            st.latex(r"I_{STOP} \Rightarrow \text{Reprezintă soluția problemei!}")
        else:
            st.write("Se parcurge lista arcelor și se evaluează condiția de ajustare: $\lambda_j - \lambda_i > f(x_i, x_j)$. Au avut loc următoarele modificări:")
            
            # Afisam doar ce s-a updatat in pasul curent
            modificari_latex =[]
            for nod_modificat, valoare_noua in pas['modificari'].items():
                modificari_latex.append(rf"\lambda'_{{{nod_modificat}}} = {fmt(valoare_noua)}")
            st.latex(r" \quad ; \quad ".join(modificari_latex))
            
            # La final afisam din nou tot vectorul lambda complet
            st_text = ", ".join([rf"\lambda_{{{n}}} = {fmt(pas['lambdas'][n])}" for n in noduri])
            st.latex(r"\text{Status curent: } " + st_text)

    # --------------------------------------------------------- PASUL 2: RECONSTITUIREA DRUMULUI ----------------
    st.divider()
    st.markdown("<h3 style='color: #e65c00;'>🛤️ 3. Soluția Problemei (Reconstituirea drumului)</h3>", unsafe_allow_html=True)
    
    drum, cost_total = reconstituie_drum_ford(istoric, edited_df, nod_start, nod_dest)
    
    if drum is None:
        st.error(cost_total)                                    # Daca n-avem drum, plangem si afisam eroare
    else:
        st.write(rf"Se reconstituie drumul optim pornind invers, de la destinație ($x_{{{nod_dest}}}$) spre sursă ($x_{{{nod_start}}}$), verificând pe arce condiția matematică de echilibru:")
        st.latex(r"\lambda_j - \lambda_i = f(x_i, x_j)")
        
        # Facem demonstratia fix cum a facut profa la curs, aratam calculele pt fiecare segment
        for k in range(len(drum)-1, 0, -1):
            i = drum[k-1]
            j = drum[k]
            # Luam costul arcului dintre ele direct din input-ul dat de noi
            f_ij = edited_df[(edited_df['Nod Start (x_i)'] == i) & (edited_df['Nod Destinație (x_j)'] == j)]['Cost f(x_i, x_j)'].values[0]
            st.latex(rf"\lambda_{{{j}}} - \lambda_{{{i}}} = {fmt(istoric[-1]['lambdas'][j])} - {fmt(istoric[-1]['lambdas'][i])} = {fmt(f_ij)} = f(x_{{{i}}}, x_{{{j}}})")
        
        # Concluzia vizuala, toata facuta in st.latex ca sa randeze perfect math font-ul
        st.success("🎉 Am ajuns la destinație! Drumul optim a fost determinat cu succes.")
        
        traseu_str = " \\rightarrow ".join([f"x_{{{n}}}" for n in drum])
        
        # AICI E CHEIA: am scris textul din titlu fix din latex sa arate super oficial
        st.latex(r"\textbf{Drumul de valoare minimă } \mu^* \textbf{ este:}")
        st.latex(rf"\mu^* = [ {traseu_str} ]")
        st.latex(rf"f(\mu^*) = \lambda_{{{nod_dest}}} = {fmt(cost_total)} \text{{ (costul optim)}}")
