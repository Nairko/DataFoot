"""Interface Streamlit de conversation avec DataFootLLM et le MCP local."""

import asyncio
import os

import streamlit as st


def _run_question(question: str, api_key: str | None) -> str:
    """Appeler le client OpenAI asynchrone depuis Streamlit."""
    # Import différé : les autres onglets restent utilisables même si la
    # dépendance OpenAI n'est pas encore installée.
    from datafoot_mcp.openai_client import ask_openai

    return asyncio.run(ask_openai(question, api_key=api_key))


def createPage() -> None:
    """Afficher l'onglet DataFoot Agent."""
    st.title("DataFoot Agent ⚽🤖")
    st.caption("Ask questions about players, statistics and DataFoot profiles.")

    if "datafoot_agent_messages" not in st.session_state:
        st.session_state.datafoot_agent_messages = []

    with st.sidebar:
        st.subheader("Configuration")
        api_key_input = st.text_input(
            "OpenAI API key",
            value=st.session_state.get("datafoot_api_key", ""),
            type="password",
            help="The key is stored only in the current Streamlit session.",
            key="datafoot_api_key_input",
        )
        st.session_state.datafoot_api_key = api_key_input.strip()

        if not api_key_input and not os.environ.get("OPENAI_API_KEY"):
            st.info("Enter an API key to enable the agent.")

        if st.button("Clear conversation", key="datafoot_agent_clear"):
            st.session_state.datafoot_agent_messages = []
            st.rerun()

    for message in st.session_state.datafoot_agent_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Example: Which players are similar to Pedri?")
    if not question:
        return

    st.session_state.datafoot_agent_messages.append(
        {"role": "user", "content": question}
    )
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Running DataFoot analysis..."):
            try:
                answer = _run_question(
                    question,
                    st.session_state.get("datafoot_api_key") or None,
                )
            except Exception as error:
                answer = f"Analysis error: {error}"
        st.markdown(answer)

    st.session_state.datafoot_agent_messages.append(
        {"role": "assistant", "content": answer}
    )
