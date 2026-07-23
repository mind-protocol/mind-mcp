from datetime import datetime, timedelta

import pytest

from runtime.cognition.temporal_desire import (
    TemporalBias,
    TemporalExpectation,
    apply_progress,
    calculate_pressure,
    integrate_previous_interval,
    plan_next_alarm,
    resolve_modifiers,
    summarize_wake_load,
)


NOW = datetime(2026, 7, 23, 12, 0, 0)


def expectation(**overrides):
    values = {
        "wish_id": "wish:bond",
        "realization_id": "objective:contact",
        "wish_weight": 1.0,
        "commitment": 1.0,
        "progress": 0.0,
        "patience_tau_seconds": 100.0,
        "base_threshold": 0.5,
        "effective_threshold": 0.5,
        "last_integrated_at": NOW,
        "held_clock_rate": 1.0,
    }
    values.update(overrides)
    return TemporalExpectation(**values)


def test_elapsed_time_uses_the_previously_held_clock_rate():
    state = expectation(held_clock_rate=2.0)

    integrated = integrate_previous_interval(state, NOW + timedelta(seconds=10))
    modifiers = resolve_modifiers(
        integrated,
        affects={"anxiety": 1.0},
        affect_biases={"anxiety": TemporalBias(clock_bias=1.0)},
        affect_status="observed",
    )

    assert integrated.subjective_age_seconds == 20.0
    assert modifiers.clock_rate == pytest.approx(2.718281828, rel=1e-6)


def test_unknown_affect_is_numerically_neutral_but_not_called_neutral():
    modifiers = resolve_modifiers(expectation(), affect_status="not_measured")

    assert modifiers.affect_factor == 1.0
    assert modifiers.clock_rate == 1.0
    assert modifiers.affect_status == "not_measured"


def test_explicit_anxiety_policy_advances_the_next_alarm():
    state = expectation()
    neutral = resolve_modifiers(state, affect_status="observed")
    anxious = resolve_modifiers(
        state,
        affects={"anxiety": 0.8},
        affect_biases={
            "anxiety": TemporalBias(clock_bias=0.9, threshold_bias=-0.15)
        },
        affect_status="observed",
    )

    neutral_plan = plan_next_alarm(state, neutral, NOW)
    anxious_plan = plan_next_alarm(state, anxious, NOW)

    assert anxious.clock_rate > neutral.clock_rate
    assert anxious.effective_threshold < neutral.effective_threshold
    assert anxious_plan.scheduled_for < neutral_plan.scheduled_for


def test_partial_progress_reduces_amplitude_and_subjective_age():
    state = expectation(subjective_age_seconds=80.0)
    before = calculate_pressure(state)

    progressed = apply_progress(state, delta=0.25, relief=0.30)

    assert progressed.progress == 0.25
    assert progressed.subjective_age_seconds == 56.0
    assert progressed.generation == state.generation + 1
    assert calculate_pressure(progressed) < before


def test_unreachable_threshold_creates_no_alarm():
    state = expectation(wish_weight=0.4, commitment=0.5, base_threshold=0.65)
    modifiers = resolve_modifiers(state)

    plan = plan_next_alarm(state, modifiers, NOW)

    assert plan.action == "none"
    assert plan.reason == "unreachable_threshold"


def test_hysteresis_prevents_retrigger_while_pressure_stays_high():
    state = expectation(
        subjective_age_seconds=200.0,
        alarm_armed=False,
        release_threshold=0.4,
    )
    modifiers = resolve_modifiers(state)

    plan = plan_next_alarm(state, modifiers, NOW)

    assert calculate_pressure(state) > state.release_threshold
    assert plan.action == "none"
    assert plan.reason == "hysteresis"


def test_wake_load_expands_recurrences_without_claiming_task_workload():
    wakes = [
        {
            "scheduledFor": (NOW + timedelta(minutes=30)).isoformat(),
            "repeat": "hourly",
        },
        {
            "scheduledFor": (NOW + timedelta(hours=8)).isoformat(),
            "repeat": "once",
        },
    ]

    load = summarize_wake_load(wakes, now=NOW)

    assert load["scheduledAlarmCount"] == 2
    assert load["nextHour"] == 1
    assert load["next24Hours"] == 25
    assert load["next7Days"] == 169
    assert load["level"] == "saturated"
    assert load["meaning"] == "scheduled_activation_density_not_task_workload"
