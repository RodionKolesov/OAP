import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from scheduling import build_completion_matrix


# Distinct color palette for jobs
COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
    "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
    "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF",
]


def create_gantt_chart(matrix: np.ndarray, job_order: list[int], title: str = "Диаграмма Ганта", job_names: list[str] | None = None) -> go.Figure:
    """Create a Plotly Gantt chart for flow shop schedule.
    Y-axis: machines, X-axis: time units, color-coded by job.
    """
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
                y=[f"Станок {j + 1}"],
                x=[duration],
                base=[start],
                orientation="h",
                marker=dict(color=color),
                name=job_names[i],
                legendgroup=job_names[i],
                showlegend=show_legend,
                hovertemplate=f"{job_names[i]}<br>Станок {j+1}<br>Начало: {start:.0f}<br>Конец: {end:.0f}<br>Длительность: {duration:.0f}<extra></extra>",
            ))
            show_legend = False

    fig.update_layout(
        title=title,
        xaxis_title="Время",
        yaxis_title="",
        barmode="stack",
        height=max(300, m * 50 + 100),
        legend_title="Детали",
        yaxis=dict(autorange="reversed"),
    )

    return fig
