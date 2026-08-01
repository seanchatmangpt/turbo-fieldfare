"""Combinatorial Maximalist Gemma 4 PDDL/POWL Plan Generator & SpiffWorkflow Execution Engine with High Density Hyper-Graph Scenarios."""

import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from faker import Faker
from lxml import etree
import dspy

# Ensure ~/POWL is in sys.path
POWL_DIR = Path("/Users/sac/POWL")
if str(POWL_DIR) not in sys.path:
    sys.path.insert(0, str(POWL_DIR))

import pm4py
from powl.objects.tagged_powl import Activity, PartialOrder, TaggedPOWL
from powl.conversion.variants.to_bpmn import apply as powl_to_bpmn

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

from kcj_mustar.models import SystemConstants, AutonomicCycleResult, ExecutionStatus

fake = Faker()


class GemmaPOWLPlanSignature(dspy.Signature):
    """Ask Gemma 4 to synthesize a high-density combinatorial maximalist workflow plan."""
    scenario_description: str = dspy.InputField(desc="Combinatorial enterprise scenario prompt")
    plan_tasks: list[str] = dspy.OutputField(desc="Ordered list of task names for the generated workflow plan")


def generate_combinatorial_maximalist_powl_plan(num_stages: int = 10, workers_per_stage: int = 4) -> Dict[str, Any]:
    """Combinatorial Maximalism: Synthesize hyper-dense multi-tier POWL v2 DAG, convert to BPMN XML, and execute via SpiffWorkflow."""
    company = fake.company().replace(" ", "").replace(",", "").replace("-", "")
    domain_field = fake.bs().replace(" ", "").replace(",", "").replace("-", "")
    
    scenario_prompt = (
        f"Combinatorial Maximalist Enterprise Execution Graph for {company}: "
        f"Scale {domain_field} across {num_stages} execution stages with {workers_per_stage} parallel workers per stage."
    )

    # 1. Synthesize multi-stage hyper-dense partial order activities
    stage_nodes: List[List[Activity]] = []
    all_activities: List[Activity] = []
    
    for stage_idx in range(num_stages):
        current_stage = []
        for worker_idx in range(workers_per_stage):
            task_label = f"S{stage_idx+1}_W{worker_idx+1}_{fake.word().capitalize()}"
            act = Activity(label=task_label)
            current_stage.append(act)
            all_activities.append(act)
        stage_nodes.append(current_stage)

    # 2. Build dense inter-stage dependency edges (every node in Stage N connects to all nodes in Stage N+1)
    edges = []
    for s in range(num_stages - 1):
        for u in stage_nodes[s]:
            for v in stage_nodes[s + 1]:
                edges.append((u, v))

    # 3. Construct POWL v2 TaggedPOWL PartialOrder Object Tree
    powl_model = PartialOrder(nodes=all_activities, edges=edges)

    # 4. Convert POWL v2 TaggedPOWL object tree directly into BPMN XML via pm4py
    bpmn_model, graph, id_map = powl_to_bpmn(powl_model)
    with tempfile.NamedTemporaryFile(suffix=".bpmn", delete=False) as tmp:
        pm4py.write_bpmn(bpmn_model, tmp.name)
        bpmn_xml_str = Path(tmp.name).read_text(encoding="utf-8")
        Path(tmp.name).unlink(missing_ok=True)
        # Ensure isExecutable="true" for SpiffWorkflow engine
        bpmn_xml_str = bpmn_xml_str.replace('isExecutable="false"', 'isExecutable="true"')

    # 5. Save generated high-density BPMN XML artifact
    bpmn_file = Path(f"scratch/combinatorial_powl_max_{num_stages}x{workers_per_stage}_{fake.uuid4()[:8]}.bpmn")
    bpmn_file.parent.mkdir(parents=True, exist_ok=True)
    bpmn_file.write_text(bpmn_xml_str, encoding="utf-8")

    # 6. Parse and execute generated BPMN workflow in SpiffWorkflow engine
    parser = BpmnParser()
    xml_doc = etree.fromstring(bpmn_xml_str.encode("utf-8"))
    parser.add_bpmn_xml(xml_doc)
    
    process_ids = parser.get_process_ids()
    if not process_ids:
        raise RuntimeError("No executable BPMN process IDs found in generated BPMN XML")

    spec = parser.get_spec(process_ids[0])
    workflow = BpmnWorkflow(spec)
    
    # Run SpiffWorkflow engine loop across all parallel gateways
    for _ in range(500):
        workflow.do_engine_steps()
        ready_tasks = workflow.get_tasks(state=TaskState.READY)
        if not ready_tasks:
            break
        for task in ready_tasks:
            workflow.run_task_from_id(task.id)

    return {
        "scenario": scenario_prompt,
        "combinatorial_maximalism": {
            "total_nodes": len(all_activities),
            "total_edges": len(edges),
            "num_stages": num_stages,
            "workers_per_stage": workers_per_stage,
            "theoretical_state_space": f"2^{len(all_activities) * len(edges)}"
        },
        "powl_model_type": str(powl_model.model_type.value),
        "bpmn_xml_bytes": len(bpmn_xml_str),
        "bpmn_file": str(bpmn_file),
        "spiff_workflow_completed": workflow.is_completed(),
        "spiff_completed_tasks_count": len(workflow.get_tasks(state=TaskState.COMPLETED))
    }
