# Cora – Vapi Helper Toolkit

`cora` is a small helper library that wraps the Vapi Server SDK with a few pragmatic utilities for building healthcare assistants. It bundles repeatable pieces—assistant creation, transcriber/voice presets, call lifecycle helpers, and credential management—so your app logic can stay focused on patient workflows.

Why does it exist? Cora is the toolkit The Data Team at [Alshival.Ai](https://alshival.ai) uses to build and maintain AI assistants across many client deployments. By keeping the integration code in this centralized repo, we stay resilient to Vapi API changes (we can patch things here before they break production bots) while sharing best practices, presets, and helpers across every project. In short, it gives us a stable foundation to manage multiple assistants without duplicating boilerplate in each app.

<div align="center">
  <img src="meta/brain2_black_with_background.png" width="35%"></img>
</div>

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

You can optionally pin other defaults via environment variables:

- `VAPI_MODEL_PROVIDER` – sets the model provider used by `cora.create_assistant` unless you pass `model_provider` explicitly (defaults to `openai`).
- `VAPI_MODEL_NAME` – sets the model ID sent to Vapi (defaults to `gpt-5.1`). Override this to `gpt-4.1`, `gpt-4o-mini`, etc., without changing code.

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

Need to inspect available numbers before placing a call? Use the phone number helpers:

```python
numbers = cora.list_phone_numbers()
for pn in numbers:
    print(pn.id, pn.number)

first = numbers[0]
details = cora.get_phone_number(first.id)
```

## Text Chats

```python
assistant = cora.create_assistant(
    name="patient-123",
    system_prompt="You are a helpful care coordinator…",
    voice=cora.openai_voices.nova,
    transcriber=cora.deepgram_transcribers.custom(lang="en"),
    analysis_plan=cora.pass_fail_plan(),
    first_message="Hi! Just checking in about your upcoming appointment.",
    connector=v,
)

# Kick off a new SMS thread (send literal text)
chat = cora.chat(
    assistant_id=assistant.id,
    phone_number_id="pn_abc123",
    customer="+1 (954) 320-0121",
    message="Hi! Just checking in about your upcoming appointment.",
    use_llm_generated_message_for_outbound=False,  # deliver message verbatim
    v=v,
)
print(chat.status, chat.id)
```

When you need the assistant/LLM to craft a response from the provided prompt (e.g., follow-up text generated from context), pass `use_llm_generated_message_for_outbound=True`. If you already know the exact text you want to deliver (most appointment reminders), keep it `False` so the string lands verbatim.

`cora.chat` wraps `vapi.chats.create` with the SMS transport boilerplate. Provide `session_id="sess_..."` instead of `phone_number_id`/`customer` when continuing an existing thread, and pass `previous_chat_id` if you want to include the last transcript as additional context for the model.

## Voices

`cora` ships with ready-to-use voices for each supported provider, and every helper lets you pass your own voice ID when you need something custom. The table below shows the available helpers and how to extend them:

| Provider    | Helper                         | Ready-to-use example                  | Custom voice options |
| ----------- | ------------------------------ | ------------------------------------- | -------------------- |
| ElevenLabs  | `cora.eleven_labs_voices`      | `cora.eleven_labs_voices.ana_maria`   | `ElevenLabs(additional_voices={"cataldo": "it-IT-CataldoNeural"})` or `cora.eleven_labs_voices.custom("<voice-id>")` |
| OpenAI      | `cora.openai_voices`           | `cora.openai_voices.nova`             | `OpenAIVoice(additional_voices={"studio": "studio-id"})` or `cora.openai_voices.custom("<voice-id>")` |
| Azure TTS   | `cora.azure_voices`            | `cora.azure_voices.ximena`            | `AzureVoice(additional_voices={"cataldo": "it-IT-CataldoNeural"})` or `cora.azure_voices.custom("<voice-id>")` |

Each attribute (including ones you add) is a `VoiceProfile`. Pass it directly to `create_assistant`, or call `.payload()` if you want to tweak values such as speed or override the model that gets sent to Vapi:

```python
import cora
from cora.voices import AzureVoice

azure = AzureVoice(additional_voices={"cataldo": "it-IT-CataldoNeural"})
voice = azure.cataldo.payload(speed=0.95)

assistant = cora.create_assistant(
    name="patient-123",
    system_prompt="You are a helpful care coordinator…",
    voice=voice,
    transcriber=cora.deepgram_transcribers.custom(lang="it"),
    connector=cora.VapiConnector(),
)

# One-off custom voice without attaching a new attribute
story_voice = cora.openai_voices.custom("narrator-prototype").payload()
```

## Transcribers

Transcribers follow the same pattern. You can stick with the canned instances (`deepgram_transcribers.english`) or build a custom profile with explicit lang/model settings:

```python
from src.transcribers import deepgram_transcribers

transcriber = deepgram_transcribers.custom(lang="es", model="nova-2").payload()
```

Passing the profile objects themselves into `create_assistant` also works—the helper calls `.payload()` internally if it detects a profile type.

## Analysis Plans

Vapi’s `AnalysisPlan` object can orchestrate several types of post-call insights in one pass. Each section can be turned on/off independently:

| Plan field | Purpose | Output location |
| ---------- | ------- | --------------- |
| `summary_plan` | Generate a natural-language recap of the conversation using customizable messages (defaults to Vapi’s expert note taker prompt). | `call.analysis.summary` |
| `structured_data_plan` | Run a single JSON-schema extraction to capture form-like data from the transcript. | `call.analysis.structuredData` |
| `structured_data_multi_plan` | Provide a catalog of named structured data plans if you need multiple schemas in one run. | `call.analysis.structuredDataMulti` |
| `success_evaluation_plan` | Score the call against a rubric (Pass/Fail, NumericScale, Checklist, etc.). | `call.analysis.successEvaluation` |
| `outcome_ids` | Ask Vapi to calculate stored outcomes (configured separately in the Vapi dashboard). | `call.analysis.outcomes` |

### cora.analysis_plan helpers

To keep things ergonomic, `cora.analysis_plan` exposes helpers that wrap the raw Vapi SDK types:

| Helper | What it configures | When to use it |
| ------ | ------------------ | -------------- |
| `summary_plan()` | Sets `summary_plan` only, inheriting Vapi’s default summarizer messages unless you override them. | You just want a post-call recap. |
| `structured_data_plan(schema=...)` | Enables a single JSON-schema extraction. Accepts either a `JsonSchema` instance or a plain dict. | You need one structured payload, e.g., symptoms reported. |
| `structured_data_multi_plan({...})` | Runs multiple named structured data extractions in the same call. | You need multiple schemas (e.g., vitals + insurance info). |
| `pass_fail_plan()` | Convenience around our appointment-booking rubric; forwards extra knobs to `SuccessEvaluationPlan`. | Default behavior referenced in the quick-start samples. |
| `success_evaluation_plan()` | Generic rubric-based evaluation (Pass/Fail, Checklist, NumericScale, etc.) with customizable prompts. | You want call scoring but with your own rubric/instructions. |

Every helper returns an `AnalysisPlan`, so you can pass the result directly to `cora.create_assistant`. If you want to combine multiple sections, build a small wrapper that merges fields or instantiate `AnalysisPlan` manually, as shown below.

Example: enable just a custom summary with a two-message prompt.

```python
from cora.analysis_plan import summary_plan

analysis_plan = summary_plan(
    messages=[
        {
            "role": "system",
            "content": "You are a care coordinator summarizing adherence concerns in 2 sentences.",
        },
        {
            "role": "user",
            "content": "Transcript:\n\n{{transcript}}\n\nEnded Reason: {{endedReason}}",
        },
    ]
)
```

Example: capture structured data with a dict schema (no manual `JsonSchema` import needed).

```python
from cora.analysis_plan import structured_data_plan

analysis_plan = structured_data_plan(
    schema={
        "type": "object",
        "description": "Capture vital signs reported during the call.",
        "properties": {
            "systolic": {"type": "integer"},
            "diastolic": {"type": "integer"},
            "pulse": {"type": "integer"},
        },
        "required": ["systolic", "diastolic"],
    }
)
```

We ship a helper for the most common case—pass/fail evaluations:

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

Need a different rubric but don’t want the custom booking prompt? Use the general-purpose helper:

```python
from cora.analysis_plan import success_evaluation_plan

analysis_plan = success_evaluation_plan(rubric="Checklist")
```

Need something richer? You can build an `AnalysisPlan` directly with the server SDK types. The snippet below enables (a) a custom summary prompt, (b) a structured JSON extraction, and (c) a checklist-style evaluation—all based on the [Vapi `AnalysisPlan` schema](https://github.com/VapiAI/server-sdk-python/blob/main/src/vapi/types/analysis_plan.py):

```python
from vapi.types.analysis_plan import AnalysisPlan
from vapi.types.summary_plan import SummaryPlan
from vapi.types.structured_data_plan import StructuredDataPlan
from vapi.types.json_schema import JsonSchema
from vapi.types.success_evaluation_plan import SuccessEvaluationPlan

analysis_plan = AnalysisPlan(
    summary_plan=SummaryPlan(
        enabled=True,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a discharge nurse. Summarize what the patient confirmed "
                    "about pain, meds, and follow-ups in 2 short sentences."
                ),
            },
            {
                "role": "user",
                "content": "Transcript:\\n\\n{{transcript}}\\n\\nEnded reason: {{endedReason}}",
            },
        ],
    ),
    structured_data_plan=StructuredDataPlan(
        enabled=True,
        schema_=JsonSchema(
            type="object",
            description="Capture medication adherence details",
            properties={
                "medication_taken": {
                    "type": "boolean",
                    "description": "Did the patient confirm taking the prescribed medication?",
                },
                "side_effects": {
                    "type": "string",
                    "description": "Any side effects mentioned by the patient.",
                },
            },
            required=["medication_taken"],
        ),
    ),
    success_evaluation_plan=SuccessEvaluationPlan(
        rubric="Checklist",  # also supports NumericScale, DescriptiveScale, Matrix, PassFail, etc.
    ),
)
```

Pass the resulting `analysis_plan` into `create_assistant` exactly like the helper output. Each section will run once the call meets the default `min_messages_threshold` (2 messages) unless you override it.

## Credentials

`cora.VapiConnector` automatically loads `.env` from the working directory (or accepts a `token=` / `env_path=` override). The connector exposes `.assistants`, `.calls`, `.chats`, and `.phone_numbers` exactly like the underlying Vapi SDK, so you can drop down to raw methods whenever you need finer control.
