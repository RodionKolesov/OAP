# streamlit — фреймворк для создания интерактивных веб-приложений на Python
import streamlit as st
# pandas — библиотека для работы с табличными данными (DataFrame)
import pandas as pd
# numpy — библиотека для работы с многомерными массивами и математическими операциями
import numpy as np
# scheduling — модуль проекта: расчёт метрик расписания и методы оптимизации порядка деталей
from scheduling import calculate_metrics, METHODS
# gantt — модуль проекта: построение диаграммы Ганта с помощью Plotly
from gantt import create_gantt_chart

st.set_page_config(
    page_title="Оперативно-календарное планирование",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom Dark Theme CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Hide default Streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* Global */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    font-family: 'Inter', sans-serif;
}

/* Hero header */
.hero {
    text-align: center;
    padding: 2rem 0 1rem;
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
    letter-spacing: -0.5px;
}
.hero p {
    color: #8b8fa3;
    font-size: 1.05rem;
    font-weight: 400;
}

/* Glass card */
.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Metric card */
.metric-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
}
.metric-label {
    color: #8b8fa3;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #e0e0ff;
}
.metric-delta {
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 0.2rem;
}
.delta-good { color: #00e676; }
.delta-bad { color: #ff5252; }
.delta-neutral { color: #8b8fa3; }

/* Section title */
.section-title {
    color: #c5c8e8;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title .icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}
.icon-purple { background: rgba(118, 75, 162, 0.3); }
.icon-blue { background: rgba(102, 126, 234, 0.3); }
.icon-green { background: rgba(0, 230, 118, 0.3); }

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #8b8fa3;
    font-weight: 600;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: rgba(102, 126, 234, 0.2) !important;
    color: #e0e0ff !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: transparent !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e0e0ff !important;
}

/* Slider */
.stSlider > div > div > div {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
}
.stSlider label, .stSlider [data-testid="stWidgetLabel"] p {
    color: #e0e0ff !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(102, 126, 234, 0.35) !important;
}

/* Dataframe */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* File uploader */
.stFileUploader > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px dashed rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
}
.stFileUploader label, .stFileUploader [data-testid="stWidgetLabel"] p {
    color: #e0e0ff !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] {
    background: rgba(15, 12, 41, 0.8) !important;
    border: 1px dashed rgba(102, 126, 234, 0.4) !important;
    border-radius: 12px !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] * {
    color: #c5c8e8 !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] button {
    background: rgba(102, 126, 234, 0.2) !important;
    border: 1px solid rgba(102, 126, 234, 0.4) !important;
    color: #e0e0ff !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] svg {
    fill: #667eea !important;
}

/* Radio */
.stRadio > div {
    gap: 0.3rem;
}
.stRadio > div {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1rem 1.2rem;
}
.stRadio label, .stRadio p, .stRadio span {
    color: #e0e0ff !important;
    font-weight: 500 !important;
}
.stRadio [data-testid="stWidgetLabel"] p {
    color: #e0e0ff !important;
    font-size: 0.95rem !important;
}
.stRadio [role="radiogroup"] label {
    padding: 0.35rem 0.6rem !important;
    border-radius: 8px !important;
    transition: background 0.15s !important;
}
.stRadio [role="radiogroup"] label:hover {
    background: rgba(102, 126, 234, 0.1) !important;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    margin: 1.5rem 0;
}

/* Order badge */
.order-badge {
    display: inline-block;
    background: rgba(102, 126, 234, 0.15);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 20px;
    padding: 0.4rem 1rem;
    color: #b0b8f0;
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
}

/* Comparison header */
.compare-header {
    text-align: center;
    padding: 0.6rem;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
}
.compare-before {
    background: rgba(255, 82, 82, 0.12);
    color: #ff8a80;
    border: 1px solid rgba(255, 82, 82, 0.2);
}
.compare-after {
    background: rgba(0, 230, 118, 0.12);
    color: #69f0ae;
    border: 1px solid rgba(0, 230, 118, 0.2);
}

/* Expander text color */
.streamlit-expanderHeader p, .streamlit-expanderHeader span,
[data-testid="stExpander"] summary span {
    color: #e0e0ff !important;
}
</style>
""", unsafe_allow_html=True)


# === HERO ===
st.markdown("""
<div class="hero">
    <h1>Оперативно-календарное планирование</h1>
    <p></p>
</div>
""", unsafe_allow_html=True)

# === DATA INPUT SECTION ===
st.markdown('<div class="section-title"><span class="icon icon-purple">1</span> Входные данные</div>', unsafe_allow_html=True)

matrix = None
job_names = None

col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 1])
with col_a:
    n_jobs = st.slider("Детали (n)", 3, 100, 5)
with col_b:
    n_machines = st.slider("Станки (m)", 3, 100, 4)
with col_c:
    max_duration = st.slider("Макс. длительность", 1, 50, 10)
with col_d:
    st.write("")
    st.write("")
    if st.button("Сгенерировать данные", use_container_width=True):
        matrix = np.random.randint(1, max_duration + 1, size=(n_jobs, n_machines)).astype(float)
        st.session_state["matrix"] = matrix
        st.session_state["job_names"] = [f"Деталь {i + 1}" for i in range(n_jobs)]

if "matrix" in st.session_state and matrix is None:
    matrix = st.session_state["matrix"]
    job_names = st.session_state.get("job_names")

uploaded = st.file_uploader("Или загрузите Excel-файл", type=["xls", "xlsx"])
if uploaded is not None:
    try:
        df = pd.read_excel(uploaded, index_col=0)
        matrix = df.values.astype(float)
        job_names = [str(x) for x in df.index]
        st.session_state["matrix"] = matrix
        st.session_state["job_names"] = job_names
    except Exception as e:
        st.error(f"Ошибка чтения файла: {e}")

if matrix is None:
    st.stop()

n_jobs, n_machines = matrix.shape
if job_names is None:
    job_names = [f"Деталь {i + 1}" for i in range(n_jobs)]

machine_cols = [f"Станок {j + 1}" for j in range(n_machines)]

# === OPERATIONS TABLE ===
with st.expander("Таблица операций"):
    df_display = pd.DataFrame(matrix.astype(int), index=job_names, columns=machine_cols)
    st.dataframe(df_display, use_container_width=True, height=min(400, n_jobs * 40 + 50))

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# === OPTIMIZATION ===
st.markdown('<div class="section-title"><span class="icon icon-blue">2</span> Метод оптимизации</div>', unsafe_allow_html=True)

initial_order = list(range(n_jobs))
initial_metrics = calculate_metrics(matrix, initial_order)

method_names = list(METHODS.keys())
method_name = st.radio("Метод", method_names, label_visibility="collapsed")

method_fn = METHODS[method_name]
optimized_order = method_fn(matrix)
optimized_metrics = calculate_metrics(matrix, optimized_order)

makespan_delta = optimized_metrics["makespan"] - initial_metrics["makespan"]
makespan_pct = (makespan_delta / initial_metrics["makespan"] * 100) if initial_metrics["makespan"] != 0 else 0
idle_delta = optimized_metrics["idle_time"] - initial_metrics["idle_time"]
util_delta = optimized_metrics["utilization"] - initial_metrics["utilization"]

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# === METRICS ===
st.markdown('<div class="section-title"><span class="icon icon-green">3</span> Результаты</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

delta_class_ms = "delta-good" if makespan_pct <= 0 else "delta-bad"
delta_class_idle = "delta-good" if idle_delta <= 0 else "delta-bad"
delta_class_util = "delta-good" if util_delta >= 0 else "delta-bad"

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Время выполнения</div>
        <div class="metric-value">{optimized_metrics['makespan']:.0f}</div>
        <div class="metric-delta {delta_class_ms}">{makespan_pct:+.1f}% от исходного</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Загрузка оборудования</div>
        <div class="metric-value">{optimized_metrics['utilization']:.1f}%</div>
        <div class="metric-delta {delta_class_util}">{util_delta:+.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Суммарный простой</div>
        <div class="metric-value">{optimized_metrics['idle_time']:.0f}</div>
        <div class="metric-delta {delta_class_idle}">{idle_delta:+.0f} от исходного</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# === GANTT COMPARISON ===
col_before, col_after = st.columns(2)

with col_before:
    st.markdown('<div class="compare-header compare-before">До оптимизации</div>', unsafe_allow_html=True)
    fig_before = create_gantt_chart(matrix, initial_order, "", job_names)
    st.plotly_chart(fig_before, use_container_width=True, key="gantt_before")

with col_after:
    st.markdown('<div class="compare-header compare-after">После оптимизации</div>', unsafe_allow_html=True)
    fig_after = create_gantt_chart(matrix, optimized_order, "", job_names)
    st.plotly_chart(fig_after, use_container_width=True, key="gantt_after")

# === ORDER ===
order_str = " → ".join(job_names[i] for i in optimized_order)
st.markdown(f'<div class="order-badge">Порядок: {order_str}</div>', unsafe_allow_html=True)

# === FINAL TABLE ===
with st.expander("Таблица после оптимизации"):
    reordered_names = [job_names[i] for i in optimized_order]
    df_optimized = pd.DataFrame(matrix[optimized_order].astype(int), index=reordered_names, columns=machine_cols)
    st.dataframe(df_optimized, use_container_width=True, height=min(400, n_jobs * 40 + 50))

# Bottom padding so expander text isn't clipped
st.markdown('<div style="height: 8rem;"></div>', unsafe_allow_html=True)
