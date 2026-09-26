from __future__ import annotations

import csv
from dataclasses import asdict
from decimal import Decimal
import json
from pathlib import Path
from time import perf_counter

from incentive_fuzzer.core import evaluate, load_spec, spec_hash
from incentive_fuzzer.game import enumerate_pure_nash, game_hash
from incentive_fuzzer.game_fixtures import aggregate_threshold_claim, safe_interaction_control
from incentive_fuzzer.population import BehavioralKind, BehavioralScenario, deterministic_grid, evaluate_population
from incentive_fuzzer.repair import (
    GateStatus, MutationResult, RegressionCheck, RepairBudget, RepairConstraint, RepairEngine,
    RepairObjective, RepairParameter, RepairProblem, RepairStatus, classify_evaluation,
    edit_parameters, evaluate_constraints, hard_cutoff_to_phase_out, make_candidate,
    multiply_action_cost, mutation_fragility, mutation_values, pareto_frontier, run_repair_loop,
)
from incentive_fuzzer.search import SearchBudget, SearchDomain, SearchEngine, SearchProblem
from incentive_fuzzer.verify import FormalDomain, FormalVerifier


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "m6"
D = Decimal
H, M = "HONEST", "MANIPULATE"
B0 = BehavioralScenario("B0", BehavioralKind.FULL_OPTIMIZATION)


def norm(value):
    if isinstance(value, Decimal): return format(value, "f")
    if hasattr(value, "value"): return value.value
    if hasattr(value, "__dataclass_fields__"): return norm(asdict(value))
    if isinstance(value, dict): return {str(k): norm(v) for k, v in value.items() if k != "mechanism"}
    if callable(value): return getattr(value, "__name__", "callable")
    if isinstance(value, (tuple, list)): return [norm(v) for v in value]
    return value


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(norm(value), indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows([{k: norm(v) for k, v in row.items()} for row in rows])


def search(spec, states, action, controls, records=None, kinds=None):
    if records is not None:
        states = {name: values if tuple(values) else sorted({row[name] for row in records})
                  for name, values in states.items()}
    domain = SearchDomain({k: tuple(D(x) for x in values) for k, values in states.items()},
                          {action: {"amount": tuple(D(x) for x in controls)}}, {},
                          None if records is None else tuple({k: D(v) for k, v in row.items()} for row in records))
    problem = SearchProblem(spec, domain, allowed_actions=(action,), action_kinds=kinds or {})
    exhaustive = SearchEngine(problem).run("exhaustive", SearchBudget(100000, 100000, 60))
    combined = SearchEngine(problem).run("combined", SearchBudget(100000, 100000, 60), seed=17)
    max_gain = max((finding.utility_delta for finding in exhaustive.raw_findings), default=D(0))
    return problem, exhaustive, combined, max_gain


def formal(spec, states, action, controls):
    domain = FormalDomain({k: tuple(D(x) for x in values) for k, values in states.items()},
                          {"amount": tuple(D(x) for x in controls)})
    return FormalVerifier(spec, domain).verify_no_profitable_deviation(action)


def benefit(spec, state, field="benefit"):
    return D(evaluate(spec, state).outcome.rule_outputs[field])


def equilibrium_profiles(game):
    return {tuple(eq.joint_action.actions[p.id] for p in game.players) for eq in enumerate_pure_nash(game).equilibria}


def scholarship_population(spec):
    population = deterministic_grid("m6-scholarship", {"true_income": tuple(range(499995, 500011)),
        "reported_income": tuple(range(499995, 500011))}, (0,1,10,100,1000,50000,99999,100000),
        (0,.5,1,2), correlated=True)
    return evaluate_population(spec, population, B0, {"reduce_work": {"amount": tuple(range(21))}})


def evaluate_scholarship(original, candidate, original_gain, original_outputs, parameters, family, changes):
    spec = candidate.mechanism
    threshold = int(spec.parameters.get("threshold").value)
    probe = sorted(set(range(499995, 500011)) | {threshold-1, threshold, threshold+1})
    records = [{"true_income": x, "reported_income": x} for x in probe]
    _, exhaustive, combined, max_gain = search(spec, {"true_income": (), "reported_income": ()},
        "reduce_work", range(21), records, {"reduce_work": "productive_effort"})
    formal_result = formal(spec, {"true_income": probe, "reported_income": probe}, "reduce_work", range(21))
    population = scholarship_population(spec)
    outputs = [benefit(spec, {"true_income": D(x), "reported_income": D(x)}) for x in range(499995,500011)]
    schedule_distance = sum((abs(a-b) for a,b in zip(outputs,original_outputs)),D(0))
    recipient_impact = D(sum(a!=b for a,b in zip(outputs,original_outputs)))/D(len(outputs))
    fiscal_deviation = sum(outputs,D(0))/D(len(outputs))-sum(original_outputs,D(0))/D(len(original_outputs))
    coverage = benefit(spec,{"true_income":D(480000),"reported_income":D(480000)})
    complexity = D(3 if family=="STRUCTURAL_PHASE_OUT" else 1)
    mutation_results=[]
    if family=="STRUCTURAL_PHASE_OUT":
        start,end=changes["phase_out_start"],changes["phase_out_end"]
        for mutated in mutation_values(end,start+D(1),D(700000)):
            try: mutated_spec=hard_cutoff_to_phase_out(original,"benefit","reported_income","award",start,mutated)
            except Exception: continue
            _,_,_,gain=search(mutated_spec,{"true_income":(),"reported_income":()},"reduce_work",range(21),records)
            mutation_results.append(MutationResult("phase_out_end",end,mutated,gain>0,"target returned" if gain>0 else "clean"))
    else:
        name=next(iter(changes)); base=changes[name]
        definition=next(p for p in parameters if p.name==name)
        for mutated in mutation_values(base,min(definition.values),max(definition.values)):
            mutated_spec=edit_parameters(original,{name:mutated})
            mutated_threshold=int(mutated_spec.parameters["threshold"].value)
            mutation_probe=sorted(set(probe)|{mutated_threshold-1,mutated_threshold,mutated_threshold+1})
            mutation_records=[{"true_income":x,"reported_income":x} for x in mutation_probe]
            _,_,_,gain=search(mutated_spec,{"true_income":(),"reported_income":()},"reduce_work",range(21),mutation_records)
            mutation_results.append(MutationResult(name,base,mutated,gain>0,"target returned" if gain>0 else "clean"))
    fragility=mutation_fragility(tuple(mutation_results))
    metrics={"max_residual_gain":max_gain,"original_max_gain":original_gain,
        "population_profitable_share":population.summary.profitable_share,"population_max_gain":population.summary.max_gain,
        "fiscal_deviation":fiscal_deviation,"positive_fiscal_deviation":max(fiscal_deviation,D(0)),
        "schedule_distance":schedule_distance,"recipient_impact":recipient_impact,"coverage":coverage,
        "max_benefit":max(outputs),"segments":complexity,"distance":candidate.distance_from_original,
        "complexity":complexity,"harmful_equilibria":D(0),"mutation_fragility":fragility}
    constraints=evaluate_constraints((RepairConstraint("coverage","coverage",">=",D(50000)),
        RepairConstraint("benefit_cap","max_benefit","<=",D(100000)),
        RepairConstraint("segments","segments","<=",D(3))),metrics)
    checks=(RegressionCheck("M2","original witness replay","FIXED" if max_gain==0 else "SURVIVES",max_gain==0),
        RegressionCheck("M2","fresh exhaustive search",exhaustive.status.value,max_gain==0,{"findings":len(exhaustive.raw_findings)}),
        RegressionCheck("M2","combined search",combined.status.value,len(combined.raw_findings)==0),
        RegressionCheck("M3","formal profitable deviation",formal_result.status.value,"SATISFIED" in formal_result.status.value),
        RegressionCheck("M4","frozen population exposure","PASS" if population.summary.profitable_share==0 else "FAIL",population.summary.profitable_share==0),
        RegressionCheck("M5","equilibrium regression","NOT_APPLICABLE",None))
    evaluation=classify_evaluation(candidate,metrics,constraints,checks)
    return evaluation,mutation_results,formal_result.status.value


def generic_spec_evaluation(candidate, original_gain, states, action, controls, population, action_values,
                            constraints_def, formal_states):
    spec=candidate.mechanism
    _,exhaustive,combined,max_gain=search(spec,states,action,controls)
    formal_result=formal(spec,formal_states,action,controls)
    pop=evaluate_population(spec,population,B0,action_values)
    metrics={"max_residual_gain":max_gain,"original_max_gain":original_gain,
        "population_profitable_share":pop.summary.profitable_share,"population_max_gain":pop.summary.max_gain,
        "fiscal_deviation":D(0),"positive_fiscal_deviation":D(0),"schedule_distance":D(0),
        "recipient_impact":D(0),"distance":candidate.distance_from_original,"complexity":D(1),
        "harmful_equilibria":D(0),"mutation_fragility":D(0)}
    metrics.update({name:value for name,value in candidate.parameter_changes.items()})
    constraints=evaluate_constraints(constraints_def,metrics)
    checks=(RegressionCheck("M2","fresh exhaustive search",exhaustive.status.value,max_gain==0),
        RegressionCheck("M2","combined search",combined.status.value,len(combined.raw_findings)==0),
        RegressionCheck("M3","formal profitable deviation",formal_result.status.value,"SATISFIED" in formal_result.status.value),
        RegressionCheck("M4","frozen population exposure","PASS" if pop.summary.profitable_share==0 else "FAIL",pop.summary.profitable_share==0),
        RegressionCheck("M5","equilibrium regression","NOT_APPLICABLE",None))
    return classify_evaluation(candidate,metrics,constraints,checks),formal_result.status.value


def row(evaluation, formal_status="NOT_APPLICABLE"):
    return {"repair_id":evaluation.candidate.repair_id,"family":evaluation.candidate.repair_family,
        "changes":json.dumps(norm(evaluation.candidate.parameter_changes),sort_keys=True),
        "status":evaluation.repair_status.value,"gate":evaluation.gate_status.value,
        "max_residual_gain":evaluation.metrics.get("max_residual_gain",D(0)),
        "population_profitable_share":evaluation.metrics.get("population_profitable_share",D(0)),
        "fiscal_deviation":evaluation.metrics.get("fiscal_deviation",D(0)),
        "distance":evaluation.metrics.get("distance",evaluation.candidate.distance_from_original),
        "complexity":evaluation.metrics.get("complexity",D(0)),
        "harmful_equilibria":evaluation.metrics.get("harmful_equilibria",D(0)),
        "mutation_fragility":evaluation.metrics.get("mutation_fragility",D(0)),
        "formal_status":formal_status}


def main():
    started=perf_counter()
    for folder in ("configs","runs","repairs","tables","figures","replays","mutations"):
        (OUT/folder).mkdir(parents=True,exist_ok=True)
    write_json(OUT/"configs"/"registered_design.json",{"precommitment":"research/M6_PRECOMMITMENT.md",
        "implementation_commit":"dda4b25","search":"EXHAUSTIVE_GRID","budgets":{"max_candidates":100,"max_iterations":5,"seconds":120},
        "mutation_deltas":[1,5,10]})

    all_evaluations=[]; mutation_rows=[]; regression_rows=[]; formal_rows=[]

    # E1/E2 scholarship.
    scholarship=load_spec(ROOT/"examples/scholarship_cliff.yaml")
    scholarship_params=(RepairParameter("threshold",D(500000),tuple(map(D,(480000,490000,499999,500000,500001))),D(10000)),
        RepairParameter("award",D(100000),tuple(map(D,(0,50000,75000,99999,100000))),D(100000)),
        RepairParameter("phase_out_start",D(500000),tuple(map(D,(480000,500000))),D(100000)),
        RepairParameter("phase_out_end",D(500000),tuple(map(D,(580000,600000,680000,700000))),D(100000)))
    scholarship_problem=RepairProblem("scholarship",spec_hash(scholarship),"m2-scholarship-cliff","no_profitable_downward_manipulation",
        scholarship_params,(),tuple(RepairObjective(name,"min") for name in ("max_residual_gain","positive_fiscal_deviation","distance","complexity","harmful_equilibria","mutation_fragility")),RepairBudget())
    base_records=[{"true_income":x,"reported_income":x} for x in range(499995,500011)]
    _,_,_,scholarship_original_gain=search(scholarship,{"true_income":(),"reported_income":()},"reduce_work",range(21),base_records)
    original_outputs=[benefit(scholarship,{"true_income":D(x),"reported_income":D(x)}) for x in range(499995,500011)]
    scholarship_candidates=[]
    for name,values in (("threshold",scholarship_params[0].values),("award",scholarship_params[1].values)):
        for value in values:
            if value==next(p.original for p in scholarship_params if p.name==name): continue
            spec=edit_parameters(scholarship,{name:value}); scholarship_candidates.append(make_candidate(spec_hash(scholarship),"PARAMETER_EDIT",{name:value},scholarship_params,spec,spec_hash(spec)))
    for start,end in ((480000,580000),(480000,680000),(500000,600000),(500000,700000)):
        spec=hard_cutoff_to_phase_out(scholarship,"benefit","reported_income","award",D(start),D(end))
        changes={"phase_out_start":D(start),"phase_out_end":D(end)}
        scholarship_candidates.append(make_candidate(spec_hash(scholarship),"STRUCTURAL_PHASE_OUT",changes,scholarship_params,spec,spec_hash(spec),"STRUCTURAL_TRANSFORM"))
    scholarship_evals=[]
    for candidate in scholarship_candidates:
        evaluation,mutations,formal_status=evaluate_scholarship(scholarship,candidate,scholarship_original_gain,original_outputs,scholarship_params,candidate.repair_family,candidate.parameter_changes)
        scholarship_evals.append(evaluation); all_evaluations.append(evaluation); formal_rows.append({"problem":"scholarship","repair_id":candidate.repair_id,"status":formal_status})
        mutation_rows.extend({"problem":"scholarship","repair_id":candidate.repair_id,**norm(item)} for item in mutations)
    scholarship_frontier=pareto_frontier(tuple(scholarship_evals),scholarship_problem.objectives)

    # E3 stacked programs.
    stacked=load_spec(ROOT/"examples/stacked_programs.yaml")
    stacked_params=(RepairParameter("award_a",D(8),tuple(map(D,(0,2,4,6,8))),D(8)),RepairParameter("award_b",D(5),tuple(map(D,(0,1,3,5))),D(5)))
    stacked_problem=RepairProblem("stacked",spec_hash(stacked),"m2-stacked","no_profitable_deviation",stacked_params,(),
        (RepairObjective("max_residual_gain","min"),RepairObjective("distance","min")),RepairBudget())
    _,_,_,stacked_original_gain=search(stacked,{"income":range(21)},"reduce_income",range(6))
    stacked_pop=deterministic_grid("stacked",{"income":tuple(range(21))},(0,1,5,10))
    stacked_evals=[]
    for a in stacked_params[0].values:
        for b in stacked_params[1].values:
            if (a,b)==(D(8),D(5)): continue
            spec=edit_parameters(stacked,{"award_a":a,"award_b":b})
            candidate=make_candidate(spec_hash(stacked),"PARAMETER_EDIT",{"award_a":a,"award_b":b},stacked_params,spec,spec_hash(spec))
            constraints=(RepairConstraint("program_a_min","award_a",">=",D(4)),RepairConstraint("program_b_min","award_b",">=",D(3)))
            evaluation,formal_status=generic_spec_evaluation(candidate,stacked_original_gain,{"income":range(21)},"reduce_income",range(6),stacked_pop,{"reduce_income":{"amount":tuple(range(6))}},constraints,{"income":range(21)})
            stacked_evals.append(evaluation); all_evaluations.append(evaluation); formal_rows.append({"problem":"stacked","repair_id":candidate.repair_id,"status":formal_status})

    # E4 procurement.
    procurement=load_spec(ROOT/"examples/procurement_threshold.yaml")
    procurement_params=(RepairParameter("threshold",D(100),tuple(map(D,(98,99,100,101,102))),D(10)),RepairParameter("process_cost",D(20),tuple(map(D,(0,5,10,15,20))),D(20)),RepairParameter("cost_multiplier",D(1),tuple(map(D,(1,5,10,19,20))),D(20)))
    _,_,_,proc_original_gain=search(procurement,{"transaction_value":range(95,106)},"reduce_scope",range(11))
    procurement_pop=deterministic_grid("procurement",{"transaction_value":tuple(range(95,106))},(0,1,5,10,20))
    procurement_evals=[]
    candidates=[]
    for name,param in (("threshold",procurement_params[0]),("process_cost",procurement_params[1])):
        for value in param.values:
            if value==param.original: continue
            spec=edit_parameters(procurement,{name:value}); candidates.append(make_candidate(spec_hash(procurement),"PARAMETER_EDIT",{name:value},procurement_params,spec,spec_hash(spec)))
    for value in procurement_params[2].values:
        if value==1: continue
        spec=multiply_action_cost(procurement,"reduce_scope",value); candidates.append(make_candidate(spec_hash(procurement),"ACTION_COST_MULTIPLIER",{"cost_multiplier":value},procurement_params,spec,spec_hash(spec),"STRUCTURAL_TRANSFORM"))
    for candidate in candidates:
        metrics_constraints=(RepairConstraint("process_cost_min","process_cost",">=",D(10)),)
        # Structural candidates retain original process cost; expose it for the constraint.
        candidate_changes=dict(candidate.parameter_changes)
        if "process_cost" not in candidate_changes: candidate_changes["process_cost"]=D(20)
        proxy=make_candidate(candidate.parent_spec_hash,candidate.repair_family,candidate_changes,procurement_params,candidate.mechanism,candidate.candidate_spec_hash,candidate.provenance)
        evaluation,formal_status=generic_spec_evaluation(proxy,proc_original_gain,{"transaction_value":range(95,106)},"reduce_scope",range(11),procurement_pop,{"reduce_scope":{"amount":tuple(range(11))}},metrics_constraints,{"transaction_value":range(95,106)})
        procurement_evals.append(evaluation); all_evaluations.append(evaluation); formal_rows.append({"problem":"procurement","repair_id":proxy.repair_id,"status":formal_status})

    # E5 strategic game repair.
    original_game=aggregate_threshold_claim(); original_profiles=equilibrium_profiles(original_game)
    game_params=(RepairParameter("cost",D(2),tuple(map(D,(2,3,4,5)))),RepairParameter("bonus",D(4),tuple(map(D,(1,2,3,4)))),RepairParameter("threshold",D(2),tuple(map(D,(1,2)))))
    game_objectives=(RepairObjective("harmful_equilibria","min"),RepairObjective("distance","min"),RepairObjective("fiscal_deviation","min"),RepairObjective("mutation_fragility","min"))
    game_problem=RepairProblem("strategic_game",game_hash(original_game),"m5-mm-equilibrium","remove_target_equilibrium",game_params,(),game_objectives,RepairBudget())
    game_evals=[]
    for cost in game_params[0].values:
        for bonus in game_params[1].values:
            for threshold in game_params[2].values:
                if (cost,bonus,threshold)==(D(2),D(4),D(2)): continue
                game=aggregate_threshold_claim(bonus,cost,int(threshold)); changes={"cost":cost,"bonus":bonus,"threshold":threshold}
                candidate=make_candidate(game_hash(original_game),"GAME_PARAMETER_EDIT",changes,game_params,game,game_hash(game))
                profiles=equilibrium_profiles(game); harmful=D((M,M) in profiles); honest=D((H,H) in profiles)
                mutation_results=[]
                for name,value,lower,upper in (("cost",cost,D(0),D(10)),("bonus",bonus,D(0),D(10))):
                    for mutated in mutation_values(value,lower,upper):
                        params={"cost":cost,"bonus":bonus}; params[name]=mutated
                        mutated_profiles=equilibrium_profiles(aggregate_threshold_claim(params["bonus"],params["cost"],int(threshold)))
                        mutation_results.append(MutationResult(name,value,mutated,(M,M) in mutated_profiles,"harmful equilibrium returned" if (M,M) in mutated_profiles else "clean"))
                fragility=mutation_fragility(tuple(mutation_results)); mutation_rows.extend({"problem":"strategic_game","repair_id":candidate.repair_id,**norm(item)} for item in mutation_results)
                fiscal=D(0)
                if (M,M) in profiles: fiscal=D(2)*bonus
                metrics={"max_residual_gain":harmful,"original_max_gain":D(1),"harmful_equilibria":harmful,"honest_equilibrium":honest,
                    "bonus":bonus,"positive_payout":D(bonus>0),"distance":candidate.distance_from_original,"complexity":D(1),
                    "fiscal_deviation":fiscal-D(8),"positive_fiscal_deviation":max(fiscal-D(8),D(0)),"mutation_fragility":fragility,
                    "population_profitable_share":D(0)}
                constraints=evaluate_constraints((RepairConstraint("bonus_min","bonus",">=",D(3)),RepairConstraint("payout","positive_payout",">=",D(1)),RepairConstraint("honest","honest_equilibrium",">=",D(1))),metrics)
                checks=(RegressionCheck("M2","single-agent attack","NOT_APPLICABLE",None),RegressionCheck("M3","formal check","NOT_APPLICABLE",None),RegressionCheck("M4","population","NOT_APPLICABLE",None),RegressionCheck("M5","target manipulation equilibrium","REMOVED" if not harmful else "PRESENT",not bool(harmful),{"equilibria":["|".join(p) for p in sorted(profiles)]}))
                evaluation=classify_evaluation(candidate,metrics,constraints,checks)
                game_evals.append(evaluation); all_evaluations.append(evaluation)
    game_frontier=pareto_frontier(tuple(game_evals),game_objectives)

    # E6 safe no-repair control.
    safe=safe_interaction_control(); safe_profiles=equilibrium_profiles(safe)
    safe_result={"status":"NO_REPAIR_NEEDED" if safe_profiles=={(H,H)} else "UNEXPECTED_VULNERABILITY","equilibria":["|".join(p) for p in safe_profiles],"game_hash":game_hash(safe)}

    # E7 repair-induced vulnerability fixture.
    induced=[]
    for penalty in (D(1),D(2)):
        isolated_gain=D(2)-penalty; game=aggregate_threshold_claim(bonus=D(3)*penalty,cost=D(5),threshold=2)
        profiles=equilibrium_profiles(game); harmful=(M,M) in profiles
        induced.append({"penalty":penalty,"isolated_gain":isolated_gain,"isolated_fixed":isolated_gain<=0,
            "interaction_bonus":D(3)*penalty,"equilibria":["|".join(p) for p in sorted(profiles)],"harmful_equilibrium":harmful,
            "status":RepairStatus.REPAIR_INDUCED_VULNERABILITY.value if isolated_gain<=0 and harmful else "BASELINE"})

    # E10 bounded loop selects first passing scholarship frontier candidate.
    passing=list(scholarship_frontier.candidates)
    loop=run_repair_loop("scholarship-ce-0",RepairBudget(max_iterations=5),lambda iteration,ce,seen: next((item for item in passing if item.candidate.repair_id not in seen),None))

    # Persist candidate evidence and regression matrix.
    problem_sets={"scholarship":scholarship_evals,"stacked":stacked_evals,"procurement":procurement_evals,"strategic_game":game_evals}
    for problem_name,evaluations in problem_sets.items():
        for evaluation in evaluations:
            write_json(OUT/"repairs"/f"{problem_name}-{evaluation.candidate.repair_id}.json",evaluation)
            for check in evaluation.regressions:
                regression_rows.append({"problem":problem_name,"repair_id":evaluation.candidate.repair_id,"layer":check.layer,"check":check.check,"status":check.status,"passed":"NOT_APPLICABLE" if check.passed is None else check.passed})
    write_csv(OUT/"tables"/"scholarship_repairs.csv",[row(item,next((r["status"] for r in formal_rows if r["repair_id"]==item.candidate.repair_id),"NOT_APPLICABLE")) for item in scholarship_evals])
    write_csv(OUT/"tables"/"stacked_repairs.csv",[row(item,next((r["status"] for r in formal_rows if r["repair_id"]==item.candidate.repair_id),"NOT_APPLICABLE")) for item in stacked_evals])
    write_csv(OUT/"tables"/"procurement_repairs.csv",[row(item,next((r["status"] for r in formal_rows if r["repair_id"]==item.candidate.repair_id),"NOT_APPLICABLE")) for item in procurement_evals])
    write_csv(OUT/"tables"/"game_repairs.csv",[row(item) for item in game_evals])
    write_csv(OUT/"tables"/"regression_matrix.csv",regression_rows)
    write_csv(OUT/"tables"/"mutation_results.csv",mutation_rows)
    write_csv(OUT/"tables"/"formal_regression.csv",formal_rows)
    write_json(OUT/"runs"/"safe_control.json",safe_result); write_json(OUT/"runs"/"repair_induced_vulnerability.json",induced); write_json(OUT/"runs"/"repair_loop.json",loop)
    write_json(OUT/"runs"/"pareto_frontiers.json",{"scholarship":[item.candidate.repair_id for item in scholarship_frontier.candidates],"strategic_game":[item.candidate.repair_id for item in game_frontier.candidates]})
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="700" height="260"><rect width="100%" height="100%" fill="white"/><text x="350" y="25" text-anchor="middle" font-size="16">M6 scholarship repair tradeoffs</text>'
    for i,item in enumerate(scholarship_evals):
        x=60+float(item.metrics["distance"])*80; y=220-float(item.metrics["max_residual_gain"])/500
        color="#54A24B" if item.gate_status is GateStatus.REPAIR_PASS else "#E45756"
        svg+=f'<circle cx="{min(x,670):.1f}" cy="{max(40,min(y,220)):.1f}" r="5" fill="{color}"/>'
    svg+='<text x="350" y="252" text-anchor="middle">normalized repair distance</text></svg>\n'; (OUT/"figures"/"scholarship_pareto.svg").write_text(svg,encoding="utf-8")

    elapsed=D(str(perf_counter()-started)); summary={"run_id":"m6-bounded-repair-001","search_method":"EXHAUSTIVE_GRID",
        "candidates_evaluated":len(all_evaluations),"regression_checks":len(regression_rows),"runtime_seconds":elapsed,
        "passing_repairs":sum(item.gate_status is GateStatus.REPAIR_PASS for item in all_evaluations),
        "scholarship":{"original_max_gain":scholarship_original_gain,"candidates":len(scholarship_evals),"passes":sum(item.gate_status is GateStatus.REPAIR_PASS for item in scholarship_evals),"pareto":[item.candidate.repair_id for item in scholarship_frontier.candidates]},
        "stacked":{"original_max_gain":stacked_original_gain,"candidates":len(stacked_evals),"passes":sum(item.gate_status is GateStatus.REPAIR_PASS for item in stacked_evals)},
        "procurement":{"original_max_gain":proc_original_gain,"candidates":len(procurement_evals),"passes":sum(item.gate_status is GateStatus.REPAIR_PASS for item in procurement_evals)},
        "strategic_game":{"original_equilibria":["|".join(p) for p in sorted(original_profiles)],"candidates":len(game_evals),"passes":sum(item.gate_status is GateStatus.REPAIR_PASS for item in game_evals),"pareto":[item.candidate.repair_id for item in game_frontier.candidates]},
        "safe_control":safe_result,"repair_induced":induced[1],"loop_stop":loop.stop_reason,
        "mutation_tests":len(mutation_rows),"formal_checks":len(formal_rows)}
    write_json(OUT/"runs"/"summary.json",summary)
    write_json(OUT/"runs"/"run_manifest.json",{"milestone":"M6","implementation_commit":"dda4b25","precommitment_commit":"d3b38b0","results":summary})
    print(json.dumps(norm(summary),indent=2))


if __name__ == "__main__": main()
