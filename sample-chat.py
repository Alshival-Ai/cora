"""Example showing how to kick off a text (SMS) chat with Cora helpers."""

import cora


def build_assistant(connector: cora.VapiConnector, *, first_message: str):
    """Provision a simple assistant that we'll text with."""
    voice = cora.openai_voices.nova
    transcriber = cora.deepgram_transcribers.custom(lang="en")
    plan = cora.pass_fail_plan()

    return cora.create_assistant(
        name="demo-chat",
        system_prompt="You are a helpful scheduling assistant.",
        voice=voice,
        transcriber=transcriber,
        analysis_plan=plan,
        first_message=first_message,
        connector=connector,
    )


def choose_phone_number(connector: cora.VapiConnector) -> str:
    """Pick the first SMS-capable phone number from the account."""
    numbers = cora.list_phone_numbers(connector=connector)
    if not numbers:
        raise RuntimeError("No phone numbers available; provision one in Vapi first.")
    return numbers[0].id


def send_sms_chat(
    connector: cora.VapiConnector,
    *,
    assistant_id: str,
    phone_number_id: str,
    customer_number: str,
    message: str,
    use_llm_generated_message_for_outbound: bool = False,
):
    """Kick off a chat via SMS using the provided message text."""
    return cora.chat(
        assistant_id=assistant_id,
        phone_number_id=phone_number_id,
        customer=customer_number,
        message=message,
        use_llm_generated_message_for_outbound=use_llm_generated_message_for_outbound,
        v=connector,
    )


def main():
    test_phone_number = "+1 (956) 670-7155"  # Replace with your own phone number for testing
    initial_message = "Hi! Just checking in about your upcoming appointment."
    connector = cora.VapiConnector()

    assistant = build_assistant(connector, first_message=initial_message)
    phone_number_id = choose_phone_number(connector)
    chat = send_sms_chat(
        connector,
        assistant_id=assistant.id,
        phone_number_id=phone_number_id,
        customer_number=test_phone_number,
        message=initial_message,
        use_llm_generated_message_for_outbound=False,
    )

    print("Chat created:", chat.id)
    print("Status:", getattr(chat, "status", "unknown"))
    last_message = getattr(chat, "messages", None) or []
    if last_message:
        print("Latest message:", last_message[-1])

    # Clean up the assistant after the demo
    connector.assistants.delete(assistant.id)


if __name__ == "__main__":
    main()
