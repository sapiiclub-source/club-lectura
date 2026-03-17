import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Club de Lectura", page_icon="📚", layout="centered")

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "jugadoras": [
            {"nombre": "Jugadora 1", "puntos": 0},
            {"nombre": "Jugadora 2", "puntos": 0},
            {"nombre": "Jugadora 3", "puntos": 0},
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

st.title("📚 Club de Lectura")
st.caption("Marcador de comportamiento lector")

# ── Marcador ──────────────────────────────────────────────
st.subheader("🏆 Marcador")

sorted_j = sorted(enumerate(data["jugadoras"]), key=lambda x: x[1]["puntos"], reverse=True)
cols = st.columns(len(data["jugadoras"]))

for col_idx, (j_idx, j) in enumerate(sorted_j):
    with cols[col_idx]:
        pts = j["puntos"]
        color = "#1D9E75" if pts > 0 else ("#993C1D" if pts < 0 else "#888780")
        lider = col_idx == 0 and pts > 0
        st.markdown(f"""
        <div style='text-align:center;padding:12px 6px;background:var(--background-color);
                    border:1.5px solid {"#1D9E75" if lider else "#ddd"};
                    border-radius:12px;margin-bottom:6px'>
            {"⭐ " if lider else ""}<b>{j["nombre"]}</b><br>
            <span style='font-size:28px;font-weight:600;color:{color}'>
                {("+" if pts > 0 else "")}{pts}
            </span><br>
            <span style='font-size:11px;color:gray'>puntos</span>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Aplicar regla ─────────────────────────────────────────
st.subheader("⚡ Aplicar regla")

c1, c2 = st.columns(2)
with c1:
    nombres = [j["nombre"] for j in data["jugadoras"]]
    jugadora_sel = st.selectbox("Jugadora", nombres, key="sel_j")
with c2:
    regla_nombres = [f'{r["nombre"]} ({("+" if r["puntos"]>0 else "")}{r["puntos"]})' for r in data["reglas"]]
    regla_sel = st.selectbox("Regla", regla_nombres, key="sel_r")

if st.button("✅ Aplicar", use_container_width=True, type="primary"):
    j_idx = nombres.index(jugadora_sel)
    r_idx = regla_nombres.index(regla_sel)
    pts = data["reglas"][r_idx]["puntos"]
    data["jugadoras"][j_idx]["puntos"] += pts
    hora = datetime.now().strftime("%H:%M")
    accion = f'{hora} — {jugadora_sel}: "{data["reglas"][r_idx]["nombre"]}" → {("+" if pts>0 else "")}{pts} pts'
    data["historial"].insert(0, accion)
    data["historial"] = data["historial"][:30]
    save_data(data)
    st.success(accion)
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

st.divider()

# ── Reglas ────────────────────────────────────────────────
with st.expander("📋 Ver y editar reglas"):
    for i, r in enumerate(data["reglas"]):
        c1, c2, c3 = st.columns([3,1,1])
        with c1:
            st.write(r["nombre"])
        with c2:
            pts = r["puntos"]
            color = "green" if pts > 0 else "red"
            st.markdown(f'<span style="color:{color};font-weight:600">{("+" if pts>0 else "")}{pts}</span>', unsafe_allow_html=True)
        with c3:
            if st.button("🗑️", key=f"del_r_{i}"):
                data["reglas"].pop(i)
                save_data(data)
                st.rerun()

    st.write("**Agregar regla nueva:**")
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        nueva_regla = st.text_input("Nombre", placeholder="Ej: Trajo snacks", key="nueva_r")
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

st.divider()

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

    nueva_j = st.text_input("Nueva jugadora", placeholder="Nombre", key="nueva_j")
    if st.button("Agregar jugadora"):
        if nueva_j.strip():
            data["jugadoras"].append({"nombre": nueva_j.strip(), "puntos": 0})
            save_data(data)
            st.rerun()

st.divider()

# ── Historial ─────────────────────────────────────────────
with st.expander("📜 Historial"):
    if data["historial"]:
        for h in data["historial"]:
            st.caption(h)
    else:
        st.caption("Sin movimientos aún.")

st.divider()

# ── Reset ─────────────────────────────────────────────────
with st.expander("⚠️ Zona peligrosa"):
    if st.button("🔄 Reiniciar todos los puntos a cero", type="secondary"):
        for j in data["jugadoras"]:
            j["puntos"] = 0
        data["historial"].insert(0, f'{datetime.now().strftime("%H:%M")} — Puntos reiniciados')
        save_data(data)
        st.rerun()
