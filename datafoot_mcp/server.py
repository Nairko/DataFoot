"""Serveur MCP DataFoot, independant de l'application Streamlit."""

import sys
from pathlib import Path

# `mcp dev` charge ce fichier directement, sans toujours ajouter la racine
# du projet au PYTHONPATH. On la rend explicite pour les imports du package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server import MCPServer

from datafoot_mcp.complementary_tools import find_complementary_players as complementary_service
from datafoot_mcp.percentile_tools import get_player_percentiles as percentile_service
from datafoot_mcp.player_tools import filter_players as filter_service
from datafoot_mcp.player_tools import search_player as search_service
from datafoot_mcp.statistics_tools import compare_players as compare_service
from datafoot_mcp.statistics_tools import get_player_stats as stats_service
from datafoot_mcp.similar_tools import find_similar_players as similar_service


mcp = MCPServer("DataFoot")


@mcp.tool()
def search_player(player_name: str, dataset: str = "Big5", max_results: int = 10) -> dict:
    """Rechercher un joueur par nom exact ou partiel dans Liga, Ligue1 ou Big5."""
    return search_service(player_name, dataset, max_results)


@mcp.tool()
def get_player_stats(player_name: str, dataset: str = "Big5", statistics: list[str] | None = None) -> dict:
    """Retourner les statistiques globales disponibles d'un joueur."""
    return stats_service(player_name, dataset, statistics)


@mcp.tool()
def compare_players(player_a: str, player_b: str, dataset: str = "Big5", statistics: list[str] | None = None) -> dict:
    """Comparer deux joueurs sur des statistiques communes."""
    return compare_service(player_a, player_b, dataset, statistics)


@mcp.tool()
def filter_players(dataset: str = "Liga", position: str | None = None, age_max: float | None = None, age_min: float | None = None, minutes_min: float | None = None, team: str | None = None, statistic: str | None = None, operator: str | None = None, value: float | None = None, max_results: int = 20) -> dict:
    """Filtrer les joueurs par championnat, poste, age, minutes, equipe ou statistique."""
    return filter_service(dataset, position, age_max, age_min, minutes_min, team, statistic, operator, value, max_results)


@mcp.tool()
def find_complementary_players(
    player_name: str,
    dataset: str = "Liga",
    top_k: int = 5,
    team: str | None = None,
) -> dict:
    """Trouver des joueurs du meme poste qui compensent les faiblesses du joueur cible."""
    return complementary_service(player_name, dataset, top_k, team)


@mcp.tool()
def find_similar_players(
    player_name: str,
    dataset: str = "Big5",
    top_k: int = 5,
    same_position: bool = True,
    team: str | None = None,
) -> dict:
    """Trouver les joueurs statistiquement les plus similaires à un joueur."""
    return similar_service(player_name, dataset, top_k, same_position, team)


@mcp.tool()
def get_player_percentiles(
    player_name: str,
    dataset: str = "Big5",
    statistics: list[str] | None = None,
    top_k: int = 10,
    include_all: bool = False,
    team: str | None = None,
) -> dict:
    """Comparer un joueur à son poste par percentiles.

    Par défaut, retourne seulement les meilleurs percentiles pour garder une
    réponse compacte. Utiliser include_all=True uniquement pour une analyse
    exhaustive de toutes les statistiques disponibles.
    """
    return percentile_service(player_name, dataset, statistics, top_k, include_all, team)


if __name__ == "__main__":
    mcp.run()
