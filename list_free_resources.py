import argparse
import json
import shlex
import string
import subprocess
from pathlib import Path
from typing import Any, Dict, List

FIELDS = ("GPUs", "CPUs", "Memory")


def run(command_str: str) -> str:
    """Execute a shell command."""
    command = shlex.split(command_str)

    stdout = subprocess.check_output(
        command, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
    )

    return stdout.decode()


def get_resources() -> List[Dict[str, Any]]:
    """Return a list of dicts containing the resources per node."""
    # query sinfo
    stdout = run(
        'sinfo -o \'{"node": "%N", "CPUs": %c, "Memory": %m, "GPUs": "%G", "state": "%t", "parition": "%P"}\' -N --noheader'
    )
    nodes = [json.loads(line) for line in stdout.strip("\n").split("\n")]
    nodes = sorted(nodes, key=lambda node: node["node"])
    # extract partitions
    partitions = {}
    for node in nodes:
        name = node["node"]
        if name not in partitions:
            partitions[name] = []
        parition = node["parition"]
        partitions[name].append(parition)
        del node["parition"]
    # remove duplicate lines
    nodes = [
        node
        for inode, node in enumerate(nodes)
        if node["node"] not in [_node["node"] for _node in nodes[:inode]]
    ]
    # remove offline/dead nodes
    offline = [
        node["node"] for node in nodes if node.pop("state").startswith(("d", "fail"))
    ]
    if offline:
        print("down/drain/fail:", offline)
        print()
    nodes = [node for node in nodes if node["node"] not in offline]
    # parse GPU type
    for node in nodes:
        node["GPU Type"] = []
    for line in Path("/etc/slurm/gres.conf").read_text().split("\n"):
        if line.startswith("#") or "gpu Type=" not in line:
            continue
        name = line.split("NodeName=", 1)[1].split(" ", 1)[0]
        gpu = line.split("gpu Type=", 1)[1].split(" ", 1)[0]
        for node in nodes:
            if node["node"] == name:
                node["GPU Type"].append(gpu)
                break

    # convert units
    for node in nodes:
        node["Memory"] /= 1024
        node["GPUs"] = _parse_gpu(node["GPUs"])
        node["Partitions"] = ", ".join(sorted(partitions[node["node"]]))
        node["GPU Type"] = ",".join(node["GPU Type"])
        node["weight"] = -1

    # sort by node priority
    for line in Path("/etc/slurm/local_nodenames.conf").read_text().split("\n"):
        if line.startswith("#") or "Weight=" not in line:
            continue
        name = line.split("NodeName=", 1)[1].split(" ", 1)[0]
        weight = line.split("Weight=", 1)[1].split(" ", 1)[0]
        for node in nodes:
            if node["node"] == name:
                node["weight"] = int(weight)
                break
    nodes = sorted(nodes, key=lambda node: node["weight"])
    return nodes


def _parse_gpu(gpu: str) -> int:
    if ":" not in gpu:
        return 0
    return sum([int(x.split(":")[-1]) for x in gpu.split(",")])


def get_usage(min_memory: float) -> Dict[str, int]:
    """Return a dict containing the used resources per node."""
    # query squeue
    stdout = run(
        'squeue --format=\'{"node": "%N", "GPUs": "%b", "Memory": "%m", "CPUs": %c}\' --noheader --states=running --noconvert'
    )
    jobs = [json.loads(line) for line in stdout.strip("\n").split("\n")]

    # convert units and aggregate
    usage = {}
    for job in sorted(jobs, key=lambda x: x["node"]):
        job["Memory"] = int(job["Memory"].strip("M")) / 1024
        if job["Memory"] == 0.0:  # min of the max memory per node
            job["Memory"] = min_memory
        job["GPUs"] = _parse_gpu(job["GPUs"])
        if job["node"] not in usage:
            usage[job["node"]] = {field: job[field] for field in FIELDS}
            continue
        for field in FIELDS:
            usage[job["node"]][field] += job[field]
    return usage


def print_stats(nodes: List[Dict[str, Any]]) -> None:
    header = {key: key for key in (*FIELDS, "node", "GPU Type", "Partitions")}
    for node in [header] + nodes:
        print(
            f"{node['node']:<12}{node['GPUs']:>8}{node['CPUs']:>8}{node['Memory']:>8}{node['GPU Type']:>15}{node['Partitions']:>22}"
        )


if __name__ == "__main__":
    nodes = get_resources()
    used = get_usage(min(node["Memory"] for node in nodes))

    print("Free resources")
    free = []
    for node in nodes:
        name = node["node"]
        used_node = {
            field: used[name][field] if node["node"] in used else 0 for field in FIELDS
        }

        free.append(
            {
                **{field: node[field] for field in ("node", "Partitions", "GPU Type")},
                **{
                    field: max(round(node[field] - used_node[field]), 0)
                    for field in FIELDS
                },
            }
        )
    print_stats(free)
