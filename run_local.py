"""Run the Tutor, Quiz Creator, and Evaluator in one local uAgents Bureau."""

import os
from pathlib import Path

from uagents import Bureau
from uagents.crypto import Identity


ROOT = Path(__file__).resolve().parent
LOCAL_SEEDS = {
    "TUTOR": "study-partners-local-tutor-v1",
    "QUIZ": "study-partners-local-quiz-v1",
    "EVALUATOR": "study-partners-local-evaluator-v1",
}


def load_dotenv(path: Path):
    """Load this project's simple KEY=VALUE file without another dependency."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def configure_local_identities():
    for role, default_seed in LOCAL_SEEDS.items():
        seed_key = f"{role}_AGENT_SEED"
        seed = os.getenv(seed_key, default_seed)
        os.environ[seed_key] = seed
        os.environ[f"{role}_AGENT_ADDRESS"] = Identity.from_seed(seed, 0).address


load_dotenv(ROOT / ".env")
configure_local_identities()

# Imports must happen after environment setup because each module reads its
# peer addresses and seed during initialization.
from evaluator_agent import agent as evaluator_agent
from quiz_creator_agent import agent as quiz_agent
from tutor_agent import agent as tutor_agent


def main():
    if os.getenv("ASI_API_KEY", "").startswith("replace_"):
        print(
            "WARNING: ASI_API_KEY is still a placeholder. The agents will start, "
            "but lesson generation requires a new ASI:One key."
        )

    print("Starting Study Partners locally at http://127.0.0.1:8000")
    print(f"Tutor:        {tutor_agent.address}")
    print(f"Quiz Creator: {quiz_agent.address}")
    print(f"Evaluator:    {evaluator_agent.address}")

    bureau = Bureau(
        agents=[tutor_agent, quiz_agent, evaluator_agent],
        port=8000,
        endpoint="http://127.0.0.1:8000/submit",
    )
    bureau.run()


if __name__ == "__main__":
    main()
