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
    if val == float('inf'): return "∞"                          # daca e infinit, punem simbolul de infinit matematic
    if isinstance(val, (np.floating, float, int)):
        return str(int(val)) if float(val).is_integer() else f"{val:.2f}" # lasa intreg daca e intreg, altfel 2 zecimale
    return str(val)

                                                                # =======================================================
                                                                # LOGICA MATEMATICA: ALGORITMUL FORD
                                                                # =======================================================

def executa_algoritmul_ford(arce_df, nod_start):                # functia care face toata munca iterativa
    # extragem lista unica de noduri (varfuri) din coloanele tabelului
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
    max_iter = len(noduri) + 5                                  # protectie: nu rulam la infinit daca se blocheaza cumva
    
    while iteratie < max_iter:
        modificat = False
        modificari_iteratie = {}
        lambdas_curente = lambdas.copy()
        
        # Parcurgem lista de arce rand cu rand, fix ca la seminar/curs
        for _, rand in arce_df.iterrows():
            i = rand['Nod Start (x_i)']
            j = rand['Nod Destinație (x_j)']
            f_ij = rand['Cost f(x_i, x_j)']
            
            # Condiția de aur a lui Ford: daca se poate mai ieftin, actualizam valoarea
            if lambdas_curente[i] != float('inf') and lambdas_curente[j] - lambdas_curente[i] > f_ij:
                lambdas_curente[j] = lambdas_curente[i] + f_ij
                modificat = True
                modificari_iteratie[j] = lambdas_curente[j]     # tinem minte cine s-a modificat ca sa scriem dupa
        
        lambdas = lambdas_curente.copy()
        istoric.append({
            'iteratie': iteratie,
            'lambdas': lambdas.copy(),
            'modificari': modificari_iteratie
        })
        
        if not modificat:                                       # STOP JOC, s-a stabilizat rețeaua!
            break
        iteratie += 1
        
    return noduri, istoric

def reconstituie_drum_ford(istoric_lambdas, arce_df, nod_start, nod_destinatie): # refacem drumul mergand invers (de la capat)
    lambdas = istoric_lambdas[-1]['lambdas']                    # luam etichetele finale
    
    if lambdas[nod_destinatie] == float('inf'):                 # daca a ramas infinit, inseamna ca nu exista drum
        return None, "Nu există drum de la sursă la destinație!"
        
    drum = [nod_destinatie]
    curent = nod_destinatie
    
    while curent != nod_start:
        gasit = False
        for _, rand in arce_df.iterrows():
            i = rand['Nod Start (x_i)']
            j = rand['Nod Destinație (x_j)']
            f_ij = rand['Cost f(x_i, x_j)']
            
            # Verificam relatia inversa: lambda_j - lambda_i = f(xi, xj)
            if j == curent and abs(lambdas[j] - lambdas[i] - f_ij) < 1e-9:
                drum.append(i)
                curent = i
                gasit = True
                break
        
        if not gasit:                                           # masura de siguranta
            break
            
    return drum[::-1], lambdas[nod_destinatie]                  # returnam drumul intors pe fata si costul lui

                                                                # =======================================================
                                                                # INTERFATA UI STREAMLIT (Aici cream efectiv app-ul)
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

# AICI E SECRETUL: Salvam tabelul de date initiale in memoria aplicatiei
# Am pus tabelul mare din exemplul 6 de la curs, ca sa il avem gata facut 
if "tabel_arce" not in st.session_state:
    date_initiale = [[1, 2, 10], [1, 9, 10],[2, 3, 15], [3, 4, 12],
        [4, 1, 7],[4, 6, 8], [4, 9, 9],[5, 1, 6],
        [5, 6, 20], [6, 7, 17],[6, 8, 13], [7, 1, 4],
        [7, 2, 6],[8, 9, 11],[9, 5, 5],[9, 6, 4]
    ]
    df_initial = pd.DataFrame(date_initiale, columns=["Nod Start (x_i)", "Nod Destinație (x_j)", "Cost f(x_i, x_j)"])
    st.session_state.tabel_arce = df_initial

# Parametrul "key" blocheaza resetarea tabelului cand editam celule
edited_df = st.data_editor(
    st.session_state.tabel_arce, 
    num_rows="dynamic",
    use_container_width=True,
    key="editor_arce"
)

# Cream meniurile dropdown pentru a alege nodul de start si cel de final
noduri_disponibile = sorted(list(set(edited_df['Nod Start (x_i)']).union(set(edited_df['Nod Destinație (x_j)']))))
if len(noduri_disponibile) > 0:
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        nod_start = st.selectbox("📍 Vârful de start ($x_s$)", noduri_disponibile, index=0)
    with col2:
        nod_dest = st.selectbox("🏁 Vârful terminal ($x_t$)", noduri_disponibile, index=len(noduri_disponibile)-1 if len(noduri_disponibile)>5 else 0)

# Cand apasam butonul incepe MAGIA
if st.button("🚀 Calculează Drumul Minim", type="primary", use_container_width=True):
    st.divider()
    
    # --------------------------------------------------------- PASUL 1: ITERATIILE -----------------------
    st.markdown("<h3 style='color: #e65c00;'>⚙️ 2. Algoritmul FORD (Etape de rezolvare)</h3>", unsafe_allow_html=True)
    
    noduri, istoric = executa_algoritmul_ford(edited_df, nod_start)
    
    # Afisam Iterația I_0
    st.markdown(r"#### 🟢 Iterația $I_0$")
    st.write(f"Se atribuie fiecărui vârf $x_i \in X$ o valoare $\lambda_i$ astfel încât $\lambda_{{{nod_start}}} = 0$ și restul $\infty$.")
    
    l0_text = ", ".join([rf"\lambda_{{{n}}} = {fmt(istoric[0]['lambdas'][n])}" for n in noduri])
    st.latex(l0_text)                                           # generez ecuatiile LaTeX brici
    
    # Iteram prin restul de pasi
    for pas in istoric[1:]:
        st.markdown(r"---")
        st.markdown(rf"#### 🟡 Iterația $I_{{{pas['iteratie']}}}$")
        
        if len(pas['modificari']) == 0:
            st.success(rf"**Testul de optimalitate (TO):** Nu s-a făcut nicio modificare la parcurgerea listei de arce. $\Rightarrow$ **STOP**.")
            st.latex(r"I_{STOP} \Rightarrow \text{Reprezintă soluția problemei!}")
        else:
            st.write("Se parcurge lista arcelor și se evaluează condiția $\lambda_j - \lambda_i > f(x_i, x_j)$. Au avut loc următoarele actualizări:")
            
            # Afisam doar ce s-a schimbat in pasul asta
            modificari_latex =[]
            for nod_modificat, valoare_noua in pas['modificari'].items():
                modificari_latex.append(rf"\lambda'_{{{nod_modificat}}} = {fmt(valoare_noua)}")
            st.latex(r" \quad ; \quad ".join(modificari_latex))
            
            # Afisam toata lista la final de pas
            st_text = ", ".join([rf"\lambda_{{{n}}} = {fmt(pas['lambdas'][n])}" for n in noduri])
            st.latex(r"\text{Status curent: } " + st_text)

    # --------------------------------------------------------- PASUL 2: INTERPRETARE FINALA ----------------
    st.divider()
    st.markdown("<h3 style='color: #e65c00;'>🛤️ 3. Soluția Problemei (Reconstituirea drumului)</h3>", unsafe_allow_html=True)
    
    drum, cost_total = reconstituie_drum_ford(istoric, edited_df, nod_start, nod_dest)
    
    if drum is None:
        st.error(cost_total)                                    # Daca n-avem drum, afisam mesajul de eroare si aia e
    else:
        st.write(rf"Se reconstituie drumul optim pornind de la destinație ($x_{{{nod_dest}}}$) spre sursă ($x_{{{nod_start}}}$) verificând pe arcele inversate condiția:")
        st.latex(r"\lambda_j - \lambda_i = f(x_i, x_j)")
        
        # Vizualizare matematică a traseului (fix cum ne-a invatat la curs sa demonstram la test)
        demonstratie =[]
        for k in range(len(drum)-1, 0, -1):
            i = drum[k-1]
            j = drum[k]
            # Luam costul arcului curent din tabel
            f_ij = edited_df[(edited_df['Nod Start (x_i)'] == i) & (edited_df['Nod Destinație (x_j)'] == j)]['Cost f(x_i, x_j)'].values[0]
            demonstratie.append(rf"\lambda_{{{j}}} - \lambda_{{{i}}} = {fmt(istoric[-1]['lambdas'][j])} - {fmt(istoric[-1]['lambdas'][i])} = {fmt(f_ij)} = f(x_{{{i}}}, x_{{{j}}})")
        
        for dem in demonstratie:
            st.latex(dem)
        
        # Concluzia grafica - un chenar frumos verde la final pt nota maxima
        st.markdown(f"<div style='background-color: #d4edda; border-left: 5px solid #28a745; padding: 15px; border-radius: 5px; margin-top: 20px;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color: #155724; margin:0;'>Drumul de valoare minimă $\mu^*$ este:</h4>", unsafe_allow_html=True)
        
        traseu_str = " \\rightarrow ".join([f"x_{{{n}}}" for n in drum])
        st.latex(rf"\mu^* = [ {traseu_str} ]")
        st.latex(rf"V(\mu^*) = \lambda_{{{nod_dest}}} = {fmt(cost_total)} \text{{ (timp total / cost optim)}}")
        st.markdown("</div>", unsafe_allow_html=True)
