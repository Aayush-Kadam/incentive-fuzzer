"""Execute the frozen M4 design. Standard library only; deterministic outputs."""
from __future__ import annotations
import csv, json, subprocess
from dataclasses import asdict
from decimal import Decimal as D
from pathlib import Path
from time import perf_counter

from incentive_fuzzer import (AgentType, BehavioralKind, BehavioralScenario,
    PopulationSpecification, deterministic_grid, evaluate_population, load_spec,
    population_hash, sample_weighted, wilson_interval)
from incentive_fuzzer.verify import FormalDomain, FormalVerifier

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"experiments"/"m4"
FIXED=(0,1,10,100,1000,50000,99999,100000)
SCENARIOS=(BehavioralScenario("B0",BehavioralKind.FULL_OPTIMIZATION),
           BehavioralScenario("B1",BehavioralKind.LIMITED_SEARCH,3),
           BehavioralScenario("B2",BehavioralKind.SATISFICING,hurdle=D(100)))

CASES={
 "scholarship":("scholarship_cliff",{"true_income":tuple(range(499995,500011)),"reported_income":tuple(range(499995,500011))},FIXED,(0,.5,1,2),True,"reduce_work",20),
 "phase_out":("linear_phase_out",{"income":(479999,480000,480001,500000,550000,619999,620000,620001)},FIXED,(1,),False,"reduce_income",20),
 "stacked":("stacked_programs",{"income":tuple(range(21))},(0,1,5,10),(1,),False,"reduce_income",5),
 "procurement":("procurement_threshold",{"transaction_value":tuple(range(95,106))},(0,1,5,10,20),(1,),False,"reduce_scope",10),
 "honest":("honest_reporting_control",{"true_income":tuple(range(21)),"reported_income":tuple(range(21))},(0,1,5,10),(1,),True,"misreport",10),
}

def norm(v):
    if isinstance(v,D): return format(v,"f")
    if hasattr(v,"value"): return v.value
    if isinstance(v,dict): return {k:norm(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)): return [norm(x) for x in v]
    return v

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ["empty"]); w.writeheader(); w.writerows(rows)

def main():
    for d in ("configs","runs","tables","figures","populations"): (OUT/d).mkdir(parents=True,exist_ok=True)
    rows=[]; cells=[]; individual=[]
    for label,(fixture,states,fixed,mults,corr,action,max_amount) in CASES.items():
        spec=load_spec(ROOT/"examples"/f"{fixture}.yaml")
        pop=deterministic_grid(label,states,fixed,mults,correlated=corr)
        (OUT/"populations"/f"{label}.json").write_text(json.dumps(norm(asdict(pop)),indent=2),encoding="utf-8")
        actions={action:{"amount":tuple(range(max_amount+1))}}
        for scenario in SCENARIOS:
            start=perf_counter(); result=evaluate_population(spec,pop,scenario,actions,f"M4-{label}-{scenario.id}"); seconds=perf_counter()-start
            s=result.summary
            rows.append({"case":label,"scenario":scenario.id,"members":len(pop.members),"profitable_share":s.profitable_share,"response_share":s.response_share,"mean_positive_gain":s.mean_positive_gain,"max_gain":s.max_gain,"designer_impact":json.dumps(norm(s.designer_change),sort_keys=True),"evaluations":result.evaluations,"seconds":f"{seconds:.6f}","agents_per_second":f"{len(pop.members)/seconds:.2f}","population_hash":result.population_hash})
            for x in result.individuals:
                state=";".join(f"{k}={v}" for k,v in x.resulting_state.items())
                individual.append({"case":label,"scenario":scenario.id,"member":x.member_id,"weight":x.weight,"state":state,"fixed_cost":next(m.fixed_cost for m in pop.members if m.id==x.member_id),"multiplier":next(m.cost_multiplier for m in pop.members if m.id==x.member_id),"profitable":x.profitable,"adopted":x.adopted,"gain":x.adjusted_gain,"action":x.best_action.name if x.best_action else ""})
            if scenario.id=="B0":
                for x,m in zip(result.individuals,pop.members): cells.append({"case":label,"member":x.member_id,"state":json.dumps(norm(m.state),sort_keys=True),"fixed_cost":m.fixed_cost,"multiplier":m.cost_multiplier,"profitable":x.profitable,"gain":x.adjusted_gain})
    write_csv(OUT/"tables"/"population_summary.csv",rows); write_csv(OUT/"tables"/"robustness_cells.csv",cells); write_csv(OUT/"tables"/"individual_results.csv",individual)
    write_csv(OUT/"tables"/"table1_robustness_by_fixture.csv",rows)
    write_csv(OUT/"tables"/"table2_manipulation_cost_sensitivity.csv",[x for x in cells if x["case"] in ("scholarship","procurement")])
    write_csv(OUT/"tables"/"table3_hard_cutoff_vs_phase_out.csv",[x for x in rows if x["case"] in ("scholarship","phase_out")])

    # Frozen weighted scholarship population.
    incomes=(499999,500000,500001,500005,500010); weights=(.1,.2,.3,.2,.2); costs=(0,1,10,100,1000)
    members=tuple(AgentType(f"type-{i+1}",D(str(w)),{"true_income":D(x),"reported_income":D(x)},fixed_cost=D(c)) for i,(x,w,c) in enumerate(zip(incomes,weights,costs)))
    wp=PopulationSpecification("weighted-scholarship",members); ss=load_spec(ROOT/"examples/scholarship_cliff.yaml"); acts={"reduce_work":{"amount":tuple(range(21))}}
    exact=evaluate_population(ss,wp,SCENARIOS[0],acts,"M4-weighted-exact")
    weighted=[{"member":x.member_id,"weight":x.weight,"income":m.state["true_income"],"fixed_cost":m.fixed_cost,"profitable":x.profitable,"adopted":x.adopted,"gain":x.adjusted_gain} for x,m in zip(exact.individuals,members)]
    write_csv(OUT/"tables"/"weighted_population.csv",weighted)
    write_csv(OUT/"tables"/"table4_weighted_population.csv",weighted)
    mc=[]
    for n in (100,1000,5000):
        sample=sample_weighted(wp,n,20260926); r=evaluate_population(ss,sample,SCENARIOS[0],acts,f"M4-MC-{n}")
        successes=sum(x.profitable for x in r.individuals); lo,hi=wilson_interval(successes,n)
        mc.append({"n":n,"seed":20260926,"profitable_share":r.summary.profitable_share,"exact_share":exact.summary.profitable_share,"error":r.summary.profitable_share-exact.summary.profitable_share,"wilson_low":lo,"wilson_high":hi,"sample_hash":population_hash(sample)})
    write_csv(OUT/"tables"/"monte_carlo.csv",mc)
    write_csv(OUT/"tables"/"table5_monte_carlo_convergence.csv",mc)
    write_csv(OUT/"tables"/"table6_negative_controls.csv",[x for x in rows if x["case"] in ("phase_out","honest")])

    # Per-state break-even is one unit above the maximum raw gain; tested-grid disappearance is separately recorded.
    breaks=[]
    for income in range(499995,500011):
        p=PopulationSpecification("one",(AgentType("x",D(1),{"true_income":D(income),"reported_income":D(income)}),))
        r=evaluate_population(ss,p,SCENARIOS[0],acts).individuals[0]
        tested=next((c for c in FIXED if D(c)>=r.adjusted_gain),None)
        breaks.append({"income":income,"raw_max_gain":r.adjusted_gain,"exact_eliminating_fixed_cost":max(D(0),r.adjusted_gain),"minimum_tested_eliminating_fixed_cost":tested if tested is not None else "not_in_grid"})
    write_csv(OUT/"tables"/"break_even.csv",breaks)

    hold=[]
    for income in range(500006,500011):
        p=PopulationSpecification("hold",(AgentType("x",D(1),{"true_income":D(income),"reported_income":D(income)}),))
        r=evaluate_population(ss,p,SCENARIOS[0],acts).individuals[0]
        hold.append({"income":income,"best_amount":r.best_action.controls["amount"],"gain":r.adjusted_gain,"profitable":r.profitable})
    write_csv(OUT/"tables"/"holdout.csv",hold)

    def dec(values): return tuple(D(str(v)) for v in values)
    formal=[]
    for label,fixture,action,states,controls in (
        ("scholarship-boundary","scholarship_cliff","reduce_work",{"true_income":[500000,500001],"reported_income":[500000,500001]},{"amount":[0,1,2]}),
        ("honest-negative-control","honest_reporting_control","misreport",{"true_income":[10,11,12],"reported_income":[10,11,12]},{"amount":range(4)})):
        sp=load_spec(ROOT/"examples"/f"{fixture}.yaml")
        domain=FormalDomain({k:dec(v) for k,v in states.items()},{k:dec(v) for k,v in controls.items()})
        result=FormalVerifier(sp,domain,5000).verify_no_profitable_deviation(action)
        formal.append({"check":label,"status":result.status.value,"witness_replay":result.witness.runtime_replay if result.witness else "n/a","message":result.message})
    write_csv(OUT/"tables"/"formal_spot_checks.csv",formal)

    # Compact SVGs generated from the evidence (not decorative smoothing).
    def svg(path,title,lines):
        text=''.join(f'<text x="20" y="{55+i*22}" font-family="monospace" font-size="14">{line}</text>' for i,line in enumerate(lines))
        path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{90+22*len(lines)}"><rect width="100%" height="100%" fill="white"/><text x="20" y="28" font-family="sans-serif" font-size="20" font-weight="bold">{title}</text>{text}</svg>',encoding="utf-8")
    svg(OUT/"figures"/"scenario_summary.svg","M4 scenario summaries",[f"{r['case']:12} {r['scenario']} profitable={r['profitable_share']} response={r['response_share']} max={r['max_gain']}" for r in rows])
    svg(OUT/"figures"/"monte_carlo.svg","Seeded Monte Carlo convergence",[f"N={r['n']:5} estimate={r['profitable_share']} exact={r['exact_share']} error={r['error']} CI=[{r['wilson_low']:.4f},{r['wilson_high']:.4f}]" for r in mc])
    svg(OUT/"figures"/"holdout.svg","Scholarship holdout 500006-500010",[f"income={r['income']} best amount={r['best_amount']} gain={r['gain']} profitable={r['profitable']}" for r in hold])

    commit=subprocess.run(["git","-c",f"safe.directory={ROOT.as_posix()}","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True).stdout.strip()
    manifest={"milestone":"M4","precommit":"research/M4_PRECOMMITMENT.md","engine_commit":commit,"seed":20260926,"cases":list(CASES),"scenarios":[norm(asdict(x)) for x in SCENARIOS],"weighted_exact":norm(asdict(exact.summary)),"files":sorted(str(p.relative_to(ROOT)) for p in OUT.rglob("*") if p.is_file())}
    (OUT/"runs"/"run_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (OUT/"runs"/"summary.json").write_text(json.dumps({"population_rows":norm(rows),"weighted_exact":norm(asdict(exact.summary)),"monte_carlo":norm(mc),"holdout":norm(hold)},indent=2),encoding="utf-8")
    (OUT/"configs"/"registered_design.json").write_text(json.dumps({"fixed_costs":FIXED,"seed":20260926,"sample_sizes":[100,1000,5000],"candidate_limit":3,"hurdle":"100"},indent=2),encoding="utf-8")

if __name__=="__main__": main()
