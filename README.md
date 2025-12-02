# Cora – Vapi Helper Toolkit

`cora` is a small helper library that wraps the Vapi Server SDK with a few pragmatic utilities for building healthcare assistants. It bundles repeatable pieces—assistant creation, transcriber/voice presets, call lifecycle helpers, and credential management—so your app logic can stay focused on patient workflows.

## Installation

```bash
pip install -e .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/Alshival-Ai/cora.git
```

The package expects a `.env` file (or exported env vars) containing at least `VAPI_API_KEY`. When `VapiConnector()` is instantiated, it loads the environment automatically.

```
VAPI_API_KEY=sk_live_your_key
```

## Quick Start

```python
import cora

v = cora.VapiConnector()  # auto-reads .env

# Build assistant resources
voice = cora.eleven_labs_voices.ana_maria
transcriber = cora.deepgram_transcribers.custom(lang="es")
analysis_plan = cora.pass_fail_plan()

assistant = cora.create_assistant(
    name="patient-123",
    system_prompt="You are a helpful care coordinator…",
    tool_ids=["mcp-tool-id", "ba39debb-885e-415b-9ed0-3e57f2642430"],
    voice=voice,
    transcriber=transcriber,
    analysis_plan=analysis_plan,
    first_message="Hola, soy Margori con Broward Health...",
    connector=v,
)
```

## Making Calls

```python
call = cora.create_call(
    assistant_id=assistant.id,
    phone_number_id="pn_abc123",
    customer="+1 (954) 320-0121",
    v=v,
)

for snapshot in cora.watch_call(v, call_id=call.id):
    print(snapshot["status"], snapshot["last_message"])

# or block until terminal:
final_call = cora.wait_for_terminal(v, call.id)
```

`TERMINAL_STATUSES` enumerates the statuses that stop polling.

## Custom Voices & Transcribers

Voices are exposed as `VoiceProfile` instances so you can either pass them directly to `create_assistant` or expand them into raw payloads when you need to tweak attributes on the fly:

```python
voice = cora.openai_voices.nova.payload(speed=1.05)  # tweak speed/model on demand
```

Transcribers follow the same pattern. You can stick with the instances (`deepgram_transcribers.english`) or build a custom profile with explicit lang/model settings:

```python
from src.transcribers import deepgram_transcribers

transcriber = deepgram_transcribers.custom(lang="es", model="nova-2").payload()
```

Passing the profile objects themselves into `create_assistant` also works—the helper calls `.payload()` internally if it detects a profile type.

## Analysis Plans

You can override both the rubric text and the evaluation messages—for example, to embed call-specific instructions or tweak the evaluator role:

```python
from src.analysis_plan import pass_fail_plan

evaluation_messages = [
    {
        "role": "system",
        "content": (
            "You are an expert call evaluator. You will be given a transcript of a call and the "
            "system prompt of the Ai participant. If the Ai successfully booked an appointment for "
            "the patient, label the call as `true`. If the patient answered but no appointment was "
            "scheduled, label the call as `false`. If a voicemail was left or the patient did not "
            "answer, label the call as `false`.\n\nRubric:\n\n{{rubric}}\n\nOnly respond with the "
            "evaluation result."
        ),
    },
    {
        "role": "user",
        "content": (
            "Here is the transcript of the call:\n\n{{transcript}}\n\n. Here is the ended reason of "
            "the call:\n\n{{endedReason}}\n\n"
        ),
    },
    {
        "role": "user",
        "content": "Here was the system prompt of the call:\n\n{{systemPrompt}}\n\n",
    },
]

analysis_plan = pass_fail_plan(
    rubric="PassFail",
    evaluation_messages=evaluation_messages,
)
```

## Credentials

`cora.VapiConnector` automatically loads `.env` from the working directory (or accepts a `token=` / `env_path=` override). The connector exposes `.assistants`, `.calls`, and `.phone_numbers` exactly like the underlying Vapi SDK, so you can drop down to raw methods whenever you need finer control.
