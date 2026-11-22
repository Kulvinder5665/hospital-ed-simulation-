from src.simulation import run_simulation, generate_patients, BASE_DOCTORS, BACKUP_DOCTORS


def test_deterministic_arrivals():
    # The same seed should reproduce every pre-sampled patient field.
    assert generate_patients(seed=5) == generate_patients(seed=5)


def test_patient_conservation():
    # Use a short arrival interval to exercise all policies under heavier demand.
    for policy in ("baseline", "orb", "improved"):
        records, _, summary = run_simulation(policy, n=100, seed=3, mean_interarrival=1)
        # Every simulated patient should complete exactly once.
        assert len(records) == 100
        assert records.patient_id.nunique() == 100
        # Total time includes service and waiting. Allow for floating-point rounding.
        assert all(records.sojourn_time >= records.service_time - 1e-8)
        assert summary["mean_queue_wait"] >= 0


def test_doctor_limits():
    for policy in ("baseline", "orb", "improved"):
        _, timeline, _ = run_simulation(policy, n=100, seed=2, mean_interarrival=1)
        # Check the sampled staffing against each grade's floor and ceiling.
        for grade, rows in timeline.groupby("grade"):
            assert rows.active_doctors.min() >= BASE_DOCTORS[grade]
            assert rows.active_doctors.max() <= BASE_DOCTORS[grade] + BACKUP_DOCTORS[grade]


def test_baseline_has_no_activations():
    # Baseline should use only the permanent treatment doctors.
    _, _, summary = run_simulation("baseline", seed=4)
    assert summary["activations"] == 0
