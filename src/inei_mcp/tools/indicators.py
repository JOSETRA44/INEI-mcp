from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import Field

from ..client import INEIClient
from ..exceptions import INEIAPIError, INEINotFoundError, INEITimeoutError
from ..formatters import (
    format_comp_filters,
    format_indicator_filters,
    format_indicator_search,
    format_thematic_tree,
)


def register_indicator_tools(mcp: FastMCP, client: INEIClient) -> None:

    @mcp.tool(
        name="inei_search_indicators",
        description=(
            "Search INEI thematic statistical indicators by keyword.\n\n"
            "The INEI Estadist database contains indicators from the National Census 2017 and "
            "other official surveys. Search by keyword to find indicators on population, "
            "education, housing, health, employment, poverty, and more.\n\n"
            "Returns indicator ID (id_indicador), name, and hierarchical path (ruta).\n"
            "Use id_indicador with `inei_get_indicator_data` to retrieve actual values.\n\n"
            "**Example searches:** 'poblacion', 'educacion', 'vivienda', 'salud', 'empleo', "
            "'pobreza', 'analfabetismo', 'electricidad', 'agua', 'desague'"
        ),
    )
    async def inei_search_indicators(
        query: Annotated[
            str,
            Field(description="Keyword to search. E.g. 'poblacion urbana', 'educacion', 'agua potable'"),
        ],
        limit: Annotated[
            int,
            Field(default=20, ge=1, le=100, description="Max results (1-100). Default: 20."),
        ] = 20,
        offset: Annotated[
            int,
            Field(default=0, ge=0, description="Skip first N results for pagination. Default: 0."),
        ] = 0,
    ) -> dict:
        try:
            raw = await client.get(
                "/thematics/indicator/",
                params={"search": query, "limit": limit, "offset": offset},
            )
            # API returns a list (not paginated dict) for this endpoint
            items = raw if isinstance(raw, list) else raw.get("results", [])
            total = len(raw) if isinstance(raw, list) else raw.get("count")
            return format_indicator_search(items, total)
        except INEITimeoutError as exc:
            raise ToolError(str(exc)) from exc
        except (INEINotFoundError, INEIAPIError) as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="inei_get_indicator_data",
        description=(
            "Get statistical data for a specific INEI indicator across geographies.\n\n"
            "Retrieves values (absolute and percentage) for the indicator broken down by "
            "all available geographies. Use `inei_search_indicators` to find indicator IDs.\n\n"
            "**Optional:** provide `id_geografia` to filter to a specific region and also get "
            "comparative data against national/regional benchmarks.\n\n"
            "Returns values by geography: absolute value, percentage, and annual figure.\n\n"
            "**Common indicator IDs (Census 2017):**\n"
            "- 516654: Población Total\n"
            "- 262215: Población Censada\n"
            "- 262218: Población Censada Urbana\n"
            "- 262221: Población Censada Rural"
        ),
    )
    async def inei_get_indicator_data(
        id_indicador: Annotated[
            int,
            Field(description="Indicator ID from inei_search_indicators. E.g. 516654 for Población Total."),
        ],
        id_geografia: Annotated[
            int | None,
            Field(
                default=None,
                description=(
                    "Optional geography ID (from inei_get_departments) to filter and compare. "
                    "E.g. 2150000 for Lima."
                ),
            ),
        ] = None,
    ) -> dict:
        try:
            params: dict = {"id_indicador": id_indicador}
            if id_geografia:
                params["id_geografia"] = id_geografia

            if id_geografia:
                # Use comp-filters for richer comparative data when geography is specified
                raw = await client.get(
                    "/thematics/indicator/comp-filters/",
                    params={"id_indicador": id_indicador, "id_geografia": id_geografia},
                )
                data = format_comp_filters(raw if isinstance(raw, list) else [])
                return {
                    "id_indicador": id_indicador,
                    "id_geografia": id_geografia,
                    "count": len(data),
                    "data": data,
                    "tip": "Values include departmental, provincial and district breakdown where available.",
                }
            else:
                raw = await client.get(
                    "/thematics/indicator/filters/",
                    params={"id_indicador": id_indicador},
                )
                data = format_indicator_filters(raw if isinstance(raw, list) else [])
                return {
                    "id_indicador": id_indicador,
                    "count": len(data),
                    "data": data,
                }
        except INEITimeoutError as exc:
            raise ToolError(str(exc)) from exc
        except (INEINotFoundError, INEIAPIError) as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="inei_browse_topics",
        description=(
            "Browse the INEI thematic indicator tree — all categories and sub-categories.\n\n"
            "Returns the hierarchical topic tree with ~1977 entries from the Census 2017 database.\n"
            "Nodes with tipo=1 are categories; tipo=2 are leaf indicators with an id_indicador.\n\n"
            "Use `id_indicador` (only on tipo=2 nodes) with `inei_get_indicator_data`.\n\n"
            "**Top-level categories include:**\n"
            "DEMOGRAFICO, SOCIAL, ECONOMICO, VIVIENDA, HOGARES, EDUCACION, SALUD, EMPLEO"
        ),
    )
    async def inei_browse_topics(
        root_id: Annotated[
            int | None,
            Field(
                default=None,
                description=(
                    "Filter to children of a specific topic node by id_tema. "
                    "Omit to get all topics (1977 items — large response)."
                ),
            ),
        ] = None,
        only_indicators: Annotated[
            bool,
            Field(
                default=False,
                description="If true, return only leaf indicators (tipo=2) that have an id_indicador.",
            ),
        ] = False,
    ) -> dict:
        try:
            raw = await client.get("/thematics/")
            items = format_thematic_tree(raw)

            if root_id is not None:
                items = [i for i in items if i.get("id_tema_padre") == root_id]

            if only_indicators:
                items = [i for i in items if i.get("tipo") == 2 and i.get("id_indicador")]

            return {
                "count": len(items),
                "topics": items,
                "tip": "Filter by root_id to get sub-topics. Use id_indicador with inei_get_indicator_data.",
            }
        except INEITimeoutError as exc:
            raise ToolError(str(exc)) from exc
        except (INEINotFoundError, INEIAPIError) as exc:
            raise ToolError(str(exc)) from exc
