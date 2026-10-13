# Agentverse Study Partners

A lightweight three-agent learning demo:

1. **Tutor** teaches a topic and coordinates the workflow.
2. **Quiz Creator** produces a validated three-question quiz.
3. **Evaluator** grades deterministically and generates helpful feedback.

The Tutor exposes the Agentverse chat protocol. Learners can send a natural
request such as `Teach me overfitting`, answer with `A, C, B`, and use the
commands `status`, `cancel`, or `help`.

## Deploy on Agentverse

Create three separate **Hosted Agents** at
[Agentverse](https://agentverse.ai). Each Hosted Agent project has its own
`agent.py`:

- Paste `tutor_agent.py` into the Tutor project's `agent.py`.
- Paste `quiz_creator_agent.py` into the Quiz Creator project's `agent.py`.
- Paste `evaluator_agent.py` into the Evaluator project's `agent.py`.

Copy the address shown by each Hosted Agent, then configure these Agent
Secrets:

### Tutor secrets

```text
ASI_API_KEY=<new ASI:One key>
ASI_MODEL=asi1
QUIZ_AGENT_ADDRESS=<Quiz Creator address>
EVALUATOR_AGENT_ADDRESS=<Evaluator address>
```

### Quiz Creator secrets

```text
ASI_API_KEY=<new ASI:One key>
ASI_MODEL=asi1
TUTOR_AGENT_ADDRESS=<Tutor address>
```

### Evaluator secrets

```text
ASI_API_KEY=<new ASI:One key>
ASI_MODEL=asi1
TUTOR_AGENT_ADDRESS=<Tutor address>
```

Run the Quiz Creator and Evaluator first, then run the Tutor. Publish the
Tutor's chat protocol/manifest and enable its Marketplace chat integration if
you want users to discover it through ASI:One.

The Tutor uses Agent Storage for mission state because Hosted Agent globals
reset between invocations. No database or external web server is required.

## Security

Store API keys only in Agentverse Agent Secrets. Never paste secrets directly
into an agent source file or commit them to Git.
