"""Pont entre Ollama et le serveur MCP DataFoot."""

import asyncio
import json
import os
import sys
import re
import unicodedata
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SERVER = PROJECT_ROOT / "datafoot_mcp" / "server.py"


def _value(obj: Any, key: str, default: Any = None) -> Any:
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def _ollama_tools(mcp_tools: list[Any]) -> list[dict[str, Any]]:
    tools = []
    for tool in mcp_tools:
        tools.append({
            "type": "function",
            "function": {
                "name": _value(tool, "name"),
                "description": _value(tool, "description", ""),
                "parameters": _value(tool, "input_schema", {"type": "object", "properties": {}}),
            },
        })
    return tools


def _result_text(result: Any) -> str:
    structured = getattr(result, "structured_content", None)
    if structured:
        return json.dumps(structured, ensure_ascii=False, default=str)
    content = getattr(result, "content", None) or []
    parts = [getattr(item, "text", str(item)) for item in content]
    return "\n".join(parts) if parts else json.dumps(result, ensure_ascii=False, default=str)


def _format_complementary_result(result: Any) -> str:
    """Formater directement le résultat MCP sans repasser par Ollama."""
    structured = getattr(result, "structured_content", None)
    if not structured:
        content = _result_text(result)
        try:
            structured = json.loads(content)
        except json.JSONDecodeError:
            return content

    target = structured.get("target_player", {})
    target_name = target.get("player", "joueur demandé")
    players = structured.get("players", [])
    if not players:
        return f"Aucun joueur complémentaire trouvé pour {target_name}."

    lines = [f"Joueurs complémentaires à {target_name} :", ""]
    for index, player in enumerate(players, start=1):
        name = player.get("player", "Nom inconnu")
        team = player.get("team")
        score = player.get("complementarity_score")
        details = []
        if team:
            details.append(str(team))
        if score is not None:
            details.append(f"score : {score}")
        suffix = f" — {' — '.join(details)}" if details else ""
        lines.append(f"{index}. {name}{suffix}")
    return "\n".join(lines)


def _server_parameters() -> StdioServerParameters:
    return StdioServerParameters(
        command=os.environ.get("DATAFOOT_PYTHON", sys.executable),
        args=[str(DEFAULT_SERVER)],
        cwd=str(PROJECT_ROOT),
        env=dict(os.environ),
    )


def _complementary_request_from_question(question: str) -> tuple[str, bool] | None:
    """Extraire le joueur et détecter si une explication est demandée."""
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFD", question.lower())
        if unicodedata.category(char) != "Mn"
    )
    match = re.search(
        r"complement\w*\s+(?:a|de|pour)\s+(.+?)(?=\s+et\s+(?:pourquoi|explique|justifie)|[?!.]|$)",
        normalized,
    )
    if not match:
        return None
    player = match.group(1).strip()
    asks_explanation = bool(
        re.search(
            r"\b(?:pourquoi|explique|justifie|raison|raisons)\b",
            normalized,
        )
    )
    return player, asks_explanation


async def ask_ollama(question: str, model: str = "qwen3:4b", max_rounds: int = 2) -> str:
    """Pose une question a Ollama et execute les outils MCP demandes."""

    try:
        import ollama
    except ImportError as error:
        raise RuntimeError("Le paquet ollama manque. Execute : python -m pip install ollama") from error

    messages: list[Any] = [
        {
            "role": "system",
            "content": (
                "Tu es DataFootLLM, un assistant d'analyse footballistique. "
                "Pour toute question concernant des joueurs, une competition, "
                "un age, un poste ou une statistique, tu DOIS appeler l'outil MCP "
                "approprie avant de repondre. Ne decris pas le raisonnement et ne "
                "reponds pas avec une supposition. Pour une demande de liste, "
                "appelle filter_players avec les criteres explicites, puis donne "
                "les resultats retournes par l'outil en francais. Traduis les "
                "termes naturels vers les valeurs du schema : attaquant vers FW, "
                "milieu vers MF, et une borne 'moins de X ans' vers age_max=X. "
                "N'ecris pas une analyse de ta decision avant l'appel d'outil."
            ),
        },
        {"role": "user", "content": question},
    ]
    async with Client(_server_parameters()) as mcp_client:
        listed = await mcp_client.list_tools()
        # MCP 2.x retourne un ListToolsResult ; les definitions sont dans
        # sa propriete `.tools`.
        tools = _ollama_tools(getattr(listed, "tools", listed))

        # Pour cette demande fréquente, on évite de faire réfléchir Qwen sur
        # le choix de l'outil. Le MCP est appelé immédiatement, puis Ollama
        # ne reçoit qu'un résultat compact à reformuler.
        complementary_request = _complementary_request_from_question(question)
        if complementary_request:
            complementary_player, asks_explanation = complementary_request
            result = await mcp_client.call_tool(
                "find_complementary_players",
                {"player_name": complementary_player, "top_k": 5},
            )
            if asks_explanation:
                compact_result = _result_text(result)
                explanation_response = await asyncio.to_thread(
                    ollama.chat,
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Réponds en français en 8 phrases maximum. "
                                "Commence directement par la réponse, sans "
                                "préambule comme 'Okay' ou 'let's see'. Explique "
                                "pourquoi les joueurs retournés sont "
                                "complémentaires, en te basant uniquement sur "
                                "le résultat MCP. Ne montre aucun raisonnement "
                                "intermédiaire et n'appelle aucun outil."
                            ),
                        },
                        {"role": "user", "content": question},
                        {
                            "role": "user",
                            "content": f"Résultat MCP DataFoot : {compact_result}",
                        },
                    ],
                    think=False,
                    options={"num_predict": 1024, "temperature": 0.1},
                )
                explanation_message = _value(explanation_response, "message", {})
                explanation = _value(explanation_message, "content", "")
                return explanation or _format_complementary_result(result)
            return _format_complementary_result(result)

        for _ in range(max_rounds):
            response = await asyncio.to_thread(
                ollama.chat,
                model=model,
                messages=messages,
                tools=tools,
                # On garde le mode thinking desactive pour obtenir directement
                # un tool call ou une reponse visible.
                think=False,
                options={"num_predict": 1024, "temperature": 0.1},
            )
            message = _value(response, "message", {})
            calls = _value(message, "tool_calls", []) or []
            messages.append(message)
            if not calls:
                return _value(message, "content", "") or "Ollama n'a pas retourne de texte."
            for call in calls:
                function = _value(call, "function", {})
                name = _value(function, "name")
                arguments = _value(function, "arguments", {}) or {}
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                result = await mcp_client.call_tool(name, arguments)
                messages.append({"role": "tool", "tool_name": name, "content": _result_text(result)})
    raise RuntimeError("Ollama a depasse le nombre maximal de tours d'outils.")
