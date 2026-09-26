from __future__ import annotations

import csv
from dataclasses import asdict
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from incentive_fuzzer.game import (
    DynamicsStatus, JointAction, UpdateMode, best_response, enumerate_basins,
    enumerate_pure_nash, evaluate_game, game_hash, isolated_gain, joint_profiles,
    payoff_matrix, replay_equilibrium,
)
from incentive_fuzzer.game_fixtures import aggregate_threshold_claim, safe_interaction_control, scarcity_capture


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "m5"
H, M = "HONEST", "MANIPULATE"


def norm(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if hasattr(value, "value"):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return norm(asdict(value))
    if isinstance(value, dict):
        return {str(key): norm(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [norm(item) for item in value]
    return value


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(norm(value), indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows([{key: norm(value) for key, value in row.items()} for row in rows])


def profiles(result):
    return ["|".join(eq.joint_action.actions[p] for p in ("A", "B")) for eq in result.equilibria]


def regime(result) -> str:
    found = set(profiles(result))
    if found == {"HONEST|HONEST"}:
        return "H"
    if found == {"MANIPULATE|MANIPULATE"}:
        return "M"
    if found == {"HONEST|HONEST", "MANIPULATE|MANIPULATE"}:
        return "MULTIPLE"
    if not found:
        return "NONE_PURE"
    return "OTHER"


def main() -> None:
    replay_directory = OUT / "replays"
    replay_directory.mkdir(parents=True, exist_ok=True)
    for replay_file in replay_directory.glob("*.json"):
        replay_file.unlink()
    validation = aggregate_threshold_claim()
    substitution = scarcity_capture()
    safe = safe_interaction_control()
    games = [validation, substitution, safe]
    write_json(OUT / "configs" / "registered_design.json", {
        "precommitment": "research/M5_PRECOMMITMENT.md",
        "manual_derivation": "research/m5_manual_fixture_derivation.md",
        "git_commit": "6004d64", "engine_commit": "72694fc",
        "research_games": [game.id for game in games],
        "timing": "simultaneous", "information": "complete",
        "equilibrium_concept": "PURE_STRATEGY_NASH",
        "method": "EXACT_FINITE_ENUMERATION",
        "dynamics": [mode.value for mode in UpdateMode],
        "phase_grid": {"threshold": [1, 2], "cost": [1, 2, 3, 4], "bonus": list(range(7))},
        "scaling_players": list(range(2, 13)),
    })

    for game in games:
        write_json(OUT / "games" / f"{game.id}.json", {
            "game_id": game.id, "game_hash": game_hash(game), "players": game.players,
            "mechanism": game.mechanism, "parameters": game.parameters,
            "timing": game.timing, "information": game.information,
            "equilibrium_concept": "PURE_STRATEGY_NASH",
        })

    matrix_rows = []
    for profile, result in payoff_matrix(validation).items():
        matrix_rows.append({"A_action": profile[0], "B_action": profile[1],
                            "A_payoff": result.player_payoffs["A"], "B_payoff": result.player_payoffs["B"],
                            "payout_total": result.designer_outcomes["payout_total"],
                            "manipulation_count": result.designer_outcomes["manipulation_count"]})
    write_csv(OUT / "tables" / "payoff_matrix.csv", matrix_rows)

    equilibrium_rows = []
    replay_rows = []
    equilibrium_sets = {}
    for game in games:
        result = enumerate_pure_nash(game)
        equilibrium_sets[game.id] = result
        for equilibrium in result.equilibria:
            action_text = "|".join(equilibrium.joint_action.actions[p.id] for p in game.players)
            replayed = replay_equilibrium(game, equilibrium)
            equilibrium_rows.append({"game": game.id, "game_hash": result.game_hash,
                                     "equilibrium_id": equilibrium.equilibrium_id,
                                     "joint_action": action_text, "player_payoffs": json.dumps(norm(equilibrium.player_payoffs), sort_keys=True),
                                     "designer_outcomes": json.dumps(norm(equilibrium.designer_outcomes), sort_keys=True),
                                     "method": result.method, "replay": replayed})
            replay = {"game_id": game.id, "game_hash": result.game_hash,
                      "equilibrium": equilibrium, "replay_status": "PASS" if replayed else "FAIL"}
            write_json(OUT / "replays" / f"{game.id}-{equilibrium.equilibrium_id}.json", replay)
            replay_rows.append(replay)
    write_csv(OUT / "tables" / "equilibria.csv", equilibrium_rows)

    response_rows = []
    for game in (validation, substitution):
        for player, other in (("A", "B"), ("B", "A")):
            for opponent_action in (H, M):
                response = best_response(game, player, {other: opponent_action})
                response_rows.append({"game": game.id, "player": player,
                                      "opponent_action": opponent_action,
                                      "best_responses": "|".join(response.actions), "payoff": response.payoff})
    write_csv(OUT / "tables" / "best_responses.csv", response_rows)

    dynamics_rows = []
    basin_summaries = {}
    for mode in (UpdateMode.SYNCHRONOUS, UpdateMode.ASYNCHRONOUS):
        basin = enumerate_basins(validation, mode)
        basin_summaries[mode.value] = basin
        for result in basin.results:
            dynamics_rows.append({"mode": mode.value,
                                  "initial": "|".join(result.initial_profile.actions[p] for p in ("A", "B")),
                                  "status": result.status.value,
                                  "terminal": "" if result.terminal_profile is None else "|".join(result.terminal_profile.actions[p] for p in ("A", "B")),
                                  "path": ";".join("|".join(step.actions[p] for p in ("A", "B")) for step in result.path),
                                  "cycle_length": len(result.cycle) - 1 if result.status is DynamicsStatus.CYCLE_DETECTED else 0})
    write_csv(OUT / "tables" / "basins.csv", dynamics_rows)

    phase_rows = []
    for threshold in (1, 2):
        for cost in range(1, 5):
            for bonus in range(0, 7):
                result = enumerate_pure_nash(aggregate_threshold_claim(Decimal(bonus), Decimal(cost), threshold))
                phase_rows.append({"threshold": threshold, "cost": cost, "bonus": bonus,
                                   "regime": regime(result), "equilibrium_count": len(result.equilibria),
                                   "equilibria": ";".join(profiles(result))})
    write_csv(OUT / "tables" / "phase_diagram.csv", phase_rows)

    scaling_rows = []
    for n in range(2, 13):
        game = aggregate_threshold_claim(threshold=n, n=n)
        started = perf_counter()
        result = enumerate_pure_nash(game)
        elapsed = perf_counter() - started
        scaling_rows.append({"players": n, "actions_per_player": 2, "joint_profiles": 2 ** n,
                             "equilibria": len(result.equilibria), "seconds": f"{elapsed:.6f}"})
    write_csv(OUT / "tables" / "scaling.csv", scaling_rows)

    svg_rows = [row for row in phase_rows if row["threshold"] == 2]
    colors = {"H": "#4C78A8", "M": "#E45756", "MULTIPLE": "#F2CF5B", "NONE_PURE": "#999999", "OTHER": "#B279A2"}
    cells = []
    for row in svg_rows:
        x, y = 80 + row["bonus"] * 70, 40 + (4 - row["cost"]) * 55
        cells.append(f'<rect x="{x}" y="{y}" width="68" height="53" fill="{colors[row["regime"]]}"/><text x="{x+34}" y="{y+31}" text-anchor="middle" font-size="11">{row["regime"]}</text>')
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="310"><rect width="100%" height="100%" fill="white"/><text x="300" y="20" text-anchor="middle" font-size="16">Threshold-2 equilibrium correspondence</text>' + ''.join(cells) + '<text x="320" y="300" text-anchor="middle">bonus</text><text x="18" y="150" transform="rotate(-90 18 150)" text-anchor="middle">cost</text></svg>\n'
    figure = OUT / "figures" / "phase_diagram.svg"
    figure.parent.mkdir(parents=True, exist_ok=True)
    figure.write_text(svg, encoding="utf-8")

    validation_eq = equilibrium_sets[validation.id]
    substitution_eq = equilibrium_sets[substitution.id]
    safe_eq = equilibrium_sets[safe.id]
    manual_matrix = {(H, H): (Decimal("10"), Decimal("10")),
                     (H, M): (Decimal("10"), Decimal("8")),
                     (M, H): (Decimal("8"), Decimal("10")),
                     (M, M): (Decimal("12"), Decimal("12"))}
    computed_matrix = {profile: (result.player_payoffs["A"], result.player_payoffs["B"])
                       for profile, result in payoff_matrix(validation).items()}
    summary = {
        "run_id": "m5-exact-games-001",
        "games_evaluated": 3,
        "joint_profiles_evaluated": sum(item.profiles_evaluated for item in equilibrium_sets.values()),
        "pure_equilibria_found": sum(len(item.equilibria) for item in equilibrium_sets.values()),
        "multiple_equilibrium_games": sum(len(item.equilibria) > 1 for item in equilibrium_sets.values()),
        "no_pure_equilibrium_validation_game": 0,
        "manual_validation": {"matrix_agreement": computed_matrix == manual_matrix, "equilibrium_set_agreement": profiles(validation_eq) == ["HONEST|HONEST", "MANIPULATE|MANIPULATE"], "all_replay": all(row["replay_status"] == "PASS" for row in replay_rows)},
        "interaction_dependent_result": {"isolated_manipulation_gain": isolated_gain(validation, "A", M), "interactive_manipulation_gain": Decimal("2"), "complementarity_increment": Decimal("4"), "equilibria": profiles(validation_eq)},
        "strategic_substitution": {"equilibria": profiles(substitution_eq), "delta_other_honest": Decimal("5"), "delta_other_manipulates": Decimal("-1")},
        "safe_control": {"equilibria": profiles(safe_eq)},
        "basins": basin_summaries,
        "phase_cells": len(phase_rows),
        "scaling_max_players": 12,
        "scaling_max_profiles": 4096,
    }
    write_json(OUT / "runs" / "summary.json", summary)
    manifest = {"milestone": "M5", "git_commit": "6004d64", "engine_commit": "72694fc", "game_id": validation.id, "game_hash": game_hash(validation),
                "number_of_players": 2, "player_types": [p.type.id for p in validation.players],
                "actions": [H, M], "timing": validation.timing, "information": validation.information,
                "equilibrium_concept": "PURE_STRATEGY_NASH", "method": "EXACT_FINITE_ENUMERATION",
                "update_dynamics": [mode.value for mode in UpdateMode], "seed": None,
                "results": summary, "artifact_hash": sha256(json.dumps(norm(summary), sort_keys=True).encode()).hexdigest()}
    write_json(OUT / "runs" / "run_manifest.json", manifest)


if __name__ == "__main__":
    main()
