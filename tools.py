# Hello to the user of this computer, eligross.
### here is where the tools will live...
from pathlib import Path
import subprocess 
import shlex


### this gets the workspace root, which is the parent directory of this file. All terminal commands will be run with this as the current working directory, and all file reads and writes will be relative to this directory. This provides a sandboxed environment for the agent to operate in, preventing it from accessing or modifying files outside of its designated workspace.
WORKSPACE_ROOT = Path(__file__).resolve().parent

OVERALL_BANNED_TERMINAL_USES = {
    "rm",
    "rmdir",
    "sudo",
    "su",
    "chmod",
    "chown",
    "curl",
    "wget",
    "ssh",
    "scp",
    "shutdown",
    "reboot",
    "halt",
    "dd",
    "mkfs",
    "diskutil",
    "installer",
    "brew",
    "pip",
    "pip3",
    "npm",
    "npx",
    "yarn",
    "pnpm",
}

BANNED_SHELL_OPERATORS = ()
BANNED_TERMINAL_TOKENS = {"install", "uninstall", "upgrade", "update", "autoremove"}


def write_memory(text):
    path = Path("/Users/eligross/Desktop/local_agent_infra/agent_infra/memory/mem.md")
    with open(path, 'a') as f:
        f.write(text)


def read_memory():
    path = Path("/Users/eligross/Desktop/local_agent_infra/agent_infra/memory/mem.md")
    with open(path) as f:
        ### read the file and return the text 
        return f.read()

### general terminal use --> lots of ability

def terminal(line, timeout=30):
    try:
        args = shlex.split(line)
    except ValueError as error:
        return {"ok": False, "blocked": True, "error": f"Could not parse command: {error}"}

    if not args:
        return {"ok": False, "blocked": True, "error": "Empty command"}

    for operator in BANNED_SHELL_OPERATORS:
        if operator in line:
            return {"ok": False, "blocked": True, "error": f"Blocked shell operator: {operator}"}

    command = Path(args[0]).name
    tokens = {Path(arg).name.lower() for arg in args}
    if tokens & OVERALL_BANNED_TERMINAL_USES:
        return {"ok": False, "blocked": True, "error": f"Blocked command: {sorted(tokens & OVERALL_BANNED_TERMINAL_USES)[0]}"}
    if tokens & BANNED_TERMINAL_TOKENS:
        return {"ok": False, "blocked": True, "error": f"Blocked install/system token: {sorted(tokens & BANNED_TERMINAL_TOKENS)[0]}"}

    try:
        result = subprocess.run(
            line,
            cwd=WORKSPACE_ROOT,
            shell=True,
            executable="/bin/zsh",
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "blocked": False, "error": f"Command timed out after {timeout}s"}
    except FileNotFoundError:
        return {"ok": False, "blocked": False, "error": f"Command not found: {command}"}

    return {
        "ok": result.returncode == 0,
        "blocked": False,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


### subagent spawning capability --> call itself basically
### this agent also has to have read write power in the memory and is instiated with a goal
### this should be asynchronous and return a handle to the subagent process, which can be used to check its status, send it messages, or retrieve its results. The subagent should have the same capabilities as the main agent, but with its own separate memory and workspace. This allows for recursive problem-solving and delegation of tasks to specialized subagents when needed.
async def subagent():
    return




### This is for skill reading and writing, which is basically just file I/O in a specific directory. The agent can read its own skills and write new ones, but cannot delete or modify existing ones. This allows for a kind of self-improvement and learning over time, as it can create new skills based on its experiences and store them for future use.

def write_skill(name, content):
    path = WORKSPACE_ROOT / "skills" / f"{name}.md"
    if path.exists():
        return {"ok": False, "error": "Skill already exists"}
    with open(path, 'w') as f:
        f.write(content)
    return {"ok": True}


def get_skills():
    skills_dir = WORKSPACE_ROOT / "skills"

    return {
        "ok": True,
        "skills": [
            {
                "name": path.stem,
                "characters": path.stat().st_size,
            }
            for path in sorted(skills_dir.glob("*.md"))
        ],
    }

def read_skill(name):
    path = WORKSPACE_ROOT / "skills" / f"{name}.md"
    if not path.exists():
        return {"ok": False, "error": "Skill not found"}
    with open(path) as f:
        return {"ok": True, "content": f.read()}