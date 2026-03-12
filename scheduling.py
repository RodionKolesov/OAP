import numpy as np
from itertools import permutations


def build_completion_matrix(matrix: np.ndarray, job_order: list[int]) -> np.ndarray:
    """Build completion time matrix C[i][j] for given job order on flow shop.
    matrix: shape (n_jobs, n_machines) — processing times
    job_order: list of job indices in processing order
    Returns: completion time matrix of shape (len(job_order), n_machines)
    """
    n = len(job_order)
    m = matrix.shape[1]
    C = np.zeros((n, m))

    for i in range(n):
        for j in range(m):
            job = job_order[i]
            top = C[i - 1][j] if i > 0 else 0
            left = C[i][j - 1] if j > 0 else 0
            C[i][j] = max(top, left) + matrix[job][j]

    return C


def calculate_makespan(matrix: np.ndarray, job_order: list[int]) -> float:
    """Calculate total production cycle length (makespan) for given job order."""
    C = build_completion_matrix(matrix, job_order)
    return C[-1][-1]


def calculate_metrics(matrix: np.ndarray, job_order: list[int]) -> dict:
    """Calculate scheduling metrics: makespan, utilization, idle time."""
    C = build_completion_matrix(matrix, job_order)
    makespan = C[-1][-1]
    n = len(job_order)
    m = matrix.shape[1]

    total_processing = sum(matrix[job].sum() for job in job_order)
    total_available = makespan * m
    total_idle = total_available - total_processing
    utilization = (total_processing / total_available * 100) if total_available > 0 else 0

    return {
        "makespan": makespan,
        "utilization": round(utilization, 2),
        "idle_time": total_idle,
    }


# === Optimization Methods ===

def method_bottleneck_distance(matrix: np.ndarray) -> list[int]:
    """Метод 1: Удалённость узкого места.
    Sort jobs by bottleneck position (machine index with max time) descending.
    Jobs with bottleneck closer to end go first.
    """
    n, m = matrix.shape
    bottleneck_positions = []
    for i in range(n):
        max_machine = int(np.argmax(matrix[i]))
        bottleneck_positions.append((i, max_machine))

    # Sort: jobs with bottleneck on later machines first
    bottleneck_positions.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in bottleneck_positions]


def method_greedy_limited_search(matrix: np.ndarray) -> list[int]:
    """Метод 2: Ограниченный перебор (жадный выбор).
    At each step, pick the job that minimizes partial makespan.
    """
    n = matrix.shape[0]
    remaining = list(range(n))
    order = []

    for _ in range(n):
        best_job = None
        best_makespan = float("inf")
        for job in remaining:
            candidate = order + [job]
            ms = calculate_makespan(matrix, candidate)
            if ms < best_makespan:
                best_makespan = ms
                best_job = job
        order.append(best_job)
        remaining.remove(best_job)

    return order


def method_max_last_machine(matrix: np.ndarray) -> list[int]:
    """Метод 3: Максимальное время на последнем станке.
    Sort by processing time on last machine, descending.
    """
    n, m = matrix.shape
    last_times = [(i, matrix[i, m - 1]) for i in range(n)]
    last_times.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in last_times]


def method_max_total_time(matrix: np.ndarray) -> list[int]:
    """Метод 4: Максимальное суммарное время.
    Sort by total processing time across all machines, descending.
    """
    n = matrix.shape[0]
    totals = [(i, matrix[i].sum()) for i in range(n)]
    totals.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in totals]


def method_min_first_machine(matrix: np.ndarray) -> list[int]:
    """Метод 5: Минимальное время на 1-м станке.
    Sort by processing time on first machine, ascending.
    """
    n = matrix.shape[0]
    first_times = [(i, matrix[i, 0]) for i in range(n)]
    first_times.sort(key=lambda x: x[1])
    return [x[0] for x in first_times]


def method_petrov_sokolitsyn(matrix: np.ndarray) -> list[int]:
    """Метод 6: Метод Петрова-Соколицына.
    For each job compute:
      first_sum = sum of times on all machines except first
      second_sum = sum of times on all machines except last
      diff = first_sum - second_sum
    Generate 3 candidate sequences:
      1) Sort by diff descending
      2) Sort by first_sum descending
      3) Sort by second_sum ascending
    Return the one with minimum makespan.
    """
    n, m = matrix.shape
    jobs_data = []
    for i in range(n):
        first_sum = matrix[i, 1:].sum()   # all except first machine
        second_sum = matrix[i, :-1].sum()  # all except last machine
        diff = first_sum - second_sum
        jobs_data.append((i, first_sum, second_sum, diff))

    # 3 candidate orderings
    seq1 = [x[0] for x in sorted(jobs_data, key=lambda x: x[3], reverse=True)]
    seq2 = [x[0] for x in sorted(jobs_data, key=lambda x: x[1], reverse=True)]
    seq3 = [x[0] for x in sorted(jobs_data, key=lambda x: x[2])]

    candidates = [seq1, seq2, seq3]
    best = min(candidates, key=lambda s: calculate_makespan(matrix, s))
    return best


METHODS = {
    "Удалённость узкого места": method_bottleneck_distance,
    "Ограниченный перебор (жадный)": method_greedy_limited_search,
    "Макс. время на последнем станке": method_max_last_machine,
    "Макс. суммарное время": method_max_total_time,
    "Мин. время на 1-м станке": method_min_first_machine,
    "Метод Петрова-Соколицына": method_petrov_sokolitsyn,
}
