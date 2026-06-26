from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import Field

from ..client import INEIClient
from ..exceptions import INEIAPIError, INEINotFoundError, INEITimeoutError
from ..formatters import format_census_dashboard, format_geography_profile


def register_census_tools(mcp: FastMCP, client: INEIClient) -> None:

    @mcp.tool(
        name="inei_get_geography_profile",
        description=(
            "Get the Census 2017 population profile for a specific Peruvian geography.\n\n"
            "Returns key census indicators for a department, province or district: total population, "
            "urban/rural breakdown, gender split, working-age population, electoral population, "
            "population density, and more.\n\n"
            "Provide `id_geografia` — a 7-digit ID from `inei_get_departments` or `inei_get_provinces`.\n\n"
            "**Common department IDs:**\n"
            "- 2010000: Amazonas  - 2020000: Ancash   - 2030000: Apurimac\n"
            "- 2040000: Arequipa  - 2050000: Ayacucho - 2060000: Cajamarca\n"
            "- 2070000: Callao    - 2080000: Cusco    - 2150000: Lima\n"
            "- 2130000: La Libertad - 2140000: Lambayeque - 2200000: Piura"
        ),
    )
    async def inei_get_geography_profile(
        id_geografia: Annotated[
            int,
            Field(
                description="Geography ID (7 digits). E.g. 2150000 for Lima, 2080000 for Cusco.",
            ),
        ],
    ) -> dict:
        try:
            raw = await client.get(f"/cpv/indicator/datos_popup/{id_geografia}/")
            result = format_geography_profile(raw)
            return {
                **result,
                "fuente": "Censos Nacionales 2017. XII de Población y VII de Vivienda. INEI.",
            }
        except INEINotFoundError as exc:
            raise ToolError(
                f"Geography id_geografia={id_geografia} not found. "
                "Use inei_get_departments to get valid IDs."
            ) from exc
        except INEITimeoutError as exc:
            raise ToolError(str(exc)) from exc
        except INEIAPIError as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="inei_get_census_dashboard",
        description=(
            "Get national Census 2017 summary dashboard — demographics or social indicators.\n\n"
            "**demografico:** Population totals, age structure, gender breakdown, urban/rural split, "
            "population density, age pyramid data.\n\n"
            "**social:** Education (literacy, school attendance), housing (water, electricity, sanitation), "
            "health insurance coverage, household composition.\n\n"
            "Returns key national figures, charts data, and breakdowns by region.\n"
            "For specific regional data, use `inei_get_geography_profile` instead."
        ),
    )
    async def inei_get_census_dashboard(
        tipo: Annotated[
            Literal["demografico", "social"],
            Field(
                default="demografico",
                description="Dashboard type: 'demografico' (population) or 'social' (education, housing, health).",
            ),
        ] = "demografico",
    ) -> dict:
        try:
            raw = await client.get(f"/cpv/dashboard/{tipo}/")
            result = format_census_dashboard(raw)
            return {
                "tipo": tipo,
                "fuente": "Censos Nacionales 2017. XII de Población y VII de Vivienda. INEI.",
                **result,
            }
        except INEITimeoutError as exc:
            raise ToolError(
                f"The census dashboard is temporarily unavailable (timeout). "
                "Try inei_get_geography_profile for a specific region instead."
            ) from exc
        except INEIAPIError as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="inei_get_data_sources",
        description=(
            "List the official data sources available in the INEI Estadist platform.\n\n"
            "Returns source IDs, names, and descriptions. Sources include:\n"
            "- Censos Nacionales 2017 (Census)\n"
            "- MINSA (Health Ministry)\n"
            "- RENIEC (Civil Registry)\n"
            "- MEF (Economy Ministry)\n"
            "- SEAS (Education indicators)"
        ),
    )
    async def inei_get_data_sources() -> dict:
        try:
            raw = await client.get("/cpv/fuente/")
            sources = [
                {
                    "id_fuente": s.get("idFuente"),
                    "nombre": s.get("fuente"),
                    "descripcion": s.get("descripFuente"),
                }
                for s in raw
            ]
            return {"count": len(sources), "sources": sources}
        except (INEIAPIError, INEITimeoutError) as exc:
            raise ToolError(str(exc)) from exc
