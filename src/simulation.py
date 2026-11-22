"""Simplified, token/resource-oriented stochastic ED simulator.

This is a reproducible approximation of the study, NOT a faithful recreation
of its complete stochastic timed Petri-net graph.
"""
from dataclasses import dataclass
import random
import simpy
import pandas as pd

GRADES = ("I", "II", "III", "IV")
PROBABILITIES = (0.10, 0.15, 0.30, 0.45)
BASE_DOCTORS = {"I": 4, "II": 3, "III": 2, "IV": 2}
BACKUP_DOCTORS = {"I": 3, "II": 2, "III": 1, "IV": 1}
# Operational targets are configurable assumptions, not clinical guidance.
TARGET_MINUTES = {"I": 2.0, "II": 10.0, "III": 30.0, "IV": 90.0}


@dataclass(frozen=True)
class Patient:
    patient_id: int
    grade: str
    arrival: float
    registration: float
    triage: float
    treatment: float


def generate_patients(n=100, mean_interarrival=5.0, seed=42):
    if n <= 0 or mean_interarrival <= 0:
        raise ValueError("Patient count and mean interarrival must be positive")
    rng = random.Random(seed)
    patients, t = [], 0.0
    for i in range(n):
        t += rng.expovariate(1.0 / mean_interarrival)
        grade = rng.choices(GRADES, weights=PROBABILITIES, k=1)[0]
        patients.append(Patient(i + 1, grade, t, rng.uniform(2, 4),
                                rng.expovariate(1 / 5), rng.expovariate(1 / 10)))
    return patients


class GradeStation:
    def __init__(self, env, grade):
        self.env = env
        self.grade = grade
        self.idle = simpy.Store(env)
        self.base = BASE_DOCTORS[grade]
        self.max_backup = BACKUP_DOCTORS[grade]
        self.active_backup = 0
        self.waiting = {}  # patient id -> first time entering waiting place
        self.samples = []
        self.activation_events = 0
        for idx in range(self.base):
            self.idle.put(("base", idx))

    def activate(self):
        if self.active_backup >= self.max_backup:
            return False
        self.active_backup += 1
        self.activation_events += 1
        self.idle.put(("backup", self.active_backup))
        return True

    def release_idle_backup(self):
        # Only remove an available (idle) backup token, never a busy physician.
        for token in list(self.idle.items):
            if token[0] == "backup":
                self.idle.items.remove(token)
                self.active_backup -= 1
                return True
        return False

    def oldest_wait(self):
        return max((self.env.now - t for t in self.waiting.values()), default=0.0)


def run_simulation(policy="baseline", n=100, mean_interarrival=5.0, seed=42,
                   queue_threshold=5, improved_trigger=0.8):
    if policy not in {"baseline", "orb", "improved"}:
        raise ValueError("policy must be baseline, orb, or improved")
    patients = generate_patients(n, mean_interarrival, seed)
    env = simpy.Environment()
    stations = {g: GradeStation(env, g) for g in GRADES}
    completed = []
    history = []

    def serve(patient):
        yield env.timeout(patient.arrival - env.now)
        # Simplified: registration/triage consume time but do not compete for staff.
        yield env.timeout(patient.registration + patient.triage)
        station = stations[patient.grade]
        queued_at = env.now
        station.waiting[patient.patient_id] = queued_at
        token = yield station.idle.get()  # consumes an available doctor token
        station.waiting.pop(patient.patient_id)
        treatment_start = env.now
        yield env.timeout(patient.treatment)
        yield station.idle.put(token)      # returns the resource token
        completed.append({"patient_id": patient.patient_id,
                          "grade": patient.grade, "arrival": patient.arrival,
                          "treatment_queue_wait": treatment_start - queued_at,
                          "pre_treatment_time": treatment_start - patient.arrival,
                          "service_time": patient.registration + patient.triage + patient.treatment,
                          "sojourn_time": env.now - patient.arrival,
                          "departure": env.now})

    def control_loop():
        while len(completed) < n:
            for grade, station in stations.items():
                q = len(station.waiting)
                if policy == "orb" and q > queue_threshold:
                    station.activate()
                elif policy == "improved" and q:
                    capacity = station.base + station.active_backup
                    # Queue workload (min) + oldest queued wait, normalized to grade target.
                    pressure = (q * 10.0 / capacity + station.oldest_wait()) / TARGET_MINUTES[grade]
                    if pressure >= improved_trigger:
                        station.activate()
                # Simple release rule with no churn: release only on empty queues.
                if q == 0 and policy != "baseline":
                    station.release_idle_backup()
                history.append({"minute": env.now, "grade": grade,
                                "queue": q, "active_doctors": station.base + station.active_backup,
                                "policy": policy})
            yield env.timeout(1)

    for patient in patients:
        env.process(serve(patient))
    env.process(control_loop())
    # Run until the last patient has completed, even under heavy congestion.
    def done():
        while len(completed) < n:
            yield env.timeout(1)
    env.run(until=env.process(done()))
    records = pd.DataFrame(completed).sort_values("patient_id").reset_index(drop=True)
    timeline = pd.DataFrame(history)
    summary = {"policy": policy, "seed": seed, "patients": n,
               "mean_queue_wait": records.treatment_queue_wait.mean(),
               "p95_queue_wait": records.treatment_queue_wait.quantile(0.95),
               "mean_sojourn": records.sojourn_time.mean(),
               "max_queue": timeline.groupby("minute")["queue"].sum().max(),
               "activations": sum(s.activation_events for s in stations.values()),
               "deadline_violations": sum(
                   records.apply(lambda r: r.treatment_queue_wait > TARGET_MINUTES[r.grade], axis=1)),
               "last_departure": records.departure.max()}
    return records, timeline, summary
