import streamlit as st
import pandas as pd
import numpy as np
from scheduling import calculate_metrics, METHODS
from gantt import create_gantt_chart

st.set_page_config(page_title="ОКП — Оперативно-календарное планирование", layout="wide")
st.title("📊 Оперативно-календарное планирование (ОКП)")

# --- Sidebar ---
st.sidebar.header("Параметры")
data_source = st.sidebar.radio("Источник данных", ["Загрузить Excel файл", "Сгенерировать случайные данные"])

matrix = None
job_names = None

if data_source == "Загрузить Excel файл":
    uploaded = st.sidebar.file_uploader("Загрузите файл Excel", type=["xls", "xlsx"])
    if uploaded is not None:
        try:
            df = pd.read_excel(uploaded, index_col=0)
            matrix = df.values.astype(float)
            job_names = [str(x) for x in df.index]
        except Exception as e:
            st.sidebar.error(f"Ошибка чтения файла: {e}")

else:
    n_jobs = st.sidebar.slider("Количество деталей (n)", 3, 100, 5)
    n_machines = st.sidebar.slider("Количество станков (m)", 3, 100, 4)
    max_duration = st.sidebar.slider("Макс. длительность операции", 1, 50, 10)

    if st.sidebar.button("Сгенерировать"):
        matrix = np.random.randint(1, max_duration + 1, size=(n_jobs, n_machines)).astype(float)
        st.session_state["matrix"] = matrix
        st.session_state["job_names"] = [f"Деталь {i + 1}" for i in range(n_jobs)]

    if "matrix" in st.session_state and matrix is None:
        matrix = st.session_state["matrix"]
        job_names = st.session_state.get("job_names")

if matrix is None:
    st.info("Загрузите файл Excel или сгенерируйте случайные данные в боковой панели.")
    st.stop()

n_jobs, n_machines = matrix.shape
if job_names is None:
    job_names = [f"Деталь {i + 1}" for i in range(n_jobs)]

machine_cols = [f"Станок {j + 1}" for j in range(n_machines)]

# --- Operations Table ---
with st.expander("📋 Таблица операций", expanded=False):
    df_display = pd.DataFrame(matrix, index=job_names, columns=machine_cols)
    st.dataframe(df_display, use_container_width=True)

# --- Initial Schedule ---
initial_order = list(range(n_jobs))
initial_metrics = calculate_metrics(matrix, initial_order)

with st.expander("📉 Диаграмма Ганта до оптимизации", expanded=True):
    st.metric("Исходное время выполнения", f"{initial_metrics['makespan']:.0f}")
    fig_initial = create_gantt_chart(matrix, initial_order, "До оптимизации", job_names)
    st.plotly_chart(fig_initial, use_container_width=True)

# --- Optimization ---
st.header("🔧 Оптимизация расписания")

method_name = st.selectbox("Выберите метод оптимизации", list(METHODS.keys()))

method_fn = METHODS[method_name]
optimized_order = method_fn(matrix)
optimized_metrics = calculate_metrics(matrix, optimized_order)

# Deltas
makespan_delta = optimized_metrics["makespan"] - initial_metrics["makespan"]
makespan_pct = (makespan_delta / initial_metrics["makespan"] * 100) if initial_metrics["makespan"] != 0 else 0
idle_delta = optimized_metrics["idle_time"] - initial_metrics["idle_time"]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Время выполнения",
        f"{optimized_metrics['makespan']:.0f}",
        delta=f"{makespan_pct:+.1f}%",
        delta_color="inverse",
    )
with col2:
    st.metric(
        "Загрузка оборудования",
        f"{optimized_metrics['utilization']:.1f}%",
    )
with col3:
    st.metric(
        "Суммарный простой",
        f"{optimized_metrics['idle_time']:.0f}",
        delta=f"{idle_delta:+.0f}",
        delta_color="inverse",
    )

fig_opt = create_gantt_chart(matrix, optimized_order, f"После оптимизации — {method_name}", job_names)
st.plotly_chart(fig_opt, use_container_width=True)

with st.expander("📋 Конечная таблица операций (порядок после оптимизации)", expanded=False):
    reordered_names = [job_names[i] for i in optimized_order]
    df_optimized = pd.DataFrame(matrix[optimized_order], index=reordered_names, columns=machine_cols)
    st.dataframe(df_optimized, use_container_width=True)

st.caption(f"Порядок деталей: {' → '.join(job_names[i] for i in optimized_order)}")
