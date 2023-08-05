from pycsp3 import *

jobs = data.jobs
n, m = len(jobs), len(jobs[0].durations)
horizon = max(job.dueDate for job in jobs) if all(job.dueDate != -1 for job in jobs) else sum(sum(job.durations) for job in jobs)
durations = [job.durations for job in jobs]
indexes = [[job.resources.index(j) for j in range(m)] for job in jobs]

# s[i][j] is the start time of the jth operation for the ith job
s = VarArray(size=[n, m], dom=range(horizon))

# e[i] is the end time of the last operation for the ith job
e = VarArray(size=[n], dom=range(horizon))


def respecting_dates(i):
    if jobs[i].releaseDate > 0:
        return s[i][0] > jobs[i].releaseDate
    if jobs[i].dueDate != -1 and jobs[i].dueDate < horizon - 1:
        return e[i] <= jobs[i].dueDate
    return None


satisfy(
    # operations must be ordered on each job
    [Increasing(s[i], lengths=durations[i]) for i in range(n)],

    # computing the end time of each job
    [e[i] == s[i][- 1] + durations[i][- 1] for i in range(n)],

    # respecting release and due dates
    [respecting_dates(i) for i in range(n)],

    # no overlap on resources
    [NoOverlap(origins=[s[i][indexes[i][j]] for i in range(n)], lengths=[durations[i][indexes[i][j]] for i in range(n)]) for j in range(m)]
)

minimize(
    # minimizing the makespan
    Maximum(e)
)
