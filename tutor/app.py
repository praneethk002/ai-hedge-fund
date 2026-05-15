from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from llm_router import get_llm_response

load_dotenv()

WELCOME_MESSAGE = (
    "Welcome! I'm Aswath Damodaran — Professor of Finance at NYU Stern and, some would say,\n"
    "a valuation obsessive. I've spent decades arguing that valuation is as much about\n"
    "storytelling as it is about spreadsheets.\n\n"
    "What would you like to learn today? You can ask me about DCF models, cost of capital,\n"
    "relative valuation, how to value a startup — or challenge me on anything you've read.\n\n"
    "If you're not sure where to start, try: 'How do you value a company from scratch?'"
)

PROVIDER_LABELS = {
    "OpenAI": "openai",
    "Anthropic": "anthropic",
    "Groq (Free)": "groq",
    "Offline Mode": "mock",
}

SHORTCUTS = [
    "Explain DCF from scratch",
    "What is WACC?",
    "How do I value a startup?",
    "Explain terminal value",
    "What's the difference between FCFF and FCFE?",
    "Teach me beta",
]


def init_state() -> None:
    st.session_state.setdefault("chat_history", [{"role": "assistant", "content": WELCOME_MESSAGE}])
    st.session_state.setdefault("provider", "mock")
    st.session_state.setdefault("api_key", "")


def add_and_respond(user_text: str, provider: str, api_key: str) -> None:
    st.session_state.chat_history.append({"role": "user", "content": user_text})
    context_messages = st.session_state.chat_history[-20:]
    with st.spinner("Professor Damodaran is thinking..."):
        try:
            response_text = get_llm_response(
                messages=context_messages,
                provider=provider,
                api_key=api_key,
            )
        except Exception:
            st.error(
                "I hit an API issue while responding. Double-check your key, then try again. "
                "If needed, switch to Groq's free tier from the sidebar."
            )
            return
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})


def main() -> None:
    st.set_page_config(page_title="Professor Damodaran Tutor", page_icon="🎓", layout="centered")
    init_state()

    with st.sidebar:
        st.header("🎓 Professor Damodaran")
        st.caption("Your AI Valuation Tutor")

        provider_label = st.selectbox("LLM Provider", list(PROVIDER_LABELS.keys()))
        provider = PROVIDER_LABELS[provider_label]
        st.session_state.provider = provider

        if provider != "mock":
            st.session_state.api_key = st.text_input(
                "API Key", type="password", value=st.session_state.api_key
            )

        st.markdown("[Get Groq free key → groq.com](https://groq.com)")
        st.divider()

        st.subheader("📚 Topic Shortcuts")
        for question in SHORTCUTS:
            if st.button(question, use_container_width=True):
                add_and_respond(question, st.session_state.provider, st.session_state.api_key)

        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.chat_history = [{"role": "assistant", "content": WELCOME_MESSAGE}]
            st.rerun()

    st.title("Chat with Professor Damodaran")
    st.caption("Ask me anything about valuation, cost of capital, or financial modeling")

    for message in st.session_state.chat_history:
        avatar = "🎓" if message["role"] == "assistant" else "🧑‍🎓"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask Professor Damodaran...")
    if prompt:
        add_and_respond(prompt, st.session_state.provider, st.session_state.api_key)
        st.rerun()


if __name__ == "__main__":
    main()
