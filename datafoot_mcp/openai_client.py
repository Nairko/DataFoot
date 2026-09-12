"""Pont entre l'API OpenAI et le serveur MCP DataFoot local."""

import asyncio
import json
import os
import unicodedata
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SERVER = PROJECT_ROOT / "datafoot_mcp" / "server.py"


def _value(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _openai_tools(mcp_tools: list[Any]) -> list[dict[str, Any]]:
    """Convertir les schemas MCP au format function tools OpenAI."""
    return [
        {
            "type": "function",
            "function": {
                "name": _value(tool, "name"),
                "description": _value(tool, "description", ""),
                "parameters": _value(
                    tool,
                    "input_schema",
                    {"type": "object", "properties": {}},
                ),
            },
        }
        for tool in mcp_tools
    ]


def _result_text(result: Any) -> str:
    structured = getattr(result, "structured_content", None)
    if structured:
        return json.dumps(structured, ensure_ascii=False, default=str)
    content = getattr(result, "content", None) or []
    parts = [getattr(item, "text", str(item)) for item in content]
    return "\n".join(parts) if parts else json.dumps(result, default=str)


def _server_parameters() -> StdioServerParameters:
    return StdioServerParameters(
        command=os.environ.get("DATAFOOT_PYTHON", "python"),
        args=[str(DEFAULT_SERVER)],
        cwd=str(PROJECT_ROOT),
        env=dict(os.environ),
    )


def _requested_tool_names(question: str) -> set[str]:
    """Identifier les outils explicitement demandés, sans choisir leurs arguments."""
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFD", question.lower())
        if unicodedata.category(char) != "Mn"
    )
    requested = set()
    if "percentile" in normalized:
        requested.add("get_player_percentiles")
    if "similaire" in normalized or "ressembl" in normalized:
        requested.add("find_similar_players")
    if "complement" in normalized:
        requested.add("find_complementary_players")
    if "compare" in normalized or "compar" in normalized:
        requested.add("compare_players")
    return requested


def _assistant_message_dict(message: Any) -> dict[str, Any]:
    if hasattr(message, "model_dump"):
        data = message.model_dump(exclude_none=True)
    else:
        data = dict(message)
    # Chat Completions attend le role assistant, même si le SDK l'a déjà fourni.
    data["role"] = "assistant"
    return data


async def ask_openai(
    question: str,
    model: str | None = None,
    max_rounds: int = 3,
    api_key: str | None = None,
) -> str:
    """Envoyer une question à OpenAI et exécuter les outils MCP demandés."""
    selected_api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not selected_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Enter your API key in the DataFoot Agent tab."
        )

    selected_model = model or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(api_key=selected_api_key)
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Tu es DataFootLLM, un assistant d'analyse footballistique. "
                "Pour toute question sur les joueurs, postes, compétitions, "
                "âges ou statistiques, utilise d'abord un ou plusieurs outils "
                "MCP appropriés. Pour une demande combinée, appelle tous les "
                "outils nécessaires. Réponds en français et n'invente aucune "
                "donnée. Les résultats MCP sont la source de vérité. Si une "
                "équipe est précisée, transmets-la au paramètre team de l'outil."
            ),
        },
        {"role": "user", "content": question},
    ]

    async with Client(_server_parameters()) as mcp_client:
        listed = await mcp_client.list_tools()
        tools = _openai_tools(getattr(listed, "tools", listed))
        requested_tools = _requested_tool_names(question)
        called_tools: set[str] = set()

        for _ in range(max_rounds):
            missing_tools = requested_tools - called_tools
            if missing_tools:
                if len(missing_tools) == 1:
                    tool_choice = {
                        "type": "function",
                        "function": {"name": next(iter(missing_tools))},
                    }
                else:
                    tool_choice = "required"
            else:
                tool_choice = "auto"
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=selected_model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                parallel_tool_calls=True,
                temperature=0.1,
                max_tokens=1024,
            )
            message = response.choices[0].message
            calls = message.tool_calls or []
            if not calls:
                return message.content or "OpenAI n'a pas retourné de texte."

            messages.append(_assistant_message_dict(message))
            for call in calls:
                function = call.function
                arguments = json.loads(function.arguments or "{}")
                # Une demande combinée doit rester dans le même périmètre de
                # données. Sinon l'outil similarité peut utiliser Big5 tandis
                # que complémentarité retombe sur son défaut Liga.
                if "dataset" not in arguments:
                    if function.name in {"find_similar_players", "get_player_percentiles"}:
                        arguments["dataset"] = "Big5"
                    elif function.name == "find_complementary_players" and "find_similar_players" in requested_tools:
                        arguments["dataset"] = "Big5"
                result = await mcp_client.call_tool(function.name, arguments)
                called_tools.add(function.name)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": _result_text(result),
                    }
                )

    raise RuntimeError("OpenAI a dépassé le nombre maximal de tours d'outils.")
