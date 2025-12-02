"""Minimal example showing how to assemble an assistant + call with cora."""

import cora


if __name__ == "__main__":
    test_phone_number = "+1 (956) 670-7155"  # Replace with your own phone number for testing

    connector = cora.VapiConnector()

    voice = cora.openai_voices.nova
    transcriber = cora.deepgram_transcribers.custom(lang="en")
    plan = cora.pass_fail_plan()

    assistant = cora.create_assistant(
        name="demo-patient",
        system_prompt="You are a helpful scheduling assistant.",
        #tool_ids=["mcp_tool_id", "ba39debb-885e-415b-9ed0-3e57f2642430"],
        voice=voice,
        transcriber=transcriber,
        analysis_plan=plan,
        first_message="Hi! I'm calling about your upcoming appointment.",
        connector=connector,
    )

    # Get a phone number ID from your account to use here

    numbers = cora.list_phone_numbers()
    for pn in numbers:
        print(pn.name, pn.id, pn.number)

    first = numbers[0]
    # You can uncomment this line to see more details about a specific phone number using its ID
    # details = cora.get_phone_number(first.id)

    call = cora.create_call(
        assistant_id=assistant.id,
        phone_number_id=first.id,
        customer=test_phone_number,
        v=connector,
    )

    print("Watching call:")
    for snapshot in cora.watch_call(connector, call_id=call.id):
        print(snapshot)

    # Delete the assistant to clean up
    connector.assistants.delete(assistant.id)
