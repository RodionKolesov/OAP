# numpy — библиотека для работы с многомерными массивами; используется для операций над матрицей времён
import numpy as np
# plotly.graph_objects — модуль библиотеки Plotly для построения интерактивных графиков;
# класс Figure — контейнер графика, класс Bar — горизонтальные столбцы для диаграммы Ганта
import plotly.graph_objects as go
# build_completion_matrix — функция из модуля scheduling, вычисляющая матрицу времён завершения
# операций на каждом станке для заданного порядка деталей
from scheduling import build_completion_matrix


# Неоновая цветовая палитра для тёмной темы — каждый цвет соответствует отдельной детали на диаграмме
COLORS = [
    "#667eea", "#764ba2", "#00e676", "#ff5252", "#ffab40",
    "#18ffff", "#e040fb", "#b2ff59", "#ff80ab", "#ffd740",
    "#448aff", "#ff6e40", "#69f0ae", "#7c4dff", "#eeff41",
    "#40c4ff", "#ff4081", "#b9f6ca", "#ea80fc", "#ffe57f",
]


def create_gantt_chart(
    matrix: np.ndarray,
    job_order: list[int],
    title: str = "",
    job_names: list[str] | None = None,
) -> go.Figure:
    C = build_completion_matrix(matrix, job_order)
    n = len(job_order)
    m = matrix.shape[1]

    if job_names is None:
        job_names = [f"Деталь {job_order[i] + 1}" for i in range(n)]
    else:
        job_names = [job_names[job_order[i]] for i in range(n)]

    fig = go.Figure()

    for i in range(n):
        job_idx = job_order[i]
        color = COLORS[job_idx % len(COLORS)]
        show_legend = True
        for j in range(m):
            end = C[i][j]
            start = end - matrix[job_idx][j]
            duration = matrix[job_idx][j]
            if duration == 0:
                continue
            fig.add_trace(go.Bar(
                y=[f"M{j + 1}"],
                x=[duration],
                base=[start],
                orientation="h",
                marker=dict(
                    color=color,
                    line=dict(width=0),
                    opacity=0.85,
                ),
                name=job_names[i],
                legendgroup=job_names[i],
                showlegend=show_legend,
                hovertemplate=(
                    f"<b>{job_names[i]}</b><br>"
                    f"Станок {j+1}<br>"
                    f"{start:.0f} → {end:.0f} ({duration:.0f})"
                    f"<extra></extra>"
                ),
            ))
            show_legend = False

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#c5c8e8")),
        xaxis=dict(
            title="",
            color="#8b8fa3",
            gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
        ),
        yaxis=dict(
            title="",
            color="#c5c8e8",
            autorange="reversed",
            gridcolor="rgba(255,255,255,0.04)",
        ),
        barmode="stack",
        height=max(250, m * 45 + 80),
        margin=dict(l=30, r=20, t=40, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        legend=dict(
            font=dict(color="#c5c8e8", size=11),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
        ),
        font=dict(family="Inter, sans-serif"),
    )

    return fig
