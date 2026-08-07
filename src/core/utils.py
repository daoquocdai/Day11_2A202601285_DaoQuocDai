"""
Lab 11 — Helper Utilities
"""
from google.genai import types


import asyncio

async def chat_with_agent(agent, runner, user_message: str, session_id=None):
    """Send a message to the agent and get the response with automatic 429 retry.

    Args:
        agent: The LlmAgent instance
        runner: The InMemoryRunner instance
        user_message: Plain text message to send
        session_id: Optional session ID to continue a conversation

    Returns:
        Tuple of (response_text, session)
    """
    user_id = "student"
    app_name = runner.app_name

    session = None
    if session_id is not None:
        try:
            session = await runner.session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
        except (ValueError, KeyError):
            pass

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_message)],
    )

    max_retries = 5
    for attempt in range(max_retries):
        try:
            if session is None:
                session = await runner.session_service.create_session(
                    app_name=app_name, user_id=user_id
                )
            final_response = ""
            async for event in runner.run_async(
                user_id=user_id, session_id=session.id, new_message=content
            ):
                if hasattr(event, "content") and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            final_response += part.text
            return final_response, session
        except Exception as e:
            session = None  # Reset session on error for next attempt
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 4
                print(f"[RateLimit/Error] Backing off for {wait_time}s (attempt {attempt+1}/{max_retries}): {e}")
                await asyncio.sleep(wait_time)
            else:
                return f"Error: {e}", None
