import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Sapi Club 🐸", page_icon="🐸", layout="centered")

DATA_FILE = "data.json"

# ── Estilos kawaii ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #e8f8f0 0%, #e0f4fb 50%, #fce8f3 100%);
    min-height: 100vh;
}

.main .block-container {
    padding-top: 1.5rem;
    max-width: 700px;
}

h1 { color: #2d7a4f !important; }
h2, h3 { color: #2d7a4f !important; }

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3dba75, #2d9e62) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 12px rgba(45,154,98,0.3) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2d9e62, #236e47) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(45,154,98,0.4) !important;
}

.stButton > button[kind="secondary"], .stButton > button {
    background: white !important;
    color: #2d7a4f !important;
    border: 2px solid #a8e6c4 !important;
    border-radius: 20px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    border-color: #3dba75 !important;
    background: #f0faf5 !important;
}

.stSelectbox > div > div {
    border-radius: 14px !important;
    border-color: #a8e6c4 !important;
    background: white !important;
    font-family: 'Nunito', sans-serif !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    border-radius: 14px !important;
    border-color: #a8e6c4 !important;
    background: white !important;
    font-family: 'Nunito', sans-serif !important;
}

.streamlit-expanderHeader {
    background: white !important;
    border-radius: 16px !important;
    border: 2px solid #d4f0e4 !important;
    color: #2d7a4f !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
}

.streamlit-expanderContent {
    background: #f7fefb !important;
    border: 2px solid #d4f0e4 !important;
    border-top: none !important;
    border-radius: 0 0 16px 16px !important;
}

hr { border-color: #c5ebd8 !important; }

.stAlert {
    border-radius: 16px !important;
    font-family: 'Nunito', sans-serif !important;
}

.stCaption { color: #6abf8a !important; font-family: 'Nunito', sans-serif !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #e8f8f0; }
::-webkit-scrollbar-thumb { background: #a8e6c4; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "jugadoras": [
            {"nombre": "Sapi 1", "puntos": 0},
            {"nombre": "Sapi 2", "puntos": 0},
            {"nombre": "Sapi 3", "puntos": 0},
        ],
        "reglas": [
            {"nombre": "Leyó el capítulo completo", "puntos": 3},
            {"nombre": "Llegó a tiempo", "puntos": 2},
            {"nombre": "Aportó al debate", "puntos": 2},
            {"nombre": "No leyó", "puntos": -3},
            {"nombre": "Llegó tarde", "puntos": -1},
            {"nombre": "Spoileó sin avisar", "puntos": -2},
        ],
        "historial": []
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ── Header ─────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:1rem 0 0.5rem'>
    <div style='font-size:52px;line-height:1.1'>🐸</div>
    <h1 style='font-size:2.2rem;font-weight:800;color:#2d7a4f;margin:4px 0 0'>Sapi Club</h1>
    <p style='color:#6abf8a;font-size:14px;margin:2px 0 0;font-weight:600'>✨ Marcador de lectura kawaii ✨</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Marcador ──────────────────────────────────────────────
st.markdown("### 🏆 Marcador")

sorted_j = sorted(enumerate(data["jugadoras"]), key=lambda x: x[1]["puntos"], reverse=True)
cols = st.columns(len(data["jugadoras"]))

card_colors  = ["#d4f0e4", "#d4edf7", "#fce8f3"]
text_colors  = ["#2d7a4f", "#1a6a8a", "#a0417a"]
border_colors = ["#3dba75", "#5bc0e8", "#e87fbf"]
card_icons   = ["🐸", "🐟", "🌸"]

for col_idx, (j_idx, j) in enumerate(sorted_j):
    with cols[col_idx]:
        pts = j["puntos"]
        pts_color = "#2d7a4f" if pts > 0 else ("#c0392b" if pts < 0 else "#888")
        lider = col_idx == 0 and pts > 0
        bg  = card_colors[col_idx % len(card_colors)]
        tc  = text_colors[col_idx % len(text_colors)]
        bc  = border_colors[col_idx % len(border_colors)] if lider else "#ddd"
        bw  = "2.5px" if lider else "1.5px"
        icon = card_icons[col_idx % len(card_icons)]
        crown = "⭐ " if lider else ""
        st.markdown(f"""
        <div style='text-align:center;padding:14px 8px 10px;background:{bg};
                    border:{bw} solid {bc};border-radius:20px;margin-bottom:4px;
                    box-shadow:0 4px 12px rgba(0,0,0,0.06)'>
            <div style='font-size:28px'>{icon}</div>
            <div style='font-weight:800;color:{tc};font-size:14px;margin:4px 0 2px'>
                {crown}{j["nombre"]}
            </div>
            <div style='font-size:30px;font-weight:800;color:{pts_color};line-height:1.1'>
                {("+" if pts > 0 else "")}{pts}
            </div>
            <div style='font-size:11px;color:#999;font-weight:600'>puntos</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Aplicar regla ─────────────────────────────────────────
st.markdown("### ⚡ Aplicar regla")

c1, c2 = st.columns(2)
with c1:
    nombres = [j["nombre"] for j in data["jugadoras"]]
    jugadora_sel = st.selectbox("🐸 Jugadora", nombres, key="sel_j")
with c2:
    regla_nombres = [f'{r["nombre"]} ({("+" if r["puntos"]>0 else "")}{r["puntos"]})' for r in data["reglas"]]
    regla_sel = st.selectbox("📖 Regla", regla_nombres, key="sel_r")

if st.button("✅ Aplicar puntos", use_container_width=True, type="primary"):
    j_idx = nombres.index(jugadora_sel)
    r_idx = regla_nombres.index(regla_sel)
    pts = data["reglas"][r_idx]["puntos"]
    data["jugadoras"][j_idx]["puntos"] += pts
    hora = datetime.now().strftime("%H:%M")
    accion = f'{hora} — {jugadora_sel}: "{data["reglas"][r_idx]["nombre"]}" → {("+" if pts>0 else "")}{pts} pts'
    data["historial"].insert(0, accion)
    data["historial"] = data["historial"][:30]
    save_data(data)
    emoji = "🎉" if pts > 0 else "😬"
    st.success(f'{emoji} {accion}')
    st.rerun()

st.divider()

# ── Puntos manuales ───────────────────────────────────────
with st.expander("✏️ Sumar / restar puntos manualmente"):
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        j_manual = st.selectbox("Jugadora", nombres, key="manual_j")
    with c2:
        pts_manual = st.number_input("Puntos", value=1, step=1, key="manual_pts")
    with c3:
        st.write("")
        st.write("")
        if st.button("Aplicar", key="btn_manual"):
            j_idx = nombres.index(j_manual)
            data["jugadoras"][j_idx]["puntos"] += pts_manual
            hora = datetime.now().strftime("%H:%M")
            data["historial"].insert(0, f'{hora} — {j_manual}: {("+" if pts_manual>0 else "")}{pts_manual} pts (manual)')
            data["historial"] = data["historial"][:30]
            save_data(data)
            st.rerun()

# ── Reglas ────────────────────────────────────────────────
with st.expander("📋 Ver y editar reglas"):
    for i, r in enumerate(data["reglas"]):
        c1, c2, c3 = st.columns([3,1,1])
        with c1:
            st.write(r["nombre"])
        with c2:
            pts = r["puntos"]
            color = "#2d7a4f" if pts > 0 else "#c0392b"
            st.markdown(f'<span style="color:{color};font-weight:700;font-family:Nunito,sans-serif">{("+" if pts>0 else "")}{pts}</span>', unsafe_allow_html=True)
        with c3:
            if st.button("🗑️", key=f"del_r_{i}"):
                data["reglas"].pop(i)
                save_data(data)
                st.rerun()

    st.write("**Agregar regla nueva:**")
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        nueva_regla = st.text_input("Nombre", placeholder="Ej: Trajo snacks 🍿", key="nueva_r")
    with c2:
        nuevos_pts = st.number_input("Pts", value=1, step=1, key="nueva_pts")
    with c3:
        st.write("")
        st.write("")
        if st.button("Agregar", key="btn_add_r"):
            if nueva_regla.strip():
                data["reglas"].append({"nombre": nueva_regla.strip(), "puntos": nuevos_pts})
                save_data(data)
                st.rerun()

# ── Jugadoras ─────────────────────────────────────────────
with st.expander("👥 Editar jugadoras"):
    for i, j in enumerate(data["jugadoras"]):
        c1, c2 = st.columns([4,1])
        with c1:
            nuevo_nombre = st.text_input("Nombre", value=j["nombre"], key=f"nombre_{i}")
            if nuevo_nombre != j["nombre"]:
                data["jugadoras"][i]["nombre"] = nuevo_nombre
                save_data(data)
        with c2:
            if len(data["jugadoras"]) > 1:
                st.write("")
                if st.button("🗑️", key=f"del_j_{i}"):
                    data["jugadoras"].pop(i)
                    save_data(data)
                    st.rerun()

    nueva_j = st.text_input("Nueva jugadora", placeholder="Nombre 🐸", key="nueva_j")
    if st.button("Agregar jugadora"):
        if nueva_j.strip():
            data["jugadoras"].append({"nombre": nueva_j.strip(), "puntos": 0})
            save_data(data)
            st.rerun()

# ── Historial ─────────────────────────────────────────────
with st.expander("📜 Historial"):
    if data["historial"]:
        for h in data["historial"]:
            st.caption(f"🐸 {h}")
    else:
        st.caption("Sin movimientos aún... ¡empieza a leer! 📖")

st.divider()

# ── Reset ─────────────────────────────────────────────────
with st.expander("⚠️ Zona peligrosa"):
    st.markdown('<p style="color:#e87fbf;font-weight:700">¿Segura? Esto borrará todos los puntos 😬</p>', unsafe_allow_html=True)
    if st.button("🔄 Reiniciar todos los puntos a cero", type="secondary"):
        for j in data["jugadoras"]:
            j["puntos"] = 0
        data["historial"].insert(0, f'{datetime.now().strftime("%H:%M")} — Puntos reiniciados 🔄')
        save_data(data)
        st.rerun()

# ── Footer ─────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:1.5rem 0 1rem;color:#a8d8bf;font-size:13px;font-weight:600'>
    🐸 Sapi Club · hecho con amor y letras 🐸
</div>
""", unsafe_allow_html=True)
