import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Sapi Club 🐸", page_icon="🐸", layout="centered")

DATA_FILE = "data.json"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #e8f8f0 0%, #e0f4fb 50%, #fce8f3 100%); min-height: 100vh; }
.main .block-container { padding-top: 1.5rem; max-width: 700px; }
h1 { color: #2d7a4f !important; }
h2, h3 { color: #2d7a4f !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3dba75, #2d9e62) !important;
    color: white !important; border: none !important; border-radius: 20px !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
    font-size: 15px !important; padding: 10px 20px !important;
    box-shadow: 0 4px 12px rgba(45,154,98,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2d9e62, #236e47) !important;
    transform: translateY(-1px); box-shadow: 0 6px 16px rgba(45,154,98,0.4) !important;
}
.stButton > button[kind="secondary"], .stButton > button {
    background: white !important; color: #2d7a4f !important;
    border: 2px solid #a8e6c4 !important; border-radius: 20px !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 600 !important;
}
.stButton > button:hover { border-color: #3dba75 !important; background: #f0faf5 !important; }
.stSelectbox > div > div { border-radius: 14px !important; border-color: #a8e6c4 !important; background: white !important; font-family: 'Nunito', sans-serif !important; }
.stTextInput > div > div > input, .stNumberInput > div > div > input { border-radius: 14px !important; border-color: #a8e6c4 !important; background: white !important; font-family: 'Nunito', sans-serif !important; }
.streamlit-expanderHeader { background: white !important; border-radius: 16px !important; border: 2px solid #d4f0e4 !important; color: #2d7a4f !important; font-family: 'Nunito', sans-serif !important; font-weight: 700 !important; }
.streamlit-expanderContent { background: #f7fefb !important; border: 2px solid #d4f0e4 !important; border-top: none !important; border-radius: 0 0 16px 16px !important; }
hr { border-color: #c5ebd8 !important; }
.stAlert { border-radius: 16px !important; font-family: 'Nunito', sans-serif !important; }
.stCaption { color: #6abf8a !important; font-family: 'Nunito', sans-serif !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #e8f8f0; }
::-webkit-scrollbar-thumb { background: #a8e6c4; border-radius: 10px; }
div[data-testid="stTabs"] button { font-family: 'Nunito', sans-serif !important; font-weight: 700 !important; font-size: 15px !important; color: #2d7a4f !important; }
</style>
""", unsafe_allow_html=True)


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        if "libros" not in d:
            d["libros"] = []
        for libro in d["libros"]:
            # migrar formato viejo
            if "valoraciones" not in libro:
                libro["valoraciones"] = {}
            if "estados_miembro" not in libro:
                libro["estados_miembro"] = {}
            if "comentarios" not in libro:
                libro["comentarios"] = {}
            libro.pop("valoracion", None)
            libro.pop("comentario", None)
        return d
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
        "historial": [],
        "libros": []
    }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_data()

st.markdown("""
<div style='text-align:center;padding:1rem 0 0.5rem'>
    <div style='font-size:52px;line-height:1.1'>🐸</div>
    <h1 style='font-size:2.2rem;font-weight:800;color:#2d7a4f;margin:4px 0 0'>Sapi Club</h1>
    <p style='color:#6abf8a;font-size:14px;margin:2px 0 0;font-weight:600'>✨ Marcador de lectura sapistica ✨</p>
</div>
""", unsafe_allow_html=True)

st.divider()

tab_puntos, tab_libros = st.tabs(["🏆 Puntos", "📚 Libros"])


# ╔══════════════════════╗
# ║    TAB: PUNTOS       ║
# ╚══════════════════════╝
with tab_puntos:

    st.markdown("### 🏆 Marcador")
    sorted_j = sorted(enumerate(data["jugadoras"]), key=lambda x: x[1]["puntos"], reverse=True)
    cols = st.columns(len(data["jugadoras"]))
    card_colors   = ["#d4f0e4", "#d4edf7", "#fce8f3"]
    text_colors   = ["#2d7a4f", "#1a6a8a", "#a0417a"]
    border_colors = ["#3dba75", "#5bc0e8", "#e87fbf"]
    card_icons    = ["🐸", "🐟", "🌸"]

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
            st.markdown(
                "<div style='text-align:center;padding:14px 8px 10px;background:" + bg +
                ";border:" + bw + " solid " + bc + ";border-radius:20px;margin-bottom:4px;"
                "box-shadow:0 4px 12px rgba(0,0,0,0.06)'>"
                "<div style='font-size:28px'>" + icon + "</div>"
                "<div style='font-weight:800;color:" + tc + ";font-size:14px;margin:4px 0 2px'>" + crown + j["nombre"] + "</div>"
                "<div style='font-size:30px;font-weight:800;color:" + pts_color + ";line-height:1.1'>" +
                ("+" if pts > 0 else "") + str(pts) + "</div>"
                "<div style='font-size:11px;color:#999;font-weight:600'>puntos</div></div>",
                unsafe_allow_html=True
            )

    st.divider()
    st.markdown("### ⚡ Aplicar regla")
    c1, c2 = st.columns(2)
    with c1:
        nombres = [j["nombre"] for j in data["jugadoras"]]
        jugadora_sel = st.selectbox("🐸 Jugadora", nombres, key="sel_j")
    with c2:
        regla_nombres = [r["nombre"] + " (" + ("+" if r["puntos"] > 0 else "") + str(r["puntos"]) + ")" for r in data["reglas"]]
        regla_sel = st.selectbox("📖 Regla", regla_nombres, key="sel_r")

    if st.button("✅ Aplicar puntos", use_container_width=True, type="primary"):
        j_idx = nombres.index(jugadora_sel)
        r_idx = regla_nombres.index(regla_sel)
        pts = data["reglas"][r_idx]["puntos"]
        data["jugadoras"][j_idx]["puntos"] += pts
        hora = datetime.now().strftime("%H:%M")
        accion = hora + " — " + jugadora_sel + ': "' + data["reglas"][r_idx]["nombre"] + '" → ' + ("+" if pts > 0 else "") + str(pts) + " pts"
        data["historial"].insert(0, accion)
        data["historial"] = data["historial"][:30]
        save_data(data)
        st.success(("🎉" if pts > 0 else "😬") + " " + accion)
        st.rerun()

    st.divider()

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
                data["historial"].insert(0, hora + " — " + j_manual + ": " + ("+" if pts_manual > 0 else "") + str(pts_manual) + " pts (manual)")
                data["historial"] = data["historial"][:30]
                save_data(data)
                st.rerun()

    with st.expander("📋 Ver y editar reglas"):
        for i, r in enumerate(data["reglas"]):
            c1, c2, c3 = st.columns([3,1,1])
            with c1:
                st.write(r["nombre"])
            with c2:
                pts = r["puntos"]
                color = "#2d7a4f" if pts > 0 else "#c0392b"
                st.markdown("<span style='color:" + color + ";font-weight:700;font-family:Nunito,sans-serif'>" + ("+" if pts > 0 else "") + str(pts) + "</span>", unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key="del_r_" + str(i)):
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

    with st.expander("👥 Editar jugadoras"):
        for i, j in enumerate(data["jugadoras"]):
            c1, c2 = st.columns([4,1])
            with c1:
                nuevo_nombre = st.text_input("Nombre", value=j["nombre"], key="nombre_" + str(i))
                if nuevo_nombre != j["nombre"]:
                    data["jugadoras"][i]["nombre"] = nuevo_nombre
                    save_data(data)
            with c2:
                if len(data["jugadoras"]) > 1:
                    st.write("")
                    if st.button("🗑️", key="del_j_" + str(i)):
                        data["jugadoras"].pop(i)
                        save_data(data)
                        st.rerun()
        nueva_j = st.text_input("Nueva jugadora", placeholder="Nombre 🐸", key="nueva_j")
        if st.button("Agregar jugadora"):
            if nueva_j.strip():
                data["jugadoras"].append({"nombre": nueva_j.strip(), "puntos": 0})
                save_data(data)
                st.rerun()

    with st.expander("📜 Historial"):
        if data["historial"]:
            for h in data["historial"]:
                st.caption("🐸 " + h)
        else:
            st.caption("Sin movimientos aún... ¡empieza a leer! 📖")

    st.divider()

    with st.expander("⚠️ Zona peligrosa"):
        st.markdown("<p style='color:#e87fbf;font-weight:700'>¿Segura? Esto borrará todos los puntos 😬</p>", unsafe_allow_html=True)
        if st.button("🔄 Reiniciar todos los puntos a cero", type="secondary"):
            for j in data["jugadoras"]:
                j["puntos"] = 0
            data["historial"].insert(0, datetime.now().strftime("%H:%M") + " — Puntos reiniciados 🔄")
            save_data(data)
            st.rerun()


# ╔══════════════════════╗
# ║    TAB: LIBROS       ║
# ╚══════════════════════╝
with tab_libros:

    ESTADOS_M = {
        "leyendo":   {"label": "Leyendo",   "emoji": "📖", "color": "#d4edf7", "border": "#5bc0e8", "text": "#1a6a8a"},
        "leido":     {"label": "Leído",     "emoji": "✅", "color": "#d4f0e4", "border": "#3dba75", "text": "#2d7a4f"},
        "pendiente": {"label": "Pendiente", "emoji": "🕐", "color": "#fce8f3", "border": "#e87fbf", "text": "#a0417a"},
        "sin_estado":{"label": "Sin estado","emoji": "·",  "color": "#f1f1f1", "border": "#ccc",    "text": "#999"},
    }

    def estrellas(n):
        if not n:
            return "☆☆☆☆☆"
        n_round = round(n)
        return "⭐" * n_round + "☆" * (5 - n_round)

    def promedio_vals(libro):
        vals = libro.get("valoraciones", {})
        valores = [v for v in vals.values() if v and v > 0]
        return round(sum(valores) / len(valores), 1) if valores else 0

    def render_tarjeta_miembro(nombre, estado_key, val, comentario):
        """Renderiza la tarjeta pequeña de una miembro para un libro."""
        em = ESTADOS_M.get(estado_key, ESTADOS_M["sin_estado"])
        stars = estrellas(val) if val and val > 0 else ""
        val_str = " " + str(val) + "/5" if val and val > 0 else ""
        comentario_html = ""
        if comentario and comentario.strip():
            comentario_html = (
                "<div style='margin-top:5px;font-size:12px;color:#555;font-style:italic;"
                "background:rgba(255,255,255,0.7);border-radius:8px;padding:4px 8px;line-height:1.4'>"
                "💬 " + comentario + "</div>"
            )
        return (
            "<div style='background:" + em["color"] + ";border:1.5px solid " + em["border"] + ";"
            "border-radius:14px;padding:10px 12px;flex:1;min-width:120px'>"
            "<div style='font-weight:800;color:" + em["text"] + ";font-size:13px;margin-bottom:3px'>" + nombre + "</div>"
            "<div style='font-size:11px;color:" + em["text"] + ";font-weight:600;margin-bottom:4px'>" +
            em["emoji"] + " " + em["label"] + "</div>"
            + ("<div style='font-size:14px;line-height:1'>" + stars + "<span style='font-size:11px;color:" + em["text"] + ";font-weight:700'>" + val_str + "</span></div>" if stars else "") +
            comentario_html +
            "</div>"
        )

    def render_libro_card(libro, idx, nombres_jugadoras):
        """Renderiza la tarjeta principal del libro con tarjetas de miembros."""
        autora = libro.get("autora", "")
        prom = promedio_vals(libro)

        # Header del libro
        html = (
            "<div style='background:white;border:2px solid #c5ebd8;border-radius:20px;"
            "padding:16px;margin-bottom:8px;box-shadow:0 4px 14px rgba(0,0,0,0.06)'>"
            "<div style='display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:8px'>"
            "<div>"
            "<div style='font-weight:800;color:#2d7a4f;font-size:17px'>📚 " + libro["titulo"] + "</div>"
        )
        if autora:
            html += "<div style='font-size:13px;color:#888;font-weight:600;margin-top:2px'>✍️ " + autora + "</div>"
        html += "</div>"

        # Promedio general
        if prom > 0:
            html += (
                "<div style='text-align:right'>"
                "<div style='font-size:16px;line-height:1'>" + estrellas(prom) + "</div>"
                "<div style='font-size:12px;color:#2d7a4f;font-weight:700'>" + str(prom) + "/5 promedio</div>"
                "</div>"
            )
        html += "</div>"

        # Tarjetas por miembro
        html += "<div style='display:flex;gap:8px;flex-wrap:wrap'>"
        for nombre in nombres_jugadoras:
            estado_m = libro.get("estados_miembro", {}).get(nombre, "sin_estado")
            val_m    = libro.get("valoraciones", {}).get(nombre, 0)
            com_m    = libro.get("comentarios", {}).get(nombre, "")
            html += render_tarjeta_miembro(nombre, estado_m, val_m, com_m)
        html += "</div></div>"

        st.markdown(html, unsafe_allow_html=True)

    # ── Contadores globales ────────────────────────────────────
    libros = data.get("libros", [])
    nombres_jugadoras = [j["nombre"] for j in data["jugadoras"]]

    n_total     = len(libros)
    n_con_leido = sum(1 for l in libros if any(
        l.get("estados_miembro", {}).get(n) == "leido" for n in nombres_jugadoras
    ))

    st.markdown(
        "<div style='display:flex;gap:10px;margin-bottom:4px'>"
        "<div style='background:#d4f0e4;border-radius:14px;padding:10px 16px;flex:1;text-align:center'>"
        "<div style='font-size:22px;font-weight:800;color:#2d7a4f'>" + str(n_total) + "</div>"
        "<div style='font-size:12px;color:#2d7a4f;font-weight:700'>Total libros 📚</div></div>"
        "<div style='background:#d4edf7;border-radius:14px;padding:10px 16px;flex:1;text-align:center'>"
        "<div style='font-size:22px;font-weight:800;color:#1a6a8a'>" + str(n_con_leido) + "</div>"
        "<div style='font-size:12px;color:#1a6a8a;font-weight:700'>Con al menos 1 leído ✅</div></div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # ── Agregar libro ──────────────────────────────────────────
    with st.expander("➕ Agregar libro"):
        c1, c2 = st.columns(2)
        with c1:
            nuevo_titulo = st.text_input("Título *", placeholder="Ej: El principito", key="lib_titulo")
        with c2:
            nueva_autora = st.text_input("Autora/Autor", placeholder="Ej: Saint-Exupéry", key="lib_autora")
        if st.button("📚 Agregar libro", type="primary", use_container_width=True):
            if nuevo_titulo.strip():
                data["libros"].append({
                    "titulo": nuevo_titulo.strip(),
                    "autora": nueva_autora.strip(),
                    "valoraciones": {},
                    "estados_miembro": {},
                    "comentarios": {},
                    "fecha_agregado": datetime.now().strftime("%d/%m/%Y")
                })
                save_data(data)
                st.success('📚 "' + nuevo_titulo.strip() + '" agregado!')
                st.rerun()
            else:
                st.warning("El título no puede estar vacío 🐸")

    st.divider()

    if not libros:
        st.markdown(
            "<div style='text-align:center;padding:2rem;color:#6abf8a;font-weight:600'>"
            "<div style='font-size:40px'>📚</div>"
            "<p>¡Aún no hay libros! Agrega el primero arriba 🐸</p></div>",
            unsafe_allow_html=True
        )
    else:
        # ── Sub-pestañas por estado ────────────────────────────
        def libros_para_subtab(estado_filtro):
            """Devuelve libros donde AL MENOS UNA miembro tiene ese estado, o todos si es pendiente."""
            if estado_filtro == "pendiente":
                # pendiente = alguna miembro no ha leído aún (no tiene estado o es leyendo/pendiente)
                resultado = []
                for i, l in enumerate(libros):
                    estados_m = l.get("estados_miembro", {})
                    tiene_pendiente = any(
                        estados_m.get(n, "pendiente") in ("pendiente", "sin_estado", "leyendo")
                        for n in nombres_jugadoras
                    )
                    if tiene_pendiente:
                        resultado.append((i, l))
                return resultado
            else:
                return [
                    (i, l) for i, l in enumerate(libros)
                    if any(l.get("estados_miembro", {}).get(n) == estado_filtro for n in nombres_jugadoras)
                ]

        sub_leyendo  = libros_para_subtab("leyendo")
        sub_leido    = libros_para_subtab("leido")
        sub_pendiente= libros_para_subtab("pendiente")

        stab1, stab2, stab3 = st.tabs([
            "📖 Leyendo (" + str(len(sub_leyendo)) + ")",
            "✅ Leídos (" + str(len(sub_leido)) + ")",
            "🕐 Pendientes (" + str(len(sub_pendiente)) + ")",
        ])

        def render_lista_libros(lista_libros, subtab_key):
            if not lista_libros:
                st.markdown(
                    "<div style='text-align:center;padding:1.5rem;color:#a8d8bf;font-weight:600'>"
                    "No hay libros aquí todavía 🐸</div>",
                    unsafe_allow_html=True
                )
                return
            for idx, libro in lista_libros:
                render_libro_card(libro, idx, nombres_jugadoras)

                with st.expander("✏️ Editar · " + libro["titulo"]):
                    # Datos básicos
                    c1, c2 = st.columns(2)
                    with c1:
                        ed_titulo = st.text_input("Título", value=libro["titulo"], key=subtab_key + "_titulo_" + str(idx))
                        ed_autora = st.text_input("Autora/Autor", value=libro.get("autora", ""), key=subtab_key + "_autora_" + str(idx))

                    st.markdown("---")
                    st.markdown("**👤 ¿Quién quiere actualizar su estado?**")

                    # Selector de miembro — la key incluye idx para aislarlo por libro
                    quien_key = subtab_key + "_quien_" + str(idx)
                    nombre_sel = st.selectbox(
                        "Miembro",
                        options=nombres_jugadoras,
                        key=quien_key
                    )

                    # Las keys de los campos incluyen el nombre: al cambiar miembro, son campos distintos
                    estm_key = subtab_key + "_estm_" + str(idx) + "_" + nombre_sel
                    val_key  = subtab_key + "_val_"  + str(idx) + "_" + nombre_sel
                    com_key  = subtab_key + "_com_"  + str(idx) + "_" + nombre_sel

                    # Cargar valores guardados de esta miembro como default (solo si la key no existe aún)
                    if estm_key not in st.session_state:
                        st.session_state[estm_key] = libro.get("estados_miembro", {}).get(nombre_sel, "pendiente")
                    if val_key not in st.session_state:
                        st.session_state[val_key] = libro.get("valoraciones", {}).get(nombre_sel, 0) or 0
                    if com_key not in st.session_state:
                        st.session_state[com_key] = libro.get("comentarios", {}).get(nombre_sel, "")

                    c1, c2 = st.columns(2)
                    with c1:
                        ed_estado_m = st.selectbox(
                            "Estado",
                            options=["pendiente", "leyendo", "leido"],
                            format_func=lambda x: {"pendiente": "🕐 Pendiente", "leyendo": "📖 Leyendo", "leido": "✅ Leído"}[x],
                            key=estm_key
                        )
                    with c2:
                        ed_val_m = st.slider(
                            "Valoración ⭐",
                            min_value=0, max_value=5,
                            key=val_key
                        )

                    ed_com_m = st.text_area(
                        "Comentario 💬",
                        placeholder="¿Qué piensa " + nombre_sel + " del libro?",
                        key=com_key,
                        height=80
                    )

                    cc1, cc2 = st.columns([3, 1])
                    with cc1:
                        if st.button("💾 Guardar para " + nombre_sel, key=subtab_key + "_save_" + str(idx), type="primary"):
                            if "estados_miembro" not in data["libros"][idx]:
                                data["libros"][idx]["estados_miembro"] = {}
                            if "valoraciones" not in data["libros"][idx]:
                                data["libros"][idx]["valoraciones"] = {}
                            if "comentarios" not in data["libros"][idx]:
                                data["libros"][idx]["comentarios"] = {}
                            data["libros"][idx]["estados_miembro"][nombre_sel] = ed_estado_m
                            data["libros"][idx]["valoraciones"][nombre_sel] = ed_val_m
                            data["libros"][idx]["comentarios"][nombre_sel] = ed_com_m.strip()
                            data["libros"][idx]["titulo"] = ed_titulo.strip() or libro["titulo"]
                            data["libros"][idx]["autora"] = ed_autora.strip()
                            save_data(data)
                            # Borrar keys de esta miembro para que recarguen desde data la próxima vez
                            for k in [estm_key, val_key, com_key, quien_key]:
                                if k in st.session_state:
                                    del st.session_state[k]
                            st.success("¡Guardado para " + nombre_sel + "! 🐸")
                            st.rerun()
                    with cc2:
                        st.write("")
                        if st.button("🗑️ Eliminar", key=subtab_key + "_del_" + str(idx)):
                            data["libros"].pop(idx)
                            save_data(data)
                            st.rerun()

        with stab1:
            render_lista_libros(sub_leyendo, "ley")
        with stab2:
            render_lista_libros(sub_leido, "lei")
        with stab3:
            render_lista_libros(sub_pendiente, "pen")

st.markdown(
    "<div style='text-align:center;padding:1.5rem 0 1rem;color:#a8d8bf;font-size:13px;font-weight:600'>"
    "🐸 Sapi Club · hecho con amor y letras 🐸</div>",
    unsafe_allow_html=True
)
