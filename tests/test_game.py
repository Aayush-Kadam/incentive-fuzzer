from dataclasses import replace
from decimal import Decimal

import pytest

from incentive_fuzzer.core import load_spec
from incentive_fuzzer.game import (
    DynamicsStatus, EquilibriumStatus, JointAction, UpdateMode, best_response,
    enumerate_basins, enumerate_pure_nash, evaluate_game, externality, game_hash,
    isolated_gain, joint_profiles, payoff_matrix, replay_equilibrium,
    run_best_response_dynamics, verify_pure_nash,
)
from incentive_fuzzer.game_fixtures import (
    aggregate_threshold_claim, anti_coordination, coordination_game, matching_pennies,
    matrix_game, prisoners_dilemma, safe_interaction_control, scarcity_capture,
)


H, M = "HONEST", "MANIPULATE"


@pytest.mark.parametrize("profile,expected,designer", [
    ((H, H), ("10", "10"), ("0", "0")),
    ((H, M), ("10", "8"), ("0", "1")),
    ((M, H), ("8", "10"), ("0", "1")),
    ((M, M), ("12", "12"), ("8", "2")),
])
def test_precommitted_matrix_exact(profile, expected, designer):
    game = aggregate_threshold_claim()
    result = evaluate_game(game, JointAction({"A": profile[0], "B": profile[1]}))
    assert (result.player_payoffs["A"], result.player_payoffs["B"]) == tuple(map(Decimal, expected))
    assert (result.designer_outcomes["payout_total"], result.designer_outcomes["manipulation_count"]) == tuple(map(Decimal, designer))


@pytest.mark.parametrize("player,opponent,expected", [
    ("A", H, (H,)), ("A", M, (M,)), ("B", H, (H,)), ("B", M, (M,)),
])
def test_precommitted_best_responses(player, opponent, expected):
    other = "B" if player == "A" else "A"
    assert best_response(aggregate_threshold_claim(), player, {other: opponent}).actions == expected


def test_precommitted_equilibrium_set_exact():
    result = enumerate_pure_nash(aggregate_threshold_claim())
    profiles = {tuple(eq.joint_action.actions[p] for p in ("A", "B")) for eq in result.equilibria}
    assert profiles == {(H, H), (M, M)}
    assert result.profiles_evaluated == 4


def test_non_equilibrium_has_explainable_witness():
    result = verify_pure_nash(aggregate_threshold_claim(), JointAction({"A": H, "B": M}))
    assert result.status is EquilibriumStatus.NOT_EQUILIBRIUM
    assert (result.deviation.player_id, result.deviation.from_action, result.deviation.to_action) == ("A", H, M)
    assert (result.deviation.from_payoff, result.deviation.to_payoff) == (Decimal("10"), Decimal("12"))


def test_all_precommitted_equilibria_replay():
    game = aggregate_threshold_claim()
    assert all(replay_equilibrium(game, equilibrium) for equilibrium in enumerate_pure_nash(game).equilibria)


def test_isolated_analysis_differs_from_interactive_best_response():
    game = aggregate_threshold_claim()
    assert isolated_gain(game, "A", M) == Decimal("-2")
    assert best_response(game, "A", {"B": M}).actions == (M,)


def test_strategic_complementarity_delta():
    game = aggregate_threshold_claim()
    delta_zero = isolated_gain(game, "A", M)
    versus_m = evaluate_game(game, JointAction({"A": M, "B": M})).player_payoffs["A"] - evaluate_game(game, JointAction({"A": H, "B": M})).player_payoffs["A"]
    assert (delta_zero, versus_m, versus_m - delta_zero) == (Decimal("-2"), Decimal("2"), Decimal("4"))


def test_ties_return_full_correspondence():
    tied = matrix_game("tied", {(H, H): ("1", "1"), (H, M): ("1", "1"),
                                  (M, H): ("1", "1"), (M, M): ("1", "1")})
    assert best_response(tied, "A", {"B": H}).actions == (H, M)
    assert len(enumerate_pure_nash(tied).equilibria) == 4


@pytest.mark.parametrize("fixture,expected", [
    (prisoners_dilemma, {(M, M)}),
    (coordination_game, {(H, H), (M, M)}),
    (matching_pennies, set()),
    (anti_coordination, {(H, M), (M, H)}),
])
def test_textbook_equilibria(fixture, expected):
    result = enumerate_pure_nash(fixture())
    actual = {tuple(eq.joint_action.actions[p] for p in ("A", "B")) for eq in result.equilibria}
    assert actual == expected


def test_scarcity_capture_is_strategic_substitution():
    game = scarcity_capture()
    assert best_response(game, "A", {"B": H}).actions == (M,)
    assert best_response(game, "A", {"B": M}).actions == (H,)
    assert {tuple(eq.joint_action.actions[p] for p in ("A", "B")) for eq in enumerate_pure_nash(game).equilibria} == {(M, H), (H, M)}


def test_externality_decomposition():
    effect = externality(scarcity_capture(), "A", H, M, {"B": H})
    assert effect == {"A": Decimal("5"), "B": Decimal("0")}


def test_safe_control_has_only_honest_equilibrium():
    result = enumerate_pure_nash(safe_interaction_control())
    assert [tuple(eq.joint_action.actions[p] for p in ("A", "B")) for eq in result.equilibria] == [(H, H)]


def test_synchronous_dynamics_detects_cycle():
    result = run_best_response_dynamics(anti_coordination(), JointAction({"A": H, "B": H}), UpdateMode.SYNCHRONOUS)
    assert result.status is DynamicsStatus.CYCLE_DETECTED
    assert len(result.cycle) == 3


def test_asynchronous_dynamics_converges_and_verifies():
    result = run_best_response_dynamics(anti_coordination(), JointAction({"A": H, "B": H}), UpdateMode.ASYNCHRONOUS)
    assert result.status is DynamicsStatus.CONVERGED_EQUILIBRIUM
    assert result.equilibrium_verified
    assert verify_pure_nash(anti_coordination(), result.terminal_profile).status is EquilibriumStatus.PURE_NASH


@pytest.mark.parametrize("mode", [UpdateMode.SYNCHRONOUS, UpdateMode.ASYNCHRONOUS])
def test_basin_enumerates_every_initial_profile(mode):
    basin = enumerate_basins(aggregate_threshold_claim(), mode)
    assert basin.total_initial_profiles == 4
    assert sum(basin.equilibrium_counts.values()) + basin.cycles + basin.max_steps == 4


def test_coordination_basin_selection_is_declared_not_equilibrium_discovery():
    basin = enumerate_basins(aggregate_threshold_claim(), UpdateMode.ASYNCHRONOUS)
    assert basin.equilibrium_counts == {"HONEST|HONEST": 2, "MANIPULATE|MANIPULATE": 2}


@pytest.mark.parametrize("bonus,cost,threshold,expected", [
    ("1", "2", 2, {(H, H)}),
    ("4", "2", 2, {(H, H), (M, M)}),
    ("4", "2", 1, {(M, M)}),
])
def test_parameter_phase_changes(bonus, cost, threshold, expected):
    game = aggregate_threshold_claim(Decimal(bonus), Decimal(cost), threshold)
    profiles = {tuple(eq.joint_action.actions[p] for p in ("A", "B")) for eq in enumerate_pure_nash(game).equilibria}
    assert profiles == expected


def test_game_hash_is_stable_and_parameter_sensitive():
    first = aggregate_threshold_claim()
    assert game_hash(first) == game_hash(aggregate_threshold_claim())
    assert len(game_hash(first)) == 64
    assert game_hash(first) != game_hash(aggregate_threshold_claim(bonus=Decimal("5")))


def test_joint_profiles_scale_as_action_product():
    assert len(joint_profiles(aggregate_threshold_claim(n=2))) == 4
    assert len(joint_profiles(aggregate_threshold_claim(n=3))) == 8
    assert len(joint_profiles(aggregate_threshold_claim(n=4))) == 16


def test_invalid_joint_action_rejected():
    with pytest.raises(ValueError, match="every player"):
        evaluate_game(aggregate_threshold_claim(), JointAction({"A": H}))


def test_unknown_action_rejected():
    with pytest.raises(ValueError, match="unknown action"):
        evaluate_game(aggregate_threshold_claim(), JointAction({"A": "OTHER", "B": H}))


def test_payoff_matrix_has_every_profile_once():
    matrix = payoff_matrix(aggregate_threshold_claim())
    assert set(matrix) == {(H, H), (H, M), (M, H), (M, M)}


def test_v01_backward_compatibility():
    spec = load_spec("examples/scholarship_cliff.yaml")
    assert spec.incentive_spec_version == "0.1"
    assert spec.identity_hash
