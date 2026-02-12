import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ========== CONFIGURATION ==========
API_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="ObRail Europe - Tableau de Bord",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CSS ==========
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

        * { font-family: 'Inter', sans-serif; }

        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1b2a 0%, #112240 100%);
            border-right: 1px solid rgba(99, 179, 237, 0.2);
        }
        [data-testid="stSidebar"] * {
            color: #e2e8f0 !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            color: #e2e8f0 !important;
            font-size: 1rem !important;
        }

        /* Tous les textes en blanc */
        p, h1, h2, h3, h4, h5, h6, label, span, div {
            color: #e2e8f0 !important;
        }

        /* Header principal */
        .main-header {
            background: linear-gradient(135deg, #1a365d 0%, #2a4a8a 50%, #1a365d 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(99, 179, 237, 0.3);
            text-align: center;
            box-shadow: 0 0 40px rgba(99, 179, 237, 0.15);
            animation: glow 3s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(99, 179, 237, 0.15); }
            to { box-shadow: 0 0 40px rgba(99, 179, 237, 0.35); }
        }
        .main-header h1 {
            color: #ffffff !important;
            font-size: 3rem !important;
            font-weight: 800 !important;
            letter-spacing: 2px;
            text-shadow: 0 0 20px rgba(99, 179, 237, 0.8);
            margin: 0;
        }
        .main-header p {
            color: #90cdf4 !important;
            font-size: 1.1rem !important;
            margin-top: 10px;
        }
        .main-header .subtitle {
            color: #63b3ed !important;
            font-size: 0.9rem !important;
            margin-top: 5px;
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #1a2744 0%, #1e3a5f 100%);
            padding: 30px 20px;
            border-radius: 16px;
            border: 1px solid rgba(99, 179, 237, 0.25);
            text-align: center;
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(99, 179, 237, 0.2);
        }
        .metric-emoji {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            color: #63b3ed !important;
            line-height: 1;
        }
        .metric-label {
            font-size: 1rem !important;
            color: #90cdf4 !important;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* Section titles */
        .section-title {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            padding: 12px 20px;
            background: linear-gradient(90deg, rgba(99, 179, 237, 0.15), transparent);
            border-left: 4px solid #63b3ed;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }

        /* Quality badge */
        .quality-badge {
            background: linear-gradient(135deg, #1a4731, #276749);
            padding: 20px 25px;
            border-radius: 12px;
            border: 1px solid rgba(72, 187, 120, 0.4);
            color: #9ae6b4 !important;
            font-size: 1rem !important;
            text-align: center;
            margin-top: 15px;
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.1);
        }

        /* Dataframe */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(99, 179, 237, 0.2);
        }
        [data-testid="stDataFrame"] * {
            color: #e2e8f0 !important;
        }

        /* Input */
        .stTextInput input {
            background: #1a2744 !important;
            border: 1px solid rgba(99, 179, 237, 0.3) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
            padding: 12px !important;
        }
        .stTextInput input::placeholder {
            color: #718096 !important;
        }

        /* Selectbox */
        .stSelectbox select, [data-testid="stSelectbox"] * {
            background: #1a2744 !important;
            color: #e2e8f0 !important;
        }

        /* Slider */
        .stSlider * { color: #e2e8f0 !important; }

        /* Divider */
        hr { border-color: rgba(99, 179, 237, 0.15) !important; }

        /* Footer */
        .footer {
            text-align: center;
            padding: 25px;
            margin-top: 40px;
            border-top: 1px solid rgba(99, 179, 237, 0.2);
            background: rgba(26, 39, 68, 0.5);
            border-radius: 12px;
        }
        .footer p {
            color: #718096 !important;
            margin: 5px 0;
        }
        .footer a {
            color: #63b3ed !important;
            text-decoration: none;
        }

        /* Status badge */
        .status-ok {
            background: linear-gradient(135deg, #1a4731, #276749);
            color: #9ae6b4 !important;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem !important;
            display: inline-block;
            border: 1px solid rgba(72, 187, 120, 0.3);
        }
        .status-error {
            background: linear-gradient(135deg, #4a1a1a, #6b2727);
            color: #fc8181 !important;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem !important;
            display: inline-block;
            border: 1px solid rgba(252, 129, 129, 0.3);
        }

        /* Plotly fix */
        .js-plotly-plot .plotly .gtitle {
            fill: #e2e8f0 !important;
        }
    </style>
""", unsafe_allow_html=True)


# ========== FONCTIONS ==========
def fetch_data(endpoint):
    try:
        r = requests.get(f"{API_URL}{endpoint}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

def make_fig(fig):
    """Applique un style cohérent à tous les graphiques"""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(13,27,42,0.5)',
        font=dict(color='#e2e8f0', family='Inter'),
        title_font=dict(color='#ffffff', size=16),
        legend=dict(
            font=dict(color='#e2e8f0'),
            bgcolor='rgba(26,39,68,0.8)',
            bordercolor='rgba(99,179,237,0.2)',
            borderwidth=1
        ),
        margin=dict(t=50, b=50, l=20, r=20)
    )
    return fig


# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 10px 0 20px 0;'>
            <div style='font-size: 3rem;'>🚂</div>
            <div style='font-size: 1.3rem; font-weight: 700; color: #ffffff !important;'>ObRail Europe</div>
            <div style='font-size: 0.8rem; color: #718096 !important; letter-spacing: 2px;'>OBSERVATOIRE FERROVIAIRE</div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "Navigation",
        ["📊 Vue Globale", "🔍 Recherche", "📋 Données brutes"],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("**🔌 Status API**")
    health = fetch_data("/../../health")
    if health and health.get("status") == "healthy":
        st.markdown('<span class="status-ok">✅ API Connectée</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-error">❌ API Déconnectée</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📖 Documentation**")
    st.markdown('<a href="http://localhost:8000/docs" style="color: #63b3ed;">→ Swagger UI</a>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<p style="color: #4a5568 !important; font-size: 0.75rem; text-align: center;">© 2025 ObRail Europe<br>Mobilité durable européenne</p>', unsafe_allow_html=True)


# ========== HEADER ==========
st.markdown("""
    <div class="main-header">
        <div style="font-size: 1rem; color: #63b3ed !important; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 10px;">
            🇪🇺 Observatoire Ferroviaire Européen
        </div>
        <h1>🚂 ObRail Europe</h1>
        <p>Tableau de bord — Données ferroviaires européennes</p>
        <div class="subtitle">Trains de jour & de nuit | Mobilité durable | Green Deal Européen</div>
    </div>
""", unsafe_allow_html=True)


# ========== PAGE : VUE GLOBALE ==========
if page == "📊 Vue Globale":

    # MÉTRIQUES
    stats = fetch_data("/comparisons/stats")
    if stats:
        c1, c2, c3 = st.columns(3)
        metrics = [
            (c1, "🏛️", stats['total_gares'], "Gares"),
            (c2, "🛤️", stats['total_lignes'], "Lignes"),
            (c3, "🚆", stats['total_trajets'], "Trajets"),
        ]
        for col, emoji, val, label in metrics:
            with col:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-emoji">{emoji}</div>
                        <div class="metric-value">{val:,}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                """, unsafe_allow_html=True)

    st.divider()

    # GRAPHIQUES LIGNE 1
    c_left, c_right = st.columns(2)

    # Jour/Nuit
    with c_left:
        st.markdown('<div class="section-title">🌙 Répartition Trains Jour / Nuit</div>', unsafe_allow_html=True)
        data = fetch_data("/comparisons/repartition-jour-nuit")
        if data:
            df = pd.DataFrame(data)
            fig = px.pie(
                df, values="nombre", names="periode",
                color="periode",
                color_discrete_map={"Jour": "#F6AD55", "Nuit": "#4299E1"},
                hole=0.5
            )
            fig.update_traces(
                textinfo='percent+label',
                textfont=dict(size=14, color='white'),
                marker=dict(line=dict(color='#0d1b2a', width=3))
            )
            fig = make_fig(fig)
            fig.update_layout(
                annotations=[dict(
                    text='🚆', x=0.5, y=0.5,
                    font_size=30, showarrow=False
                )]
            )
            st.plotly_chart(fig, use_container_width=True)

    # Lignes par type
    with c_right:
        st.markdown('<div class="section-title">📊 Lignes par type de transport</div>', unsafe_allow_html=True)
        data = fetch_data("/comparisons/lignes-par-type")
        if data:
            df = pd.DataFrame(data)
            type_labels = {
                0: "🚋 Tram", 1: "🚇 Métro", 2: "🚆 Train",
                3: "🚌 Bus", 4: "⛴️ Ferry", 5: "🚡 Téléphérique",
                6: "🚠 Gondole", 7: "🚞 Funiculaire"
            }
            df["type_label"] = df["type_transport"].map(lambda x: type_labels.get(x, f"Type {x}"))
            fig = px.pie(
                df, values="nombre_lignes", names="type_label",
                hole=0.5,
                color_discrete_sequence=['#63b3ed', '#4299e1', '#3182ce', '#2b6cb0', '#2c5282', '#ebf8ff', '#bee3f8', '#90cdf4']
            )
            fig.update_traces(
                textinfo='percent+label',
                textfont=dict(size=12, color='white'),
                marker=dict(line=dict(color='#0d1b2a', width=3))
            )
            fig = make_fig(fig)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # TOP OPÉRATEURS
    st.markdown('<div class="section-title">🏢 Volume de données par opérateur</div>', unsafe_allow_html=True)
    data = fetch_data("/comparisons/top-operateurs?limit=10")
    if data:
        df = pd.DataFrame(data)
        fig = px.bar(
            df, x="nombre_lignes", y="operateur",
            orientation="h",
            color="nombre_lignes",
            color_continuous_scale=[[0, '#1a365d'], [0.5, '#2b6cb0'], [1, '#63b3ed']],
            text="nombre_lignes"
        )
        fig.update_traces(
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=12),
            marker_line_color='rgba(0,0,0,0)'
        )
        fig = make_fig(fig)
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending', gridcolor='rgba(99,179,237,0.1)', color='#e2e8f0'),
            xaxis=dict(gridcolor='rgba(99,179,237,0.1)', color='#e2e8f0'),
            coloraxis_showscale=False,
            height=420
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # GARES LES PLUS DESSERVIES
    st.markdown('<div class="section-title">🏛️ Top 10 Gares les plus desservies</div>', unsafe_allow_html=True)
    data = fetch_data("/comparisons/gares-les-plus-desservies?limit=10")
    if data:
        df = pd.DataFrame(data)
        fig = px.bar(
            df, x="gare", y="nombre_passages",
            color="nombre_passages",
            color_continuous_scale=[[0, '#1a4731'], [0.5, '#276749'], [1, '#48bb78']],
            text="nombre_passages"
        )
        fig.update_traces(
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=11),
            marker_line_color='rgba(0,0,0,0)'
        )
        fig = make_fig(fig)
        fig.update_layout(
            xaxis=dict(tickangle=-35, gridcolor='rgba(99,179,237,0.1)', color='#e2e8f0'),
            yaxis=dict(gridcolor='rgba(99,179,237,0.1)', color='#e2e8f0'),
            coloraxis_showscale=False,
            height=420
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # QUALITÉ DES DONNÉES
    st.markdown('<div class="section-title">⚠️ Qualité des données — Valeurs manquantes</div>', unsafe_allow_html=True)
    data = fetch_data("/comparisons/valeurs-manquantes")
    if data:
        df = pd.DataFrame(data)
        fig = px.bar(
            df, x="champ", y="taux_manquant",
            color="taux_manquant",
            color_continuous_scale=[[0, '#276749'], [0.5, '#c05621'], [1, '#c53030']],
            text="taux_manquant"
        )
        fig.update_traces(
            texttemplate='%{text}%',
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=12),
            marker_line_color='rgba(0,0,0,0)'
        )
        fig = make_fig(fig)
        fig.update_layout(
            xaxis=dict(tickangle=-35, gridcolor='rgba(99,179,237,0.1)', color='#e2e8f0'),
            yaxis=dict(range=[0, 100], title="Taux (%)", gridcolor='rgba(99,179,237,0.1)', color='#e2e8f0'),
            coloraxis_showscale=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        if all(v["taux_manquant"] == 0 for v in data):
            st.markdown("""
                <div class="quality-badge">
                    ✅ &nbsp; Aucune valeur manquante détectée — Les données sont complètes et de haute qualité
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Des valeurs manquantes ont été détectées.")


# ========== PAGE : RECHERCHE ==========
elif page == "🔍 Recherche":
    st.markdown('<div class="section-title">🔍 Rechercher une gare</div>', unsafe_allow_html=True)

    search_nom = st.text_input("", placeholder="✍️ Ex: Paris, Lyon, Marseille...", label_visibility="collapsed")
    if search_nom:
        gares = fetch_data(f"/gares/search/nom?nom={search_nom}")
        if gares:
            st.success(f"✅ {len(gares)} gare(s) trouvée(s)")
            st.dataframe(pd.DataFrame(gares), use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Aucune gare trouvée")

    st.divider()

    st.markdown('<div class="section-title">🔍 Rechercher une ligne</div>', unsafe_allow_html=True)
    search_code = st.text_input("", placeholder="✍️ Ex: C30, TGV, TER...", label_visibility="collapsed", key="ligne")
    if search_code:
        lignes = fetch_data(f"/lignes/search/code?code={search_code}")
        if lignes:
            st.success(f"✅ {len(lignes)} ligne(s) trouvée(s)")
            st.dataframe(pd.DataFrame(lignes), use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Aucune ligne trouvée")

    st.divider()

    st.markdown('<div class="section-title">🔍 Rechercher un opérateur</div>', unsafe_allow_html=True)
    search_op = st.text_input("", placeholder="✍️ Ex: SNCF, ÖBB, Trenitalia...", label_visibility="collapsed", key="operateur")
    if search_op:
        operateurs = fetch_data(f"/operateurs/search/nom?nom={search_op}")
        if operateurs:
            st.success(f"✅ {len(operateurs)} opérateur(s) trouvé(s)")
            st.dataframe(pd.DataFrame(operateurs), use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Aucun opérateur trouvé")


# ========== PAGE : DONNÉES BRUTES ==========
elif page == "📋 Données brutes":
    st.markdown('<div class="section-title">📋 Explorer les données brutes</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        table = st.selectbox("Table", ["Gares", "Lignes", "Opérateurs", "Trajets", "Horaires"])
    with c2:
        limit = st.slider("Lignes", 10, 500, 50, 10)

    endpoint_map = {
        "Gares": f"/gares?limit={limit}",
        "Lignes": f"/lignes?limit={limit}",
        "Opérateurs": f"/operateurs?limit={limit}",
        "Trajets": f"/trajets?limit={limit}",
        "Horaires": f"/horaires?limit={limit}"
    }

    data = fetch_data(endpoint_map[table])
    if data:
        df = pd.DataFrame(data)
        st.success(f"✅ {len(df)} lignes — Table : {table}")
        st.dataframe(df, use_container_width=True, hide_index=True)


# ========== FOOTER ==========
st.markdown("""
    <div class="footer">
        <p>🚂 <strong>ObRail Europe</strong> © 2025 — Observatoire indépendant spécialisé dans le ferroviaire et la mobilité durable</p>
        <p>API REST disponible sur <a href='http://localhost:8000/docs'>http://localhost:8000/docs</a> | Green Deal Européen | TEN-T</p>
    </div>
""", unsafe_allow_html=True)