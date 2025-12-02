"""Minimal example showing how to assemble an assistant + call with cora."""

import cora


def build_assistant(connector: cora.VapiConnector):
    """Provision a sample assistant with voice, transcriber, and analysis plan."""
    voice = cora.openai_voices.nova
    transcriber = cora.deepgram_transcribers.custom(lang="en")
    plan = cora.pass_fail_plan()

    return cora.create_assistant(
        name="demo-patient",
        system_prompt="You are a helpful scheduling assistant.",
        voice=voice,
        transcriber=transcriber,
        analysis_plan=plan,
        first_message="Hi! I'm calling about your upcoming appointment.",
        connector=connector,
    )


def choose_phone_number(connector: cora.VapiConnector) -> str:
    """Pick the first phone number from the account (replace in production)."""
    numbers = cora.list_phone_numbers(connector=connector)
    if not numbers:
        raise RuntimeError("No phone numbers available; provision one in Vapi first.")
    return numbers[0].id


def start_call(connector: cora.VapiConnector, assistant_id: str, number: str, phone_number_id: str):
    """Kick off a call using the newly created assistant."""
    return cora.create_call(
        assistant_id=assistant_id,
        phone_number_id=phone_number_id,
        customer=number,
        v=connector,
    )


def watch_call(connector: cora.VapiConnector, call_id: str):
    """Stream call updates until the call reaches a terminal status."""
    print("Watching call:")
    for snapshot in cora.watch_call(connector, call_id=call_id):
        print(snapshot)


def main():
    test_phone_number = "+1 (956) 670-7155"  # Replace with your own phone number for testing
    connector = cora.VapiConnector()

    assistant = build_assistant(connector)
    phone_number_id = choose_phone_number(connector)
    call = start_call(connector, assistant.id, test_phone_number, phone_number_id)
    watch_call(connector, call.id)

    # Delete the assistant to clean up the example
    connector.assistants.delete(assistant.id)


if __name__ == "__main__":
    main()
