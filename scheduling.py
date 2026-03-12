import numpy as np


def build_completion_matrix(matrix: np.ndarray, job_order: list[int]) -> np.ndarray:
    """Build completion time matrix C[i][j] for given job order on flow shop."""
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


def method_johnson_n(matrix: np.ndarray) -> list[int]:
    """Алгоритм Джонсона для N станков.
    Поиск минимума только на 1-м и последнем станке.
    Если минимум на 1-м — деталь в начало, на последнем — в конец.
    """
    n, m = matrix.shape
    col_first = matrix[:, 0].copy()
    col_last = matrix[:, m - 1].copy()

    remaining = set(range(n))
    result = [None] * n
    left = 0
    right = n - 1

    while remaining:
        best_val = float("inf")
        best_job = -1
        best_is_first = True

        for job in remaining:
            if col_first[job] < best_val:
                best_val = col_first[job]
                best_job = job
                best_is_first = True
            if col_last[job] < best_val:
                best_val = col_last[job]
                best_job = job
                best_is_first = False
            if col_first[job] == best_val and col_first[job] <= col_last[job]:
                best_job = job
                best_is_first = True

        if best_is_first:
            result[left] = best_job
            left += 1
        else:
            result[right] = best_job
            right -= 1

        remaining.remove(best_job)

    return result


def method_generalization_1(matrix: np.ndarray) -> list[int]:
    """Первое обобщение Джонсона.
    Сначала запускают детали с минимальным временем на 1-м станке
    в порядке возрастания этого времени.
    """
    n = matrix.shape[0]
    jobs = [(i, matrix[i, 0]) for i in range(n)]
    jobs.sort(key=lambda x: x[1])
    return [x[0] for x in jobs]


def method_generalization_2(matrix: np.ndarray) -> list[int]:
    """Второе обобщение Джонсона.
    Сначала запускают детали с максимальным временем на последнем станке
    в порядке убывания этого времени.
    """
    n, m = matrix.shape
    jobs = [(i, matrix[i, m - 1]) for i in range(n)]
    jobs.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in jobs]


def method_generalization_3(matrix: np.ndarray) -> list[int]:
    """Третье обобщение Джонсона.
    Сначала запускают детали, у которых «узкое место» (станок с макс. временем)
    находится дальше от начала процесса обработки.
    """
    n = matrix.shape[0]
    jobs = [(i, int(np.argmax(matrix[i]))) for i in range(n)]
    jobs.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in jobs]


def method_generalization_4(matrix: np.ndarray) -> list[int]:
    """Четвёртое обобщение Джонсона.
    Сначала обрабатывают детали с максимальным суммарным временем
    на всех станках, в порядке убывания.
    """
    n = matrix.shape[0]
    jobs = [(i, matrix[i].sum()) for i in range(n)]
    jobs.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in jobs]


def method_petrov_sokolitsyn(matrix: np.ndarray) -> list[int]:
    """Метод Петрова-Соколицына.
    1) Первая сумма = сумма на всех станках кроме 1-го
    2) Вторая сумма = сумма на всех станках кроме последнего
    3) Разность = первая - вторая
    4) Убывание первой суммы
    5) Возрастание второй суммы
    6) Убывание разности
    7) Выбрать лучшую из трёх
    """
    n, m = matrix.shape
    jobs_data = []
    for i in range(n):
        first_sum = matrix[i, 1:].sum()
        second_sum = matrix[i, :-1].sum()
        diff = first_sum - second_sum
        jobs_data.append((i, first_sum, second_sum, diff))

    seq1 = [x[0] for x in sorted(jobs_data, key=lambda x: x[1], reverse=True)]
    seq2 = [x[0] for x in sorted(jobs_data, key=lambda x: x[2])]
    seq3 = [x[0] for x in sorted(jobs_data, key=lambda x: x[3], reverse=True)]

    candidates = [seq1, seq2, seq3]
    best = min(candidates, key=lambda s: calculate_makespan(matrix, s))
    return best


METHODS = {
    "Алгоритм Джонсона для N станков": method_johnson_n,
    "Первое обобщение Джонсона": method_generalization_1,
    "Второе обобщение Джонсона": method_generalization_2,
    "Третье обобщение Джонсона": method_generalization_3,
    "Четвёртое обобщение Джонсона": method_generalization_4,
    "Метод Петрова-Соколицына": method_petrov_sokolitsyn,
}
