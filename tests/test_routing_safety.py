from angel_platform.webui.server import (
    asks_for_action,
    asks_for_live_unintegrated_data,
    action_guidance,
    live_data_guidance,
)


def test_action_safety_is_deterministic_and_not_claimed_executed():
    assert asks_for_action("run a PowerShell command")
    text = action_guidance("run a PowerShell command")
    assert "not executed" in text.lower()
    assert "no command was run" in text.lower()
    assert "sys chat" not in text.lower()


def test_live_data_does_not_fabricate():
    assert asks_for_live_unintegrated_data("what is the weather today?")
    text = live_data_guidance("what is the weather today?")
    assert "will not invent" in text.lower()
    assert "no live lookup was performed" in text.lower()


def test_normal_conversation_does_not_enter_action_safety():
    assert not asks_for_action("Tell me about this repository.")
    assert not asks_for_action("Is the README too long?")
    assert not asks_for_action("Explain why this script is safe.")


def test_sys_chat_words_are_not_a_special_router():
    assert not asks_for_action("Explain what Sys Chat used to mean in Angel.")
    assert not asks_for_action("Remove the Sys Chat wording from the UI.")


def test_approval_executes_only_pending_safe_diagnostic():
    from angel_platform.webui.server import action_guidance, execute_pending_approved
    text = action_guidance("check Python version")
    assert "NOT EXECUTED" in text
    result = execute_pending_approved()
    assert "VERIFIED EXECUTION RESULT" in result
    assert "Command: python --version" in result
    assert "Return code:" in result


def test_approval_without_pending_command_is_honest():
    from angel_platform.webui.server import execute_pending_approved
    assert "No pending command" in execute_pending_approved()
