from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from enum import Enum
from hashlib import sha256
from itertools import product
import json
from typing import Any, Callable, Mapping


class EquilibriumStatus(str, Enum):
    PURE_NASH = "PURE_NASH"
    NOT_EQUILIBRIUM = "NOT_EQUILIBRIUM"


class DynamicsStatus(str, Enum):
    CONVERGED_EQUILIBRIUM = "CONVERGED_EQUILIBRIUM"
    CYCLE_DETECTED = "CYCLE_DETECTED"
    MAX_STEPS = "MAX_STEPS"


class UpdateMode(str, Enum):
    SYNCHRONOUS = "SYNCHRONOUS"
    ASYNCHRONOUS = "ASYNCHRONOUS"


@dataclass(frozen=True)
class PlayerType:
    id: str
    state: Mapping[str, Decimal | str | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class Player:
    id: str
    type: PlayerType
    actions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.id or not self.actions or len(set(self.actions)) != len(self.actions):
            raise ValueError("player requires an id and unique nonempty actions")


@dataclass(frozen=True)
class JointAction:
    actions: Mapping[str, str]


@dataclass(frozen=True)
class PayoffProfile:
    player_payoffs: Mapping[str, Decimal]
    designer_outcomes: Mapping[str, Decimal | bool]
    aggregates: Mapping[str, Decimal | bool] = field(default_factory=dict)


GameEvaluator = Callable[["Game", JointAction], PayoffProfile]


@dataclass(frozen=True)
class Game:
    id: str
    players: tuple[Player, ...]
    mechanism: str
    parameters: Mapping[str, Decimal | str | bool]
    evaluator: GameEvaluator = field(compare=False, repr=False)
    timing: str = "simultaneous"
    information: str = "complete"
    neutral_action: str = "HONEST"

    def __post_init__(self) -> None:
        if len(self.players) < 2:
            raise ValueError("a game requires at least two players")
        if len({p.id for p in self.players}) != len(self.players):
            raise ValueError("player ids must be unique")
        if self.timing != "simultaneous":
            raise ValueError("M5 supports simultaneous games only")
        if self.information != "complete":
            raise ValueError("M5 supports complete-information games only")


@dataclass(frozen=True)
class BestResponse:
    player_id: str
    opponents: Mapping[str, str]
    actions: tuple[str, ...]
    payoff: Decimal


@dataclass(frozen=True)
class DeviationWitness:
    player_id: str
    from_action: str
    to_action: str
    from_payoff: Decimal
    to_payoff: Decimal


@dataclass(frozen=True)
class EquilibriumVerification:
    status: EquilibriumStatus
    joint_action: JointAction
    payoff: PayoffProfile
    deviation: DeviationWitness | None


@dataclass(frozen=True)
class Equilibrium:
    equilibrium_id: str
    joint_action: JointAction
    player_payoffs: Mapping[str, Decimal]
    designer_outcomes: Mapping[str, Decimal | bool]
    equilibrium_concept: str = "PURE_STRATEGY_NASH"
    verification_method: str = "EXACT_UNILATERAL_ENUMERATION"
    stability_metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EquilibriumSet:
    game_id: str
    game_hash: str
    equilibria: tuple[Equilibrium, ...]
    profiles_evaluated: int
    method: str = "EXACT_FINITE_ENUMERATION"


@dataclass(frozen=True)
class DynamicsResult:
    status: DynamicsStatus
    mode: UpdateMode
    initial_profile: JointAction
    path: tuple[JointAction, ...]
    terminal_profile: JointAction | None
    equilibrium_verified: bool
    cycle: tuple[JointAction, ...] = ()


@dataclass(frozen=True)
class BasinResult:
    mode: UpdateMode
    equilibrium_counts: Mapping[str, int]
    cycles: int
    max_steps: int
    total_initial_profiles: int
    results: tuple[DynamicsResult, ...]


@dataclass(frozen=True)
class InteractionFinding:
    finding_id: str
    game_hash: str
    players: tuple[str, ...]
    interaction_type: str
    baseline_profile: JointAction
    equilibrium_profiles: tuple[JointAction, ...]
    property_violated: str
    designer_outcomes: tuple[Mapping[str, Decimal | bool], ...]
    player_payoffs: tuple[Mapping[str, Decimal], ...]
    best_response_map: Mapping[str, tuple[str, ...]]
    equilibrium_method: str
    assumptions: Mapping[str, str]
    replay_status: str


def _normal(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return _normal(asdict(value))
    if isinstance(value, Mapping):
        return {str(k): _normal(value[k]) for k in sorted(value)}
    if isinstance(value, (tuple, list)):
        return [_normal(item) for item in value]
    return value


def game_hash(game: Game) -> str:
    identity = {"id": game.id, "players": game.players, "mechanism": game.mechanism,
                "parameters": game.parameters, "timing": game.timing,
                "information": game.information, "neutral_action": game.neutral_action,
                "equilibrium_concept": "PURE_STRATEGY_NASH"}
    payload = json.dumps(_normal(identity), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode()).hexdigest()


def joint_profiles(game: Game) -> tuple[JointAction, ...]:
    ids = tuple(player.id for player in game.players)
    return tuple(JointAction(dict(zip(ids, actions))) for actions in product(*(p.actions for p in game.players)))


def evaluate_game(game: Game, joint_action: JointAction) -> PayoffProfile:
    expected = {player.id for player in game.players}
    if set(joint_action.actions) != expected:
        raise ValueError("joint action must specify every player exactly once")
    for player in game.players:
        if joint_action.actions[player.id] not in player.actions:
            raise ValueError(f"unknown action for player {player.id}")
    result = game.evaluator(game, joint_action)
    if set(result.player_payoffs) != expected:
        raise ValueError("evaluator must return one payoff per player")
    if any(not isinstance(value, Decimal) for value in result.player_payoffs.values()):
        raise TypeError("player payoffs must use exact Decimal values")
    return result


def best_response(game: Game, player_id: str, opponents: Mapping[str, str]) -> BestResponse:
    player = next((item for item in game.players if item.id == player_id), None)
    if player is None:
        raise ValueError(f"unknown player {player_id}")
    expected = {item.id for item in game.players if item.id != player_id}
    if set(opponents) != expected:
        raise ValueError("opponent profile has incorrect players")
    scored = []
    for action in player.actions:
        profile = JointAction(dict(opponents) | {player_id: action})
        scored.append((action, evaluate_game(game, profile).player_payoffs[player_id]))
    maximum = max(score for _, score in scored)
    return BestResponse(player_id, dict(opponents), tuple(a for a, score in scored if score == maximum), maximum)


def best_response_map(game: Game) -> Mapping[str, Mapping[tuple[str, ...], tuple[str, ...]]]:
    result = {}
    for player in game.players:
        others = tuple(item for item in game.players if item.id != player.id)
        rows = {}
        for actions in product(*(item.actions for item in others)):
            opponents = dict(zip((item.id for item in others), actions))
            rows[actions] = best_response(game, player.id, opponents).actions
        result[player.id] = rows
    return result


def verify_pure_nash(game: Game, joint_action: JointAction) -> EquilibriumVerification:
    current = evaluate_game(game, joint_action)
    for player in game.players:
        from_action = joint_action.actions[player.id]
        from_payoff = current.player_payoffs[player.id]
        for action in player.actions:
            if action == from_action:
                continue
            deviation_profile = JointAction(dict(joint_action.actions) | {player.id: action})
            to_payoff = evaluate_game(game, deviation_profile).player_payoffs[player.id]
            if to_payoff > from_payoff:
                witness = DeviationWitness(player.id, from_action, action, from_payoff, to_payoff)
                return EquilibriumVerification(EquilibriumStatus.NOT_EQUILIBRIUM, joint_action, current, witness)
    return EquilibriumVerification(EquilibriumStatus.PURE_NASH, joint_action, current, None)


def enumerate_pure_nash(game: Game) -> EquilibriumSet:
    equilibria = []
    identity = game_hash(game)
    profiles = joint_profiles(game)
    for profile in profiles:
        verification = verify_pure_nash(game, profile)
        if verification.status is EquilibriumStatus.PURE_NASH:
            encoded = json.dumps(_normal(profile), sort_keys=True, separators=(",", ":"))
            equilibrium_id = sha256(f"{identity}:{encoded}".encode()).hexdigest()[:16]
            equilibria.append(Equilibrium(equilibrium_id, profile, verification.payoff.player_payoffs,
                                          verification.payoff.designer_outcomes))
    return EquilibriumSet(game.id, identity, tuple(equilibria), len(profiles))


def replay_equilibrium(game: Game, equilibrium: Equilibrium) -> bool:
    result = verify_pure_nash(game, equilibrium.joint_action)
    return (result.status is EquilibriumStatus.PURE_NASH
            and result.payoff.player_payoffs == equilibrium.player_payoffs
            and result.payoff.designer_outcomes == equilibrium.designer_outcomes)


def _selected_response(game: Game, player: Player, profile: JointAction) -> str:
    opponents = {key: value for key, value in profile.actions.items() if key != player.id}
    responses = best_response(game, player.id, opponents).actions
    current = profile.actions[player.id]
    return current if current in responses else responses[0]


def run_best_response_dynamics(game: Game, initial: JointAction, mode: UpdateMode,
                               max_steps: int = 100) -> DynamicsResult:
    evaluate_game(game, initial)
    path = [initial]
    seen = {tuple(initial.actions[p.id] for p in game.players): 0}
    current = initial
    for _ in range(max_steps):
        if verify_pure_nash(game, current).status is EquilibriumStatus.PURE_NASH:
            return DynamicsResult(DynamicsStatus.CONVERGED_EQUILIBRIUM, mode, initial, tuple(path), current, True)
        if mode is UpdateMode.SYNCHRONOUS:
            updated = {player.id: _selected_response(game, player, current) for player in game.players}
            next_profile = JointAction(updated)
        else:
            updated = dict(current.actions)
            for player in game.players:
                interim = JointAction(dict(updated))
                updated[player.id] = _selected_response(game, player, interim)
            next_profile = JointAction(updated)
        path.append(next_profile)
        key = tuple(next_profile.actions[p.id] for p in game.players)
        if key in seen:
            start = seen[key]
            return DynamicsResult(DynamicsStatus.CYCLE_DETECTED, mode, initial, tuple(path), None, False,
                                  tuple(path[start:]))
        seen[key] = len(path) - 1
        current = next_profile
    return DynamicsResult(DynamicsStatus.MAX_STEPS, mode, initial, tuple(path), None, False)


def enumerate_basins(game: Game, mode: UpdateMode, max_steps: int = 100) -> BasinResult:
    results = tuple(run_best_response_dynamics(game, profile, mode, max_steps) for profile in joint_profiles(game))
    counts = {}
    cycles = capped = 0
    for result in results:
        if result.status is DynamicsStatus.CONVERGED_EQUILIBRIUM and result.terminal_profile:
            key = "|".join(result.terminal_profile.actions[player.id] for player in game.players)
            counts[key] = counts.get(key, 0) + 1
        elif result.status is DynamicsStatus.CYCLE_DETECTED:
            cycles += 1
        else:
            capped += 1
    return BasinResult(mode, counts, cycles, capped, len(results), results)


def payoff_matrix(game: Game) -> Mapping[tuple[str, ...], PayoffProfile]:
    return {tuple(profile.actions[p.id] for p in game.players): evaluate_game(game, profile)
            for profile in joint_profiles(game)}


def isolated_gain(game: Game, player_id: str, action: str) -> Decimal:
    baseline = JointAction({item.id: game.neutral_action for item in game.players})
    deviation = JointAction(dict(baseline.actions) | {player_id: action})
    return evaluate_game(game, deviation).player_payoffs[player_id] - evaluate_game(game, baseline).player_payoffs[player_id]


def externality(game: Game, actor_id: str, from_action: str, to_action: str,
                context: Mapping[str, str]) -> Mapping[str, Decimal]:
    before = evaluate_game(game, JointAction(dict(context) | {actor_id: from_action}))
    after = evaluate_game(game, JointAction(dict(context) | {actor_id: to_action}))
    return {player.id: after.player_payoffs[player.id] - before.player_payoffs[player.id] for player in game.players}
