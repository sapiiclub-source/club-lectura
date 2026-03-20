import streamlit as st
import json
import os
import requests
from datetime import datetime, date

st.set_page_config(page_title="Sapi Club 🐸", page_icon="🐸", layout="centered")
DATA_FILE = "data.json"

# ── Supabase persistence ────────────────────────────────────
def _sb_url():
    return st.secrets.get("SUPABASE_URL", "") + "/rest/v1/app_data"

def _sb_headers():
    key = st.secrets.get("SUPABASE_KEY", "")
    return {
        "apikey": key,
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def load_from_supabase():
    try:
        r = requests.get(_sb_url() + "?id=eq.1&select=value", headers=_sb_headers(), timeout=10)
        if r.status_code == 200:
            rows = r.json()
            if rows:
                return json.loads(rows[0]["value"])
    except Exception:
        pass
    return None

def save_to_supabase(data):
    try:
        payload = json.dumps({"value": json.dumps(data, ensure_ascii=False)})
        r = requests.patch(_sb_url() + "?id=eq.1", headers=_sb_headers(), data=payload, timeout=10)
        return r.status_code in (200, 201, 204)
    except Exception:
        pass
    return False

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #e8f8f0 0%, #e0f4fb 50%, #fce8f3 100%); min-height: 100vh; }
.main .block-container { padding-top: 1.5rem; max-width: 700px; }
h1 { color: #2d7a4f !important; } h2, h3 { color: #2d7a4f !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3dba75, #2d9e62) !important;
    color: white !important; border: none !important; border-radius: 20px !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
    font-size: 15px !important; padding: 10px 20px !important;
    box-shadow: 0 4px 12px rgba(45,154,98,0.3) !important;
}
.stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #2d9e62, #236e47) !important; transform: translateY(-1px); }
.stButton > button[kind="secondary"], .stButton > button { background: white !important; color: #2d7a4f !important; border: 2px solid #a8e6c4 !important; border-radius: 20px !important; font-family: 'Nunito', sans-serif !important; font-weight: 600 !important; }
.stButton > button:hover { border-color: #3dba75 !important; background: #f0faf5 !important; }
.stSelectbox > div > div { border-radius: 14px !important; border-color: #a8e6c4 !important; background: white !important; }
.stTextInput > div > div > input, .stNumberInput > div > div > input { border-radius: 14px !important; border-color: #a8e6c4 !important; background: white !important; }
.streamlit-expanderHeader { background: white !important; border-radius: 16px !important; border: 2px solid #d4f0e4 !important; color: #2d7a4f !important; font-weight: 700 !important; }
.streamlit-expanderContent { background: #f7fefb !important; border: 2px solid #d4f0e4 !important; border-top: none !important; border-radius: 0 0 16px 16px !important; }
hr { border-color: #c5ebd8 !important; }
.stAlert { border-radius: 16px !important; }
.stCaption { color: #6abf8a !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #e8f8f0; } ::-webkit-scrollbar-thumb { background: #a8e6c4; border-radius: 10px; }
div[data-testid="stTabs"] button { font-family: 'Nunito', sans-serif !important; font-weight: 700 !important; font-size: 15px !important; color: #2d7a4f !important; }
</style>
""", unsafe_allow_html=True)

GENEROS = ["Sin género", "Romance", "Fantasía", "Terror", "Ciencia ficción", "Drama", "Misterio", "Histórico", "Aventura", "Autoayuda", "Poesía", "Otro"]

DEFAULT_DATA = {
    "jugadoras": [{"nombre": "Sapi 1", "puntos": 0}, {"nombre": "Sapi 2", "puntos": 0}, {"nombre": "Sapi 3", "puntos": 0}],
    "reglas": [
        {"nombre": "Leyó el capítulo completo", "puntos": 3}, {"nombre": "Llegó a tiempo", "puntos": 2},
        {"nombre": "Aportó al debate", "puntos": 2}, {"nombre": "No leyó", "puntos": -3},
        {"nombre": "Llegó tarde", "puntos": -1}, {"nombre": "Spoileó sin avisar", "puntos": -2},
    ],
    "historial": [], "historial_puntos": {}, "libros": [],
    "agenda": [], "meta_anio": 12, "libro_actual": "", "votacion": {"propuestas": [], "activa": False}
}

def migrate(d):
    if "libros" not in d: d["libros"] = []
    if "agenda" not in d: d["agenda"] = []
    if "meta_anio" not in d: d["meta_anio"] = 12
    if "libro_actual" not in d: d["libro_actual"] = ""
    if "votacion" not in d: d["votacion"] = {"propuestas": [], "activa": False}
    if "historial_puntos" not in d: d["historial_puntos"] = {}
    for libro in d["libros"]:
        if "valoraciones" not in libro: libro["valoraciones"] = {}
        if "estados_miembro" not in libro: libro["estados_miembro"] = {}
        if "comentarios" not in libro: libro["comentarios"] = {}
        if "genero" not in libro: libro["genero"] = "Sin género"
        if "portada_url" not in libro: libro["portada_url"] = ""
        if "fecha_inicio" not in libro: libro["fecha_inicio"] = ""
        if "fecha_fin" not in libro: libro["fecha_fin"] = ""
        if "fechas_miembro" not in libro: libro["fechas_miembro"] = {}
        libro.pop("valoracion", None); libro.pop("comentario", None)
    return d

def load_data():
    # Usar session_state como caché — solo consulta Supabase una vez por sesión
    if "_data_cache" in st.session_state:
        return st.session_state["_data_cache"]
    d = load_from_supabase()
    if d is None:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
        else:
            d = DEFAULT_DATA.copy()
    d = migrate(d)
    st.session_state["_data_cache"] = d
    return d

def save_data(data):
    # Actualizar caché inmediatamente para que la UI sea instantánea
    st.session_state["_data_cache"] = data
    # Guardar en Supabase
    save_to_supabase(data)

def estrellas(n):
    if not n: return "☆☆☆☆☆"
    n_round = round(n)
    return "⭐" * n_round + "☆" * (5 - n_round)

def promedio_vals(libro):
    vals = libro.get("valoraciones", {})
    valores = [v for v in vals.values() if v and v > 0]
    return round(sum(valores) / len(valores), 1) if valores else 0

data = load_data()
nombres_jugadoras = [j["nombre"] for j in data["jugadoras"]]

TABS = ["🏆 Puntos", "📚 Biblioteca", "⭐ Lecturas", "🗳️ Votación", "📅 Agenda", "📊 Estadísticas"]

# ── Header ─────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:1rem 0 0.5rem'>
    <div style='font-size:52px;line-height:1.1'>🐸</div>
    <h1 style='font-size:2.2rem;font-weight:800;color:#2d7a4f;margin:4px 0 0'>Sapi Club</h1>
    <p style='color:#6abf8a;font-size:14px;margin:2px 0 0;font-weight:600'>✨ Marcador de lectura sapistica ✨</p>
</div>
""", unsafe_allow_html=True)

# Libro actual destacado
if data.get("libro_actual"):
    portada_actual = ""
    autora_actual = ""
    for _lb in data.get("libros", []):
        if _lb["titulo"] == data["libro_actual"]:
            portada_actual = _lb.get("portada_url", "")
            autora_actual  = _lb.get("autora", "")
            break
    img_html = ""
    if portada_actual:
        img_html = "<img src='" + portada_actual + "' style='width:64px;height:96px;object-fit:cover;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.15);flex-shrink:0' onerror=\"this.style.display='none\"'>"
    st.markdown(
        "<div style='background:linear-gradient(135deg,#d4f0e4,#d4edf7);border:2px solid #3dba75;"
        "border-radius:18px;padding:14px 18px;margin:8px 0;display:flex;align-items:center;justify-content:center;gap:14px'>"
        + img_html +
        "<div style='text-align:center'>"
        "<div style='font-size:12px;color:#2d7a4f;font-weight:700;margin-bottom:2px'>📖 Leyendo ahora en el club</div>"
        "<div style='font-size:18px;font-weight:800;color:#1a6a8a;line-height:1.2'>" + data["libro_actual"] + "</div>"
        + ("<div style='font-size:13px;color:#2d7a4f;margin-top:2px'>✍️ " + autora_actual + "</div>" if autora_actual else "") +
        "</div></div>",
        unsafe_allow_html=True
    )

st.divider()

tab_puntos, tab_biblioteca, tab_lecturas, tab_votacion, tab_agenda, tab_stats = st.tabs(TABS)


# ╔══════════════════════╗
# ║    TAB: PUNTOS       ║
# ╚══════════════════════╝
with tab_puntos:
    st.markdown("### 🏆 Marcador")
    sorted_j = sorted(enumerate(data["jugadoras"]), key=lambda x: x[1]["puntos"], reverse=True)
    cols = st.columns(len(data["jugadoras"]))
    card_colors = ["#d4f0e4","#d4edf7","#fce8f3"]; text_colors = ["#2d7a4f","#1a6a8a","#a0417a"]
    border_colors = ["#3dba75","#5bc0e8","#e87fbf"]; card_icons = ["🐸","🐟","🌸"]

    for col_idx, (j_idx, j) in enumerate(sorted_j):
        with cols[col_idx]:
            pts = j["puntos"]
            pts_color = "#2d7a4f" if pts > 0 else ("#c0392b" if pts < 0 else "#888")
            lider = col_idx == 0 and pts > 0
            bg = card_colors[col_idx % 3]; tc = text_colors[col_idx % 3]
            bc = border_colors[col_idx % 3] if lider else "#ddd"; bw = "2.5px" if lider else "1.5px"
            icon = card_icons[col_idx % 3]; crown = "⭐ " if lider else ""
            st.markdown(
                "<div style='text-align:center;padding:14px 8px 10px;background:" + bg + ";border:" + bw + " solid " + bc + ";border-radius:20px;margin-bottom:4px;box-shadow:0 4px 12px rgba(0,0,0,0.06)'>"
                "<div style='font-size:28px'>" + icon + "</div>"
                "<div style='font-weight:800;color:" + tc + ";font-size:14px;margin:4px 0 2px'>" + crown + j["nombre"] + "</div>"
                "<div style='font-size:30px;font-weight:800;color:" + pts_color + ";line-height:1.1'>" + ("+" if pts > 0 else "") + str(pts) + "</div>"
                "<div style='font-size:11px;color:#999;font-weight:600'>puntos</div></div>",
                unsafe_allow_html=True
            )

    # Medallas
    st.divider()
    st.markdown("### 🏅 Medallas")

    mes_actual = datetime.now().strftime("%Y-%m")

    # Libros leidos en total por miembro
    libros_leidos_total = {n: 0 for n in nombres_jugadoras}
    # Libros leidos este mes por miembro (usando fecha_fin del miembro)
    libros_leidos_mes = {n: 0 for n in nombres_jugadoras}

    for libro in data.get("libros", []):
        for n in nombres_jugadoras:
            if libro.get("estados_miembro", {}).get(n) == "leido":
                libros_leidos_total[n] = libros_leidos_total.get(n, 0) + 1
                # Fecha fin individual del miembro
                fecha_fin_m = libro.get("fechas_miembro", {}).get(n, {}).get("fin", "")
                if fecha_fin_m and fecha_fin_m[:7] == mes_actual:
                    libros_leidos_mes[n] = libros_leidos_mes.get(n, 0) + 1

    # Lectora del mes: más libros terminados este mes
    max_mes = max(libros_leidos_mes.values())
    lectora_mes = max(libros_leidos_mes, key=libros_leidos_mes.get) if max_mes > 0 else ""

    # Más libros leídos en total
    max_total = max(libros_leidos_total.values())
    mas_lectora = max(libros_leidos_total, key=libros_leidos_total.get) if max_total > 0 else ""

    # Más envidiosa: menos libros leídos en total (solo si hay diferencia)
    min_total = min(libros_leidos_total.values())
    menos_lectora = min(libros_leidos_total, key=libros_leidos_total.get) if min_total < max_total else ""

    mes_nombre = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][datetime.now().month - 1]

    medallas_html = "<div style='display:flex;flex-wrap:wrap;gap:10px;margin-bottom:8px'>"

    if lectora_mes:
        medallas_html += (
            "<div style='background:#faeeda;border:2px solid #FAC775;border-radius:14px;padding:10px 14px;flex:1;min-width:140px;text-align:center'>"
            "<div style='font-size:24px'>🏅</div>"
            "<div style='font-weight:800;color:#854F0B;font-size:13px'>Lectora de " + mes_nombre + "</div>"
            "<div style='font-weight:700;color:#633806;font-size:15px'>" + lectora_mes + "</div>"
            "<div style='font-size:11px;color:#854F0B'>" + str(libros_leidos_mes[lectora_mes]) + " libro(s) este mes</div></div>"
        )
    else:
        medallas_html += (
            "<div style='background:#f5f5f5;border:2px solid #ddd;border-radius:14px;padding:10px 14px;flex:1;min-width:140px;text-align:center'>"
            "<div style='font-size:24px'>🏅</div>"
            "<div style='font-weight:800;color:#aaa;font-size:13px'>Lectora de " + mes_nombre + "</div>"
            "<div style='font-size:12px;color:#bbb'>Ninguna ha terminado un libro este mes</div></div>"
        )

    if mas_lectora:
        medallas_html += (
            "<div style='background:#d4f0e4;border:2px solid #3dba75;border-radius:14px;padding:10px 14px;flex:1;min-width:140px;text-align:center'>"
            "<div style='font-size:24px'>📚</div>"
            "<div style='font-weight:800;color:#2d7a4f;font-size:13px'>Más libros leídos</div>"
            "<div style='font-weight:700;color:#2d7a4f;font-size:15px'>" + mas_lectora + "</div>"
            "<div style='font-size:11px;color:#2d7a4f'>" + str(libros_leidos_total[mas_lectora]) + " en total</div></div>"
        )

    if menos_lectora:
        medallas_html += (
            "<div style='background:#fce8f3;border:2px solid #e87fbf;border-radius:14px;padding:10px 14px;flex:1;min-width:140px;text-align:center'>"
            "<div style='font-size:24px'>😤</div>"
            "<div style='font-weight:800;color:#a0417a;font-size:13px'>La más envidiosa</div>"
            "<div style='font-weight:700;color:#a0417a;font-size:15px'>" + menos_lectora + "</div>"
            "<div style='font-size:11px;color:#a0417a'>" + str(libros_leidos_total[menos_lectora]) + " en total</div></div>"
        )

    medallas_html += "</div>"
    st.markdown(medallas_html, unsafe_allow_html=True)

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
        data["historial"] = data["historial"][:50]
        # Guardar snapshot de puntos para gráfico
        hp = data.setdefault("historial_puntos", {})
        for j in data["jugadoras"]:
            hp.setdefault(j["nombre"], []).append(j["puntos"])
            hp[j["nombre"]] = hp[j["nombre"]][-50:]
        save_data(data)
        st.success(("🎉" if pts > 0 else "😬") + " " + accion)
        st.rerun()

    st.divider()
    with st.expander("✏️ Sumar / restar manualmente"):
        c1, c2, c3 = st.columns([2,1,1])
        with c1: j_manual = st.selectbox("Jugadora", nombres, key="manual_j")
        with c2: pts_manual = st.number_input("Puntos", value=1, step=1, key="manual_pts")
        with c3:
            st.write(""); st.write("")
            if st.button("Aplicar", key="btn_manual"):
                j_idx = nombres.index(j_manual)
                data["jugadoras"][j_idx]["puntos"] += pts_manual
                hora = datetime.now().strftime("%H:%M")
                data["historial"].insert(0, hora + " — " + j_manual + ": " + ("+" if pts_manual > 0 else "") + str(pts_manual) + " pts (manual)")
                data["historial"] = data["historial"][:50]
                hp = data.setdefault("historial_puntos", {})
                for j in data["jugadoras"]:
                    hp.setdefault(j["nombre"], []).append(j["puntos"])
                    hp[j["nombre"]] = hp[j["nombre"]][-50:]
                save_data(data)
                st.rerun()

    with st.expander("📋 Ver y editar reglas"):
        for i, r in enumerate(data["reglas"]):
            c1, c2, c3 = st.columns([3,1,1])
            with c1: st.write(r["nombre"])
            with c2:
                pts = r["puntos"]; color = "#2d7a4f" if pts > 0 else "#c0392b"
                st.markdown("<span style='color:" + color + ";font-weight:700'>" + ("+" if pts > 0 else "") + str(pts) + "</span>", unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key="del_r_" + str(i)):
                    data["reglas"].pop(i); save_data(data); st.rerun()
        st.write("**Agregar regla nueva:**")
        c1, c2, c3 = st.columns([3,1,1])
        with c1: nueva_regla = st.text_input("Nombre", placeholder="Ej: Trajo snacks 🍿", key="nueva_r")
        with c2: nuevos_pts = st.number_input("Pts", value=1, step=1, key="nueva_pts")
        with c3:
            st.write(""); st.write("")
            if st.button("Agregar", key="btn_add_r"):
                if nueva_regla.strip():
                    data["reglas"].append({"nombre": nueva_regla.strip(), "puntos": nuevos_pts})
                    save_data(data); st.rerun()

    with st.expander("👥 Editar jugadoras"):
        for i, j in enumerate(data["jugadoras"]):
            c1, c2 = st.columns([4,1])
            with c1:
                nuevo_nombre = st.text_input("Nombre", value=j["nombre"], key="nombre_" + str(i))
                if nuevo_nombre != j["nombre"]:
                    data["jugadoras"][i]["nombre"] = nuevo_nombre; save_data(data)
            with c2:
                if len(data["jugadoras"]) > 1:
                    st.write("")
                    if st.button("🗑️", key="del_j_" + str(i)):
                        data["jugadoras"].pop(i); save_data(data); st.rerun()
        nueva_j = st.text_input("Nueva jugadora", placeholder="Nombre 🐸", key="nueva_j")
        if st.button("Agregar jugadora"):
            if nueva_j.strip():
                data["jugadoras"].append({"nombre": nueva_j.strip(), "puntos": 0})
                save_data(data); st.rerun()

    with st.expander("📜 Historial"):
        if data["historial"]:
            for h in data["historial"]: st.caption("🐸 " + h)
        else: st.caption("Sin movimientos aún... ¡empieza a leer! 📖")

    st.divider()
    with st.expander("⚠️ Zona peligrosa"):
        st.markdown("<p style='color:#e87fbf;font-weight:700'>¿Segura? Estas acciones no se pueden deshacer 😬</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Reiniciar puntos a cero", type="secondary", use_container_width=True):
                for j in data["jugadoras"]: j["puntos"] = 0
                data["historial_puntos"] = {}
                data["historial"].insert(0, datetime.now().strftime("%H:%M") + " — Puntos reiniciados 🔄")
                save_data(data); st.rerun()
        with c2:
            if st.button("🗑️ Borrar historial", type="secondary", use_container_width=True):
                data["historial"] = []
                data["historial_puntos"] = {}
                save_data(data); st.success("Historial borrado 🐸"); st.rerun()


# ╔══════════════════════╗
# ║  TAB: BIBLIOTECA     ║
# ╚══════════════════════╝
with tab_biblioteca:

    ESTADOS_M = {
        "leyendo":   {"label": "Leyendo",   "emoji": "📖", "color": "#d4edf7", "border": "#5bc0e8", "text": "#1a6a8a"},
        "leido":     {"label": "Leído",     "emoji": "✅", "color": "#d4f0e4", "border": "#3dba75", "text": "#2d7a4f"},
        "pendiente": {"label": "Pendiente", "emoji": "🕐", "color": "#fce8f3", "border": "#e87fbf", "text": "#a0417a"},
        "sin_estado":{"label": "Sin estado","emoji": "·",  "color": "#f1f1f1", "border": "#ccc",    "text": "#999"},
    }

    def render_tarjeta_miembro(nombre, estado_key, val, comentario):
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
            "<div style='font-size:11px;color:" + em["text"] + ";font-weight:600;margin-bottom:4px'>" + em["emoji"] + " " + em["label"] + "</div>"
            + ("<div style='font-size:14px;line-height:1'>" + stars + "<span style='font-size:11px;color:" + em["text"] + ";font-weight:700'>" + val_str + "</span></div>" if stars else "")
            + comentario_html + "</div>"
        )

    def dias_tardados(libro):
        fi = libro.get("fecha_inicio", ""); ff = libro.get("fecha_fin", "")
        if fi and ff:
            try:
                d1 = datetime.strptime(fi, "%Y-%m-%d"); d2 = datetime.strptime(ff, "%Y-%m-%d")
                dias = (d2 - d1).days
                return str(dias) + " días"
            except: pass
        return ""

    def render_libro_card(libro, idx, nombres_jug):
        autora = libro.get("autora", ""); prom = promedio_vals(libro)
        portada = libro.get("portada_url", ""); genero = libro.get("genero", "")
        dias = dias_tardados(libro)
        fi = libro.get("fecha_inicio", ""); ff = libro.get("fecha_fin", "")

        html = (
            "<div style='background:white;border:2px solid #c5ebd8;border-radius:20px;"
            "padding:16px;margin-bottom:8px;box-shadow:0 4px 14px rgba(0,0,0,0.06)'>"
            "<div style='display:flex;gap:12px;margin-bottom:10px'>"
        )
        if portada:
            html += "<img src='" + portada + "' style='width:60px;height:90px;object-fit:cover;border-radius:8px;flex-shrink:0' onerror=\"this.style.display='none'\">"
        html += "<div style='flex:1'>"
        html += "<div style='display:flex;align-items:flex-start;justify-content:space-between'>"
        html += "<div><div style='font-weight:800;color:#2d7a4f;font-size:17px'>📚 " + libro["titulo"] + "</div>"
        if autora: html += "<div style='font-size:13px;color:#888;font-weight:600;margin-top:2px'>✍️ " + autora + "</div>"
        if genero and genero != "Sin género": html += "<div style='display:inline-block;background:#e8f8f0;color:#2d7a4f;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;margin-top:4px'>" + genero + "</div>"
        html += "</div>"
        if prom > 0:
            html += "<div style='text-align:right;flex-shrink:0'><div style='font-size:15px'>" + estrellas(prom) + "</div><div style='font-size:12px;color:#2d7a4f;font-weight:700'>" + str(prom) + "/5</div></div>"
        html += "</div>"
        if fi or ff or dias:
            fecha_html = "<div style='font-size:11px;color:#aaa;margin-top:6px'>"
            if fi: fecha_html += "Inicio: " + fi
            if ff: fecha_html += "  ·  Fin: " + ff
            if dias: fecha_html += "  ·  ⏱️ " + dias
            fecha_html += "</div>"
            html += fecha_html
        html += "</div></div>"
        html += "<div style='display:flex;gap:8px;flex-wrap:wrap'>"
        for nombre in nombres_jug:
            estado_m = libro.get("estados_miembro", {}).get(nombre, "sin_estado")
            val_m    = libro.get("valoraciones", {}).get(nombre, 0)
            com_m    = libro.get("comentarios", {}).get(nombre, "")
            html += render_tarjeta_miembro(nombre, estado_m, val_m, com_m)
        html += "</div></div>"
        st.markdown(html, unsafe_allow_html=True)

    libros = data.get("libros", [])

    # Libro actual del club
    st.markdown("**📖 Libro actual del club:**")
    c1, c2 = st.columns([3,1])
    with c1:
        libro_actual_input = st.text_input("", value=data.get("libro_actual",""), placeholder="Ej: De sangre y cenizas", key="libro_actual_inp", label_visibility="collapsed")
    with c2:
        if st.button("Guardar", key="save_libro_actual"):
            data["libro_actual"] = libro_actual_input.strip()
            save_data(data); st.rerun()

    # Meta del año
    st.divider()
    libros_leidos_total = sum(
        1 for l in libros
        if all(l.get("estados_miembro", {}).get(n) == "leido" for n in nombres_jugadoras)
    )
    meta = data.get("meta_anio", 12)
    progreso = min(libros_leidos_total / meta, 1.0) if meta > 0 else 0
    pct = int(progreso * 100)
    st.markdown(
        "<div style='background:white;border:2px solid #c5ebd8;border-radius:16px;padding:14px 16px'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>"
        "<span style='font-weight:800;color:#2d7a4f;font-size:14px'>🎯 Meta " + str(date.today().year) + "</span>"
        "<span style='font-weight:700;color:#1a6a8a;font-size:14px'>" + str(libros_leidos_total) + " / " + str(meta) + " libros</span></div>"
        "<div style='background:#e8f8f0;border-radius:20px;height:16px;overflow:hidden'>"
        "<div style='background:linear-gradient(90deg,#3dba75,#5bc0e8);height:100%;width:" + str(pct) + "%;border-radius:20px;transition:width 0.3s'></div></div>"
        "<div style='font-size:12px;color:#6abf8a;font-weight:600;margin-top:4px;text-align:right'>" + str(pct) + "%</div></div>",
        unsafe_allow_html=True
    )
    c1, c2 = st.columns([3,1])
    with c1:
        nueva_meta = st.number_input("Cambiar meta anual", min_value=1, max_value=100, value=meta, step=1, key="meta_inp")
    with c2:
        st.write("")
        if st.button("Guardar meta", key="save_meta"):
            data["meta_anio"] = nueva_meta; save_data(data); st.rerun()

    st.divider()

    with st.expander("➕ Agregar libro"):
        c1, c2 = st.columns(2)
        with c1:
            nuevo_titulo  = st.text_input("Título *", placeholder="Ej: El principito", key="lib_titulo")
            nueva_autora  = st.text_input("Autora/Autor", placeholder="Ej: Saint-Exupéry", key="lib_autora")
        with c2:
            nuevo_genero  = st.selectbox("Género", GENEROS, key="lib_genero")
            nueva_portada = st.text_input("URL portada (opcional)", placeholder="https://...", key="lib_portada")
        if st.button("📚 Agregar libro", type="primary", use_container_width=True):
            if nuevo_titulo.strip():
                data["libros"].append({
                    "titulo": nuevo_titulo.strip(), "autora": nueva_autora.strip(),
                    "genero": nuevo_genero, "portada_url": nueva_portada.strip(),
                    "valoraciones": {}, "estados_miembro": {}, "comentarios": {},
                    "fechas_miembro": {},
                    "fecha_agregado": datetime.now().strftime("%d/%m/%Y")
                })
                save_data(data)
                # Limpiar campos del formulario
                for k in ["lib_titulo", "lib_autora", "lib_portada", "lib_genero"]:
                    if k in st.session_state: del st.session_state[k]
                st.success('📚 "' + nuevo_titulo.strip() + '" agregado!'); st.rerun()
            else: st.warning("El título no puede estar vacío 🐸")

    # ── Editar libro (datos generales) ─────────────────────────
    if libros:
        with st.expander("✏️ Editar libro"):
            titulos = [l["titulo"] for l in libros]
            libro_edit_sel = st.selectbox("Selecciona un libro", titulos, key="edit_libro_sel")
            edit_idx = titulos.index(libro_edit_sel)
            libro_e = libros[edit_idx]

            # Keys incluyen edit_idx → campos distintos por libro, se limpian al cambiar selección
            t_key = "gedit_titulo_"  + str(edit_idx)
            a_key = "gedit_autora_"  + str(edit_idx)
            p_key = "gedit_portada_" + str(edit_idx)
            g_key = "gedit_genero_"  + str(edit_idx)

            if t_key not in st.session_state: st.session_state[t_key] = libro_e["titulo"]
            if a_key not in st.session_state: st.session_state[a_key] = libro_e.get("autora","")
            if p_key not in st.session_state: st.session_state[p_key] = libro_e.get("portada_url","")
            if g_key not in st.session_state: st.session_state[g_key] = libro_e.get("genero","Sin género")

            c1, c2 = st.columns(2)
            with c1:
                ed_titulo  = st.text_input("Título",        key=t_key)
                ed_autora  = st.text_input("Autora/Autor",  key=a_key)
                ed_portada = st.text_input("URL portada",   key=p_key)
            with c2:
                ed_genero = st.selectbox("Género", GENEROS,
                    index=GENEROS.index(st.session_state[g_key]) if st.session_state[g_key] in GENEROS else 0,
                    key=g_key)
            cc1, cc2 = st.columns([3,1])
            with cc1:
                if st.button("💾 Guardar cambios", key="gedit_save", type="primary"):
                    data["libros"][edit_idx]["titulo"]      = ed_titulo.strip() or libro_e["titulo"]
                    data["libros"][edit_idx]["autora"]      = ed_autora.strip()
                    data["libros"][edit_idx]["genero"]      = ed_genero
                    data["libros"][edit_idx]["portada_url"] = ed_portada.strip()
                    save_data(data)
                    for k in [t_key, a_key, p_key, g_key]:
                        if k in st.session_state: del st.session_state[k]
                    st.success("¡Libro actualizado! 🐸"); st.rerun()
            with cc2:
                st.write("")
                if st.button("🗑️ Eliminar", key="gedit_del"):
                    data["libros"].pop(edit_idx); save_data(data); st.rerun()



# ╔══════════════════════╗
# ║   TAB: LECTURAS      ║
# ╚══════════════════════╝
with tab_lecturas:
    libros = data.get("libros", [])

    # Filtro por género (compartido entre sub-tabs)
    generos_usados2 = list(set(l.get("genero","Sin género") for l in libros)) if libros else []
    generos_usados2 = [g for g in GENEROS if g in generos_usados2]
    filtro_genero2 = "Todos"
    if generos_usados2:
        filtro_genero2 = st.selectbox("Filtrar por género", ["Todos"] + generos_usados2, key="filtro_genero2")

    def filtrar2(lista):
        if filtro_genero2 == "Todos": return lista
        return [(i, l) for i, l in lista if l.get("genero","Sin género") == filtro_genero2]

    if not libros:
        st.markdown("<div style='text-align:center;padding:2rem;color:#6abf8a;font-weight:600'><div style='font-size:40px'>📚</div><p>¡Aún no hay libros! Agrégalos en Biblioteca 🐸</p></div>", unsafe_allow_html=True)
    else:
        def libros_para_subtab(estado_filtro):
            if estado_filtro == "pendiente":
                resultado = []
                for i, l in enumerate(libros):
                    em = l.get("estados_miembro", {})
                    if any(em.get(n, "pendiente") in ("pendiente","sin_estado","leyendo") for n in nombres_jugadoras):
                        resultado.append((i, l))
                return resultado
            return [(i,l) for i,l in enumerate(libros) if any(l.get("estados_miembro",{}).get(n)==estado_filtro for n in nombres_jugadoras)]

        sub_leyendo   = filtrar2(libros_para_subtab("leyendo"))
        sub_leido     = filtrar2(libros_para_subtab("leido"))
        sub_pendiente = filtrar2(libros_para_subtab("pendiente"))

        stab1, stab2, stab3 = st.tabs([
            "📖 Leyendo (" + str(len(sub_leyendo)) + ")",
            "✅ Leídos (" + str(len(sub_leido)) + ")",
            "🕐 Pendientes (" + str(len(sub_pendiente)) + ")",
        ])

        def render_lista_libros(lista_libros, subtab_key):
            if not lista_libros:
                st.markdown("<div style='text-align:center;padding:1.5rem;color:#a8d8bf;font-weight:600'>No hay libros aquí todavía 🐸</div>", unsafe_allow_html=True)
                return
            for idx, libro in lista_libros:
                render_libro_card(libro, idx, nombres_jugadoras)

                with st.expander("⭐ Valoración · " + libro["titulo"]):
                    quien_key = subtab_key + "_quien_" + str(idx)
                    nombre_sel = st.selectbox("¿Quién valora?", options=nombres_jugadoras, key=quien_key)

                    estm_key = subtab_key+"_estm_"+str(idx)+"_"+nombre_sel
                    val_key  = subtab_key+"_val_"+str(idx)+"_"+nombre_sel
                    com_key  = subtab_key+"_com_"+str(idx)+"_"+nombre_sel
                    fim_key  = subtab_key+"_fim_"+str(idx)+"_"+nombre_sel
                    ffm_key  = subtab_key+"_ffm_"+str(idx)+"_"+nombre_sel

                    fechas_m = libro.get("fechas_miembro", {}).get(nombre_sel, {})

                    if estm_key not in st.session_state:
                        st.session_state[estm_key] = libro.get("estados_miembro",{}).get(nombre_sel,"pendiente")
                    if val_key not in st.session_state:
                        st.session_state[val_key] = libro.get("valoraciones",{}).get(nombre_sel,0) or 0
                    if com_key not in st.session_state:
                        st.session_state[com_key] = libro.get("comentarios",{}).get(nombre_sel,"")

                    c1, c2 = st.columns(2)
                    with c1:
                        ed_estado_m = st.selectbox("Estado", options=["pendiente","leyendo","leido"],
                            format_func=lambda x: {"pendiente":"🕐 Pendiente","leyendo":"📖 Leyendo","leido":"✅ Leído"}[x],
                            key=estm_key)
                    with c2:
                        ed_val_m = st.slider("Valoración ⭐", min_value=0, max_value=5, key=val_key)

                    c1, c2 = st.columns(2)
                    with c1:
                        fim_val = None
                        try:
                            if fechas_m.get("inicio"): fim_val = datetime.strptime(fechas_m["inicio"],"%Y-%m-%d").date()
                        except: pass
                        ed_fim = st.date_input("Fecha inicio 📅", value=fim_val, key=fim_key)
                    with c2:
                        ffm_val = None
                        try:
                            if fechas_m.get("fin"): ffm_val = datetime.strptime(fechas_m["fin"],"%Y-%m-%d").date()
                        except: pass
                        ed_ffm = st.date_input("Fecha fin 📅", value=ffm_val, key=ffm_key)

                    if ed_fim and ed_ffm and ed_ffm >= ed_fim:
                        dias_m = (ed_ffm - ed_fim).days
                        st.markdown(
                            "<div style='background:#e8f8f0;border-radius:10px;padding:6px 12px;"
                            "font-size:13px;color:#2d7a4f;font-weight:700;margin-bottom:4px'>"
                            "⏱️ " + str(dias_m) + " días leyendo</div>",
                            unsafe_allow_html=True
                        )

                    ed_com_m = st.text_area("Comentario 💬", placeholder="¿Qué piensa " + nombre_sel + " del libro?", key=com_key, height=80)

                    if st.button("💾 Guardar para " + nombre_sel, key=subtab_key+"_save_"+str(idx), type="primary", use_container_width=True):
                        for field in ["estados_miembro","valoraciones","comentarios","fechas_miembro"]:
                            if field not in data["libros"][idx]: data["libros"][idx][field] = {}
                        data["libros"][idx]["estados_miembro"][nombre_sel] = ed_estado_m
                        data["libros"][idx]["valoraciones"][nombre_sel]    = ed_val_m
                        data["libros"][idx]["comentarios"][nombre_sel]     = ed_com_m.strip()
                        data["libros"][idx]["fechas_miembro"][nombre_sel]  = {
                            "inicio": str(ed_fim) if ed_fim else "",
                            "fin":    str(ed_ffm) if ed_ffm else ""
                        }
                        save_data(data)
                        for k in [estm_key, val_key, com_key, quien_key, fim_key, ffm_key]:
                            if k in st.session_state: del st.session_state[k]
                        st.success("¡Guardado para " + nombre_sel + "! 🐸"); st.rerun()

        with stab1: render_lista_libros(sub_leyendo, "ley")
        with stab2: render_lista_libros(sub_leido, "lei")
        with stab3: render_lista_libros(sub_pendiente, "pen")


# ╔══════════════════════╗
# ║    TAB: VOTACIÓN     ║
# ╚══════════════════════╝
with tab_votacion:
    st.markdown("### 🗳️ Votación — próximo libro")

    votacion = data.get("votacion", {"propuestas": [], "activa": False})
    propuestas = votacion.get("propuestas", [])
    activa = votacion.get("activa", False)

    # Estado de la votación
    if activa:
        st.markdown(
            "<div style='background:#d4edf7;border:2px solid #5bc0e8;border-radius:14px;"
            "padding:10px 16px;margin-bottom:12px;font-size:13px;color:#1a6a8a;font-weight:700'>"
            "🗳️ Votación en curso — ¡todas pueden votar!</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background:#f5f5f5;border:2px solid #ddd;border-radius:14px;"
            "padding:10px 16px;margin-bottom:12px;font-size:13px;color:#999;font-weight:700'>"
            "⏸️ Votación no iniciada — agrega propuestas y actívala cuando estén listas</div>",
            unsafe_allow_html=True
        )

    # Proponer libro
    with st.expander("➕ Proponer un libro"):
        c1, c2 = st.columns(2)
        with c1:
            prop_titulo  = st.text_input("Título *", key="prop_titulo")
            prop_autora  = st.text_input("Autora/Autor", key="prop_autora")
        with c2:
            prop_quien   = st.selectbox("Propuesto por", nombres_jugadoras, key="prop_quien")
            prop_genero  = st.selectbox("Género", GENEROS, key="prop_genero")
        if st.button("📚 Agregar propuesta", type="primary", use_container_width=True, key="btn_prop"):
            if prop_titulo.strip():
                # Evitar duplicados
                titulos_prop = [p["titulo"].lower() for p in propuestas]
                if prop_titulo.strip().lower() in titulos_prop:
                    st.warning("Ese libro ya está propuesto 🐸")
                else:
                    propuestas.append({
                        "titulo":  prop_titulo.strip(),
                        "autora":  prop_autora.strip(),
                        "genero":  prop_genero,
                        "quien":   prop_quien,
                        "votos":   {}
                    })
                    data["votacion"]["propuestas"] = propuestas
                    save_data(data)
                    for k in ["prop_titulo","prop_autora"]:
                        if k in st.session_state: del st.session_state[k]
                    st.success("¡Propuesta agregada! 🐸"); st.rerun()
            else:
                st.warning("El título no puede estar vacío 🐸")

    # Controles de votación
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        lbl = "⏸️ Pausar votación" if activa else "▶️ Iniciar votación"
        if st.button(lbl, key="toggle_votacion", use_container_width=True):
            data["votacion"]["activa"] = not activa
            save_data(data); st.rerun()
    with cc2:
        if st.button("🔄 Reiniciar votos", key="reset_votos", use_container_width=True):
            for p in propuestas:
                p["votos"] = {}
            data["votacion"]["propuestas"] = propuestas
            save_data(data); st.rerun()
    with cc3:
        if st.button("🗑️ Borrar propuestas", key="clear_props", use_container_width=True):
            data["votacion"] = {"propuestas": [], "activa": False}
            save_data(data); st.rerun()

    st.divider()

    if not propuestas:
        st.markdown(
            "<div style='text-align:center;padding:2rem;color:#a8d8bf;font-weight:600'>"
            "<div style='font-size:36px'>🗳️</div>"
            "<p>Aún no hay propuestas. ¡Agrega la primera! 🐸</p></div>",
            unsafe_allow_html=True
        )
    else:
        # Calcular ganadora provisional
        max_votos = max((len(p["votos"]) for p in propuestas), default=0)

        # Ordenar por votos desc
        propuestas_ord = sorted(enumerate(propuestas), key=lambda x: -len(x[1]["votos"]))

        for orig_idx, prop in propuestas_ord:
            n_votos = len(prop["votos"])
            es_ganadora = n_votos == max_votos and max_votos > 0
            bg     = "#d4f0e4" if es_ganadora else "white"
            border = "#3dba75" if es_ganadora else "#c5ebd8"
            bw     = "2.5px"   if es_ganadora else "1.5px"
            corona = "👑 " if es_ganadora else ""

            # Barra de votos
            total_miembros = len(nombres_jugadoras)
            pct_v = int(n_votos / total_miembros * 100) if total_miembros > 0 else 0
            votantes_str = ", ".join(prop["votos"].keys()) if prop["votos"] else "Nadie aún"

            st.markdown(
                "<div style='background:" + bg + ";border:" + bw + " solid " + border + ";"
                "border-radius:18px;padding:14px 16px;margin-bottom:10px'>"
                "<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px'>"
                "<div><div style='font-weight:800;color:#2d7a4f;font-size:16px'>" + corona + prop["titulo"] + "</div>"
                + ("<div style='font-size:12px;color:#888;margin-top:1px'>✍️ " + prop["autora"] + "</div>" if prop.get("autora") else "")
                + "<div style='font-size:11px;color:#aaa;margin-top:2px'>Propuesto por " + prop["quien"] + "</div></div>"
                "<div style='text-align:right'>"
                "<div style='font-size:22px;font-weight:800;color:#2d7a4f'>" + str(n_votos) + "</div>"
                "<div style='font-size:11px;color:#888'>votos</div></div></div>"
                "<div style='background:#e8f8f0;border-radius:20px;height:8px;margin-bottom:6px'>"
                "<div style='background:#3dba75;height:100%;width:" + str(pct_v) + "%;border-radius:20px'></div></div>"
                "<div style='font-size:11px;color:#888'>🗳️ " + votantes_str + "</div>"
                "</div>",
                unsafe_allow_html=True
            )

            # Botones de votar / quitar voto / eliminar
            bc1, bc2, bc3 = st.columns([2, 2, 1])
            with bc1:
                if activa:
                    votante = st.selectbox("¿Quién vota?", nombres_jugadoras, key="vot_quien_" + str(orig_idx))
                    ya_voto = votante in prop["votos"]
                    lbl_voto = "✅ Quitar voto" if ya_voto else "🗳️ Votar"
                    tipo_voto = "secondary" if ya_voto else "primary"
                    if st.button(lbl_voto, key="vot_btn_" + str(orig_idx), type=tipo_voto, use_container_width=True):
                        if ya_voto:
                            del data["votacion"]["propuestas"][orig_idx]["votos"][votante]
                        else:
                            data["votacion"]["propuestas"][orig_idx]["votos"][votante] = True
                        save_data(data); st.rerun()
            with bc3:
                if st.button("🗑️", key="del_prop_" + str(orig_idx)):
                    data["votacion"]["propuestas"].pop(orig_idx)
                    save_data(data); st.rerun()

        # Botón para elegir ganadora como libro actual
        if max_votos > 0:
            st.divider()
            ganadora = max(propuestas, key=lambda x: len(x["votos"]))
            lbl_gan = "📖 Poner '" + ganadora["titulo"] + "' como libro actual"
            if st.button(lbl_gan, type="primary", use_container_width=True, key="set_ganadora"):
                data["libro_actual"] = ganadora["titulo"]
                save_data(data)
                st.success("¡'" + ganadora["titulo"] + "' es el próximo libro! 🐸"); st.rerun()


# ╔══════════════════════╗
# ║    TAB: AGENDA       ║
# ╚══════════════════════╝
with tab_agenda:
    st.markdown("### 📅 Próximas reuniones")

    agenda = data.get("agenda", [])
    # Mostrar reuniones futuras primero
    hoy = date.today().isoformat()
    futuras = [(i,r) for i,r in enumerate(agenda) if r.get("fecha","") >= hoy]
    pasadas = [(i,r) for i,r in enumerate(agenda) if r.get("fecha","") < hoy]

    if futuras:
        for i, reunion in futuras:
            dias_para = (datetime.strptime(reunion["fecha"],"%Y-%m-%d").date() - date.today()).days
            if dias_para == 0: cuando = "¡Hoy! 🎉"
            elif dias_para == 1: cuando = "¡Mañana! ✨"
            else: cuando = "En " + str(dias_para) + " días"
            st.markdown(
                "<div style='background:#d4edf7;border:2px solid #5bc0e8;border-radius:16px;padding:14px 16px;margin-bottom:8px'>"
                "<div style='display:flex;justify-content:space-between;align-items:flex-start'>"
                "<div><div style='font-weight:800;color:#1a6a8a;font-size:15px'>📅 " + reunion.get("titulo","Reunión") + "</div>"
                "<div style='font-size:13px;color:#1a6a8a;margin-top:2px'>" + reunion["fecha"] + "  ·  " + reunion.get("hora","") + "</div>"
                + ("<div style='font-size:13px;color:#555;margin-top:4px'>📖 " + reunion.get("capitulos","") + "</div>" if reunion.get("capitulos") else "")
                + ("<div style='font-size:13px;color:#555;margin-top:2px'>📝 " + reunion.get("notas","") + "</div>" if reunion.get("notas") else "")
                + "</div>"
                "<div style='text-align:right;font-size:12px;color:#1a6a8a;font-weight:700'>" + cuando + "</div></div></div>",
                unsafe_allow_html=True
            )
            if st.button("🗑️ Eliminar reunión", key="del_reunion_" + str(i)):
                data["agenda"].pop(i); save_data(data); st.rerun()
    else:
        st.markdown("<div style='text-align:center;padding:1rem;color:#a8d8bf;font-weight:600'>No hay reuniones próximas agendadas 🐸</div>", unsafe_allow_html=True)

    with st.expander("➕ Agendar reunión"):
        c1, c2 = st.columns(2)
        with c1:
            ag_titulo = st.text_input("Título", placeholder="Ej: Sesión #5", key="ag_titulo")
            ag_fecha  = st.date_input("Fecha", key="ag_fecha")
        with c2:
            ag_hora   = st.text_input("Hora", placeholder="Ej: 19:00", key="ag_hora")
            ag_caps   = st.text_input("Capítulos a cubrir", placeholder="Ej: Cap 10-15", key="ag_caps")
        ag_notas = st.text_area("Notas", placeholder="Lugar, link, etc.", key="ag_notas", height=70)
        if st.button("📅 Agregar reunión", type="primary", use_container_width=True):
            data["agenda"].append({
                "titulo": ag_titulo.strip() or "Reunión",
                "fecha": str(ag_fecha), "hora": ag_hora.strip(),
                "capitulos": ag_caps.strip(), "notas": ag_notas.strip()
            })
            data["agenda"].sort(key=lambda x: x.get("fecha",""))
            save_data(data); st.success("¡Reunión agendada! 📅"); st.rerun()

    if pasadas:
        with st.expander("🕐 Reuniones pasadas (" + str(len(pasadas)) + ")"):
            for i, reunion in pasadas:
                st.markdown(
                    "<div style='background:#f5f5f5;border:1px solid #ddd;border-radius:12px;padding:10px 14px;margin-bottom:6px;opacity:0.7'>"
                    "<div style='font-weight:700;color:#888;font-size:14px'>📅 " + reunion.get("titulo","Reunión") + "  ·  " + reunion["fecha"] + "</div>"
                    + ("<div style='font-size:12px;color:#aaa'>📖 " + reunion.get("capitulos","") + "</div>" if reunion.get("capitulos") else "")
                    + "</div>", unsafe_allow_html=True
                )


# ╔══════════════════════════╗
# ║  TAB: ESTADÍSTICAS       ║
# ╚══════════════════════════╝
with tab_stats:
    st.markdown("### 📊 Estadísticas del club")

    libros = data.get("libros", [])
    total_libros = len(libros)
    leidos_todos = [l for l in libros if all(l.get("estados_miembro",{}).get(n)=="leido" for n in nombres_jugadoras)]
    n_leidos_todos = len(leidos_todos)

    # Contadores
    c1, c2, c3 = st.columns(3)
    for col, label, n, color, tc in [
        (c1, "Total libros 📚", total_libros, "#d4edf7", "#1a6a8a"),
        (c2, "Leídos por todas ✅", n_leidos_todos, "#d4f0e4", "#2d7a4f"),
        (c3, "Reuniones 📅", len(data.get("agenda",[])), "#fce8f3", "#a0417a"),
    ]:
        with col:
            st.markdown(
                "<div style='text-align:center;background:" + color + ";border-radius:16px;padding:12px 8px'>"
                "<div style='font-size:26px;font-weight:800;color:" + tc + "'>" + str(n) + "</div>"
                "<div style='font-size:11px;color:" + tc + ";font-weight:700'>" + label + "</div></div>",
                unsafe_allow_html=True
            )

    st.divider()

    # Géneros más leídos
    if libros:
        st.markdown("**📖 Libros por género**")
        genero_count = {}
        for l in leidos_todos:
            g = l.get("genero","Sin género")
            genero_count[g] = genero_count.get(g, 0) + 1
        if genero_count:
            max_g = max(genero_count.values())
            for g, cnt in sorted(genero_count.items(), key=lambda x: -x[1]):
                pct_g = int(cnt / max_g * 100)
                st.markdown(
                    "<div style='margin-bottom:6px'>"
                    "<div style='display:flex;justify-content:space-between;font-size:13px;font-weight:600;color:#2d7a4f;margin-bottom:2px'>"
                    "<span>" + g + "</span><span>" + str(cnt) + "</span></div>"
                    "<div style='background:#e8f8f0;border-radius:20px;height:10px'>"
                    "<div style='background:#3dba75;height:100%;width:" + str(pct_g) + "%;border-radius:20px'></div></div></div>",
                    unsafe_allow_html=True
                )
        else:
            st.caption("Aún no hay libros leídos por todas 🐸")

        st.divider()

        # Promedio de valoración por libro (leídos)
        st.markdown("**⭐ Valoraciones promedio**")
        libros_con_val = [(l["titulo"], promedio_vals(l)) for l in leidos_todos if promedio_vals(l) > 0]
        libros_con_val.sort(key=lambda x: -x[1])
        if libros_con_val:
            for titulo, prom in libros_con_val:
                st.markdown(
                    "<div style='display:flex;justify-content:space-between;align-items:center;"
                    "background:white;border:1px solid #d4f0e4;border-radius:12px;padding:8px 14px;margin-bottom:6px'>"
                    "<span style='font-weight:700;color:#2d7a4f;font-size:13px'>" + titulo + "</span>"
                    "<span style='font-size:15px'>" + estrellas(prom) + " <b style='color:#2d7a4f;font-size:12px'>" + str(prom) + "</b></span></div>",
                    unsafe_allow_html=True
                )
        else:
            st.caption("Aún no hay valoraciones registradas 🐸")

        st.divider()

        # Tiempo por miembro por libro
        st.markdown("**⏱️ Tiempo por miembro**")

        # Construir tabla: {nombre: [(titulo, dias), ...]}
        tiempos_miembro = {n: [] for n in nombres_jugadoras}
        for l in libros:
            fechas_m = l.get("fechas_miembro", {})
            for n in nombres_jugadoras:
                fm = fechas_m.get(n, {})
                fi_s = fm.get("inicio", ""); ff_s = fm.get("fin", "")
                if fi_s and ff_s:
                    try:
                        d1 = datetime.strptime(fi_s, "%Y-%m-%d")
                        d2 = datetime.strptime(ff_s, "%Y-%m-%d")
                        if d2 >= d1:
                            tiempos_miembro[n].append((l["titulo"], (d2 - d1).days))
                    except: pass

        hay_datos = any(len(v) > 0 for v in tiempos_miembro.values())
        if hay_datos:
            member_colors = ["#d4f0e4", "#d4edf7", "#fce8f3", "#faeeda", "#eeedfe"]
            member_text   = ["#2d7a4f", "#1a6a8a", "#a0417a", "#854F0B", "#3C3489"]
            for i, nombre in enumerate(nombres_jugadoras):
                registros = tiempos_miembro[nombre]
                if not registros:
                    continue
                bg = member_colors[i % len(member_colors)]
                tc = member_text[i % len(member_text)]
                prom_n = round(sum(d for _, d in registros) / len(registros))
                mas_rapido = min(registros, key=lambda x: x[1])
                mas_lento  = max(registros, key=lambda x: x[1])

                # Header siempre visible (fuera del expander)
                st.markdown(
                    "<div style='background:" + bg + ";border:1.5px solid " + tc + ";"
                    "border-radius:14px 14px 0 0;padding:10px 16px;margin-bottom:0px'>"
                    "<div style='display:flex;justify-content:space-between;align-items:center'>"
                    "<span style='font-weight:800;color:" + tc + ";font-size:14px'>" + nombre + "</span>"
                    "<span style='font-weight:700;color:" + tc + ";font-size:13px'>Promedio: " + str(prom_n) + " días</span>"
                    "</div></div>",
                    unsafe_allow_html=True
                )
                # Detalle colapsable
                with st.expander("Ver detalle", expanded=False):
                    inner_html = ""
                    for titulo, dias in sorted(registros, key=lambda x: x[1]):
                        inner_html += (
                            "<div style='display:flex;justify-content:space-between;"
                            "background:" + bg + ";border-radius:8px;padding:5px 10px;margin-bottom:4px;font-size:12px'>"
                            "<span style='color:#444;font-weight:600'>" + titulo + "</span>"
                            "<span style='font-weight:700;color:" + tc + "'>⏱️ " + str(dias) + " días</span></div>"
                        )
                    if len(registros) > 1:
                        inner_html += (
                            "<div style='display:flex;gap:12px;margin-top:6px;font-size:11px;color:" + tc + "'>"
                            "<span>🐇 Más rápida: <b>" + mas_rapido[0] + "</b> (" + str(mas_rapido[1]) + " días)</span>"
                            "<span>🐢 Más lenta: <b>" + mas_lento[0] + "</b> (" + str(mas_lento[1]) + " días)</span>"
                            "</div>"
                        )
                    st.markdown(inner_html, unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
        else:
            st.caption("Aún no hay fechas registradas para calcular tiempos 🐸")

        st.divider()

        # Actividad y reglas por miembro
        st.markdown("**👤 Actividad por miembro**")

        # Parsear historial para contar reglas por miembro
        reglas_por_miembro = {n: {} for n in nombres_jugadoras}
        for entrada in data.get("historial", []):
            # formato: "HH:MM — Nombre: "Regla" → +X pts"
            for nombre in nombres_jugadoras:
                if (" — " + nombre + ": \"") in entrada or (" — " + nombre + ": '") in entrada:
                    try:
                        # extraer la regla entre comillas
                        if '"' in entrada:
                            partes = entrada.split('"')
                            regla = partes[1] if len(partes) > 1 else ""
                        else:
                            regla = ""
                        # extraer puntos
                        pts_part = entrada.split("→")[-1].strip().split(" ")[0] if "→" in entrada else "0"
                        pts_val = int(pts_part.replace("+","")) if pts_part not in ["", "manual)", "manual"] else 0
                        if regla:
                            if regla not in reglas_por_miembro[nombre]:
                                reglas_por_miembro[nombre][regla] = {"count": 0, "pts_total": 0}
                            reglas_por_miembro[nombre][regla]["count"] += 1
                            reglas_por_miembro[nombre][regla]["pts_total"] += pts_val
                    except: pass

        for nombre in nombres_jugadoras:
            leidos_n  = sum(1 for l in libros if l.get("estados_miembro",{}).get(nombre)=="leido")
            leyendo_n = sum(1 for l in libros if l.get("estados_miembro",{}).get(nombre)=="leyendo")
            pts_n = next((j["puntos"] for j in data["jugadoras"] if j["nombre"]==nombre), 0)
            reglas_n = reglas_por_miembro.get(nombre, {})

            with st.expander(nombre + "  ·  " + ("+" if pts_n > 0 else "") + str(pts_n) + " pts"):
                # Resumen rápido
                st.markdown(
                    "<div style='display:flex;gap:14px;font-size:13px;color:#555;margin-bottom:10px'>"
                    "<span>✅ <b>" + str(leidos_n) + "</b> leídos</span>"
                    "<span>📖 <b>" + str(leyendo_n) + "</b> leyendo</span>"
                    "<span>🏆 <b>" + ("+" if pts_n > 0 else "") + str(pts_n) + "</b> pts</span>"
                    "<span>📋 <b>" + str(sum(v["count"] for v in reglas_n.values())) + "</b> acciones</span>"
                    "</div>",
                    unsafe_allow_html=True
                )
                if reglas_n:
                    # Separar positivas y negativas
                    pos = {r: v for r, v in reglas_n.items() if v["pts_total"] >= 0}
                    neg = {r: v for r, v in reglas_n.items() if v["pts_total"] < 0}
                    if pos:
                        st.markdown("<div style='font-size:12px;font-weight:700;color:#2d7a4f;margin-bottom:4px'>✅ Positivas</div>", unsafe_allow_html=True)
                        for regla, vals in sorted(pos.items(), key=lambda x: -x[1]["count"]):
                            pts_t = ("+" if vals["pts_total"] > 0 else "") + str(vals["pts_total"])
                            st.markdown(
                                "<div style='display:flex;justify-content:space-between;background:#d4f0e4;"
                                "border-radius:10px;padding:6px 12px;margin-bottom:4px;font-size:12px'>"
                                "<span style='color:#2d7a4f;font-weight:600'>" + regla + "</span>"
                                "<span style='color:#2d7a4f;font-weight:700'>x" + str(vals["count"]) + "  " + pts_t + " pts</span></div>",
                                unsafe_allow_html=True
                            )
                    if neg:
                        st.markdown("<div style='font-size:12px;font-weight:700;color:#c0392b;margin:8px 0 4px'>❌ Negativas</div>", unsafe_allow_html=True)
                        for regla, vals in sorted(neg.items(), key=lambda x: x[1]["pts_total"]):
                            pts_t = str(vals["pts_total"])
                            st.markdown(
                                "<div style='display:flex;justify-content:space-between;background:#fce8f3;"
                                "border-radius:10px;padding:6px 12px;margin-bottom:4px;font-size:12px'>"
                                "<span style='color:#a0417a;font-weight:600'>" + regla + "</span>"
                                "<span style='color:#a0417a;font-weight:700'>x" + str(vals["count"]) + "  " + pts_t + " pts</span></div>",
                                unsafe_allow_html=True
                            )
                else:
                    st.caption("Sin acciones registradas aún 🐸")

st.markdown(
    "<div style='text-align:center;padding:1.5rem 0 1rem;color:#a8d8bf;font-size:13px;font-weight:600'>"
    "🐸 Sapi Club · hecho con poco amor para las sapas mar-acass 🐸</div>",
    unsafe_allow_html=True
)
