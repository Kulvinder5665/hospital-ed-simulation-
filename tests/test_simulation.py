from src.simulation import run_simulation, generate_patients, BASE_DOCTORS, BACKUP_DOCTORS


def test_deterministic_arrivals():
    assert generate_patients(seed=5) == generate_patients(seed=5)


def test_patient_conservation():
    for policy in ("baseline", "orb", "improved"):
        records, _, summary = run_simulation(policy, n=100, seed=3, mean_interarrival=1)
        assert len(records) == 100
        assert records.patient_id.nunique() == 100
        assert all(records.sojourn_time >= records.service_time - 1e-8)
        assert summary["mean_queue_wait"] >= 0


def test_doctor_limits():
    for policy in ("baseline", "orb", "improved"):
        _, timeline, _ = run_simulation(policy, n=100, seed=2, mean_interarrival=1)
        for grade, rows in timeline.groupby("grade"):
            assert rows.active_doctors.min() >= BASE_DOCTORS[grade]
            assert rows.active_doctors.max() <= BASE_DOCTORS[grade] + BACKUP_DOCTORS[grade]


def test_baseline_has_no_activations():
    _, _, summary = run_simulation("baseline", seed=4)
    assert summary["activations"] == 0
