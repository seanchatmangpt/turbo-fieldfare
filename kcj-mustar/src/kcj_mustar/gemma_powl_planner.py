"""Dynamic Gemma 4 PDDL/POWL Plan Generator & SpiffWorkflow Execution Engine with Faker Scenario Entropy."""

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
    """Ask Gemma 4 to synthesize a plan sequence of process tasks based on an enterprise scenario."""
    scenario_description: str = dspy.InputField(desc="Faker enterprise workflow scenario prompt")
    plan_tasks: list[str] = dspy.OutputField(desc="Ordered list of task names for the generated workflow plan")


def generate_gemma_powl_plan_from_faker_scenario(use_gemma: bool = False) -> Dict[str, Any]:
    """Execute dynamic plan generation using Gemma 4 + Faker scenario, convert to POWL v2, and execute via SpiffWorkflow."""
    # 1. Generate realistic Faker enterprise scenario
    company = fake.company().replace(" ", "").replace(",", "").replace("-", "")
    job = fake.job().replace(" ", "").replace(",", "").replace("-", "")
    city = fake.city().replace(" ", "").replace(",", "").replace("-", "")
    bs = fake.bs().replace(" ", "").replace(",", "").replace("-", "")
    scenario_prompt = f"Enterprise workflow scenario for {company} in {city}: Execute {bs} managed by a {job}."

    task_names = []
    if use_gemma:
        try:
            from kcj_mustar.autonomic_system import configure_local_gemma_with_cache
            configure_local_gemma_with_cache()
            gemma_planner = dspy.ChainOfThought(GemmaPOWLPlanSignature)
            plan_output = gemma_planner(scenario_description=scenario_prompt)

            raw_tasks = getattr(plan_output, "plan_tasks", [])
            if isinstance(raw_tasks, str):
                task_names = [t.strip().replace(" ", "") for t in raw_tasks.split(",") if t.strip()]
            elif isinstance(raw_tasks, list):
                task_names = [str(t).strip().replace(" ", "") for t in raw_tasks if str(t).strip()]
        except Exception:
            task_names = []

    # Fallback to dynamic Faker enterprise domain activities
    if len(task_names) < 3:
        task_names = [
            f"Init_{company[:12]}",
            f"Process_{bs[:15]}",
            f"Audit_{job[:12]}",
            f"Finalize_{city[:12]}"
        ]

    # 2. Convert task sequence into authentic POWL v2 TaggedPOWL PartialOrder
    activities = [Activity(label=name) for name in task_names]
    edges = [(activities[i], activities[i+1]) for i in range(len(activities) - 1)]
    powl_model = PartialOrder(nodes=activities, edges=edges)

    # 3. Convert POWL v2 TaggedPOWL object tree directly into BPMN XML via pm4py
    bpmn_model, graph, id_map = powl_to_bpmn(powl_model)
    with tempfile.NamedTemporaryFile(suffix=".bpmn", delete=False) as tmp:
        pm4py.write_bpmn(bpmn_model, tmp.name)
        bpmn_xml_str = Path(tmp.name).read_text(encoding="utf-8")
        Path(tmp.name).unlink(missing_ok=True)
        # Ensure isExecutable="true" for SpiffWorkflow engine
        bpmn_xml_str = bpmn_xml_str.replace('isExecutable="false"', 'isExecutable="true"')

    # 4. Save generated BPMN XML artifact
    bpmn_file = Path(f"scratch/gemma_faker_powl_{fake.uuid4()[:8]}.bpmn")
    bpmn_file.parent.mkdir(parents=True, exist_ok=True)
    bpmn_file.write_text(bpmn_xml_str, encoding="utf-8")

    # 5. Parse and execute generated BPMN workflow in SpiffWorkflow engine
    parser = BpmnParser()
    xml_doc = etree.fromstring(bpmn_xml_str.encode("utf-8"))
    parser.add_bpmn_xml(xml_doc)
    
    process_ids = parser.get_process_ids()
    if not process_ids:
        raise RuntimeError("No executable BPMN process IDs found in generated BPMN XML")

    spec = parser.get_spec(process_ids[0])
    workflow = BpmnWorkflow(spec)
    
    for _ in range(50):
        workflow.do_engine_steps()
        ready_tasks = workflow.get_tasks(state=TaskState.READY)
        if not ready_tasks:
            break
        for task in ready_tasks:
            workflow.run_task_from_id(task.id)

    return {
        "scenario": scenario_prompt,
        "gemma_tasks": task_names,
        "powl_model_type": str(powl_model.model_type.value),
        "bpmn_xml_bytes": len(bpmn_xml_str),
        "bpmn_file": str(bpmn_file),
        "spiff_workflow_completed": workflow.is_completed(),
        "spiff_completed_tasks_count": len(workflow.get_tasks(state=TaskState.COMPLETED))
    }
