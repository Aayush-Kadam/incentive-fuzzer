from decimal import Decimal

from .game import Game, JointAction, PayoffProfile, Player, PlayerType


def _players(n: int = 2) -> tuple[Player, ...]:
    return tuple(Player(chr(65 + i), PlayerType("synthetic", {"endowment": Decimal("10")}),
                        ("HONEST", "MANIPULATE")) for i in range(n))


def aggregate_threshold_claim(bonus=Decimal("4"), cost=Decimal("2"), threshold=2, n=2) -> Game:
    def evaluator(game: Game, joint: JointAction) -> PayoffProfile:
        count = sum(action == "MANIPULATE" for action in joint.actions.values())
        reached = count >= int(game.parameters["threshold"])
        payoffs, payout_total = {}, Decimal("0")
        for player in game.players:
            manipulates = joint.actions[player.id] == "MANIPULATE"
            payout = Decimal(game.parameters["bonus"]) if manipulates and reached else Decimal("0")
            action_cost = Decimal(game.parameters["cost"]) if manipulates else Decimal("0")
            payoffs[player.id] = Decimal("10") - action_cost + payout
            payout_total += payout
        return PayoffProfile(payoffs, {"payout_total": payout_total, "manipulation_count": Decimal(count)},
                             {"claim_count": Decimal(count), "threshold_reached": reached})
    return Game("aggregate_threshold_claim", _players(n), "aggregate claim-count threshold",
                {"bonus": Decimal(bonus), "cost": Decimal(cost), "threshold": Decimal(threshold)}, evaluator)


def scarcity_capture(prize=Decimal("6"), cost=Decimal("1")) -> Game:
    def evaluator(game: Game, joint: JointAction) -> PayoffProfile:
        manipulators = [p.id for p in game.players if joint.actions[p.id] == "MANIPULATE"]
        payoffs = {p.id: Decimal("10") for p in game.players}
        allocation = Decimal("0")
        if len(manipulators) == 1:
            payoffs[manipulators[0]] += Decimal(game.parameters["prize"]) - Decimal(game.parameters["cost"])
            allocation = Decimal("1")
        elif len(manipulators) > 1:
            for identifier in manipulators:
                payoffs[identifier] -= Decimal(game.parameters["cost"])
        return PayoffProfile(payoffs, {"captured_allocations": allocation,
                                       "manipulation_count": Decimal(len(manipulators))},
                             {"claim_count": Decimal(len(manipulators)), "capacity": Decimal("1")})
    return Game("scarcity_capture", _players(), "capacity-one allocation with collision",
                {"prize": Decimal(prize), "cost": Decimal(cost)}, evaluator)


def safe_interaction_control() -> Game:
    return aggregate_threshold_claim(bonus=Decimal("1"), cost=Decimal("2"), threshold=2)


def matrix_game(game_id: str, matrix: dict[tuple[str, str], tuple[str, str]]) -> Game:
    def evaluator(game: Game, joint: JointAction) -> PayoffProfile:
        cell = matrix[(joint.actions["A"], joint.actions["B"])]
        count = sum(action == "MANIPULATE" for action in joint.actions.values())
        return PayoffProfile({"A": Decimal(cell[0]), "B": Decimal(cell[1])},
                             {"manipulation_count": Decimal(count)})
    return Game(game_id, _players(), "explicit validation matrix", {"matrix": str(sorted(matrix.items()))}, evaluator)


def prisoners_dilemma() -> Game:
    return matrix_game("prisoners_dilemma", {
        ("HONEST", "HONEST"): ("3", "3"), ("HONEST", "MANIPULATE"): ("0", "5"),
        ("MANIPULATE", "HONEST"): ("5", "0"), ("MANIPULATE", "MANIPULATE"): ("1", "1")})


def coordination_game() -> Game:
    return matrix_game("coordination", {
        ("HONEST", "HONEST"): ("2", "2"), ("HONEST", "MANIPULATE"): ("0", "0"),
        ("MANIPULATE", "HONEST"): ("0", "0"), ("MANIPULATE", "MANIPULATE"): ("3", "3")})


def matching_pennies() -> Game:
    return matrix_game("matching_pennies", {
        ("HONEST", "HONEST"): ("1", "-1"), ("HONEST", "MANIPULATE"): ("-1", "1"),
        ("MANIPULATE", "HONEST"): ("-1", "1"), ("MANIPULATE", "MANIPULATE"): ("1", "-1")})


def anti_coordination() -> Game:
    return matrix_game("anti_coordination", {
        ("HONEST", "HONEST"): ("0", "0"), ("HONEST", "MANIPULATE"): ("2", "2"),
        ("MANIPULATE", "HONEST"): ("2", "2"), ("MANIPULATE", "MANIPULATE"): ("0", "0")})
