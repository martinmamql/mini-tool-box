import shlex
import subprocess
import tempfile
from io import StringIO

import pandas as pd


def run(command_str: str) -> tuple[int, str, str]:
    """Execute a shell command."""
    command = shlex.split(command_str)

    # use tempfile to overcome the buffer limit
    stdout = tempfile.TemporaryFile(buffering=0)
    stderr = tempfile.TemporaryFile(buffering=0)

    process = subprocess.Popen(
        command, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL
    )
    process.wait()

    stdout.seek(0)
    out = "".join([line.decode() for line in stdout.readlines()])

    stderr.seek(0)
    err = "".join([line.decode() for line in stderr.readlines()])

    return process.returncode, out, err


def get_resources() -> pd.DataFrame:
    """Return a dataframe containing the resources per node."""
    # query sinfo
    returncode, stdout, stderr = run(
        'sinfo -o "%20N | %.5a | %8c | %10m | %50G  | %t" -N'
    )
    assert returncode == 0, stderr

    # convet to dataframe
    data = pd.read_csv(StringIO(stdout), sep="|", skipinitialspace=True)

    # convert to strings
    data.columns = data.columns.str.strip()
    for name in ("NODELIST", "AVAIL", "GRES", "STATE"):
        data[name] = data[name].astype(str).str.strip()

    # remove nodes that are not available
    index = (
        (data["AVAIL"] == "up")
        & ~data["STATE"].str.startswith("down")
        & ~data["STATE"].str.startswith("drain")
    )
    print("Not-up nodes")
    print(data.loc[~index, ["NODELIST", "GRES", "STATE"]].groupby("NODELIST").first())
    print()
    data = data.loc[index, :]

    # count nodes that are in multiple partitions only one time
    data = data.drop_duplicates(subset=("NODELIST"))

    # parse GPUs
    data.loc[data["GRES"] == "(null)", "GRES"] = "0"
    data["GRES"] = (
        data["GRES"]
        .astype(str)
        .apply(lambda xs: sum([int(x.split(":")[-1]) for x in xs.split(",")]))
    )

    return data.set_index("NODELIST").drop(columns=["AVAIL", "STATE"])


def get_usage() -> pd.DataFrame:
    """Return a dataframe containing the used resources per node."""
    # query sacct
    returncode, stdout, stderr = run(
        'sacct -P -sr -a --format="Jobid,NodeList,AllocCPUS,AllocGRES,ReqMem" --units=M'
    )
    assert returncode == 0, stderr

    # convert to dataframe
    data = pd.read_csv(StringIO(stdout), sep="|", dtype=str).fillna(0)
    data.columns = (
        data.columns.str.upper()
        .str.replace("ALLOC", "")
        .str.replace("REQMEM", "MEMORY")
    )

    # remove lost jobs
    stdout = run("sacctmgr show runaway")[1]
    lost_jobs = [line.split(" ", 1)[0] for line in stdout.split("-\n")[-1].split("\n")]
    lost_jobs = [x for x in lost_jobs if x.strip()]
    data = data.loc[~data["JOBID"].isin(lost_jobs)]

    # remove job steps
    data = data.loc[~data["JOBID"].apply(lambda x: "." in x)].drop(columns=["JOBID"])

    # parse GPUs
    data["GRES"] = (
        data["GRES"]
        .astype(str)
        .apply(lambda x: x.split(":", 1)[1] if ":" in x else "0")
        .astype(int)
    )

    # parse memory
    data["MEMORY"] = data["MEMORY"].apply(lambda x: int(x[:-2]))
    data["CPUS"] = data["CPUS"].astype(int)
    return data.groupby("NODELIST").sum()


if __name__ == "__main__":
    resources = get_resources()
    print("Existing number of GPUs:", resources["GRES"].sum())

    used = get_usage()
    print("Number of used GPUs:", used["GRES"].sum())

    print("Available resources per node:")
    print(resources.subtract(used, fill_value=0).astype(int))
