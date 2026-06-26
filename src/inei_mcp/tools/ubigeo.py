from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import Field

from ..client import INEIClient
from ..exceptions import INEIAPIError, INEINotFoundError, INEITimeoutError
from ..formatters import format_geography_list


def register_ubigeo_tools(mcp: FastMCP, client: INEIClient) -> None:

    @mcp.tool(
        name="inei_get_departments",
        description=(
            "List all 25 departments (regions) of Peru with their geography IDs and ubigeo codes.\n\n"
            "Returns id_geografia (used in other tools), ubigeo (6-digit code), ccdd (2-digit dept code),\n"
            "and department name.\n\n"
            "**Use this first** to get the id_geografia or ccdd needed by other tools."
        ),
    )
    async def inei_get_departments() -> dict:
        try:
            raw = await client.get("/ubigeo/")
            departments = format_geography_list(raw)
            return {
                "count": len(departments),
                "departments": departments,
                "tip": (
                    "Use ccdd (2-digit code) with inei_get_provinces. "
                    "Use id_geografia with inei_get_geography_profile."
                ),
            }
        except (INEINotFoundError, INEIAPIError, INEITimeoutError) as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="inei_get_provinces",
        description=(
            "List all provinces in a Peruvian department.\n\n"
            "Provide `ccdd` (2-digit department code) — e.g. '15' for Lima, '01' for Amazonas.\n"
            "Get ccdd from `inei_get_departments`.\n\n"
            "Returns province list with id_geografia, ubigeo, nombre, ccdd, ccpp."
        ),
    )
    async def inei_get_provinces(
        ccdd: Annotated[
            str,
            Field(
                description="2-digit department code. E.g. '15' for Lima, '08' for Cusco, '04' for Arequipa.",
                min_length=1,
                max_length=2,
            ),
        ],
    ) -> dict:
        try:
            raw = await client.get(f"/ubigeo/{ccdd.zfill(2)}/")
            provinces = format_geography_list(raw)
            return {
                "ccdd": ccdd.zfill(2),
                "count": len(provinces),
                "provinces": provinces,
                "tip": "Use ccpp with inei_get_districts to list districts within a province.",
            }
        except INEINotFoundError as exc:
            raise ToolError(f"Department ccdd='{ccdd}' not found. Use inei_get_departments for valid codes.") from exc
        except (INEIAPIError, INEITimeoutError) as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="inei_get_districts",
        description=(
            "List districts in a province, or search districts by name across Peru.\n\n"
            "**Option 1:** Provide both `ccdd` and `ccpp` to list all districts of a province.\n"
            "**Option 2:** Provide only `search` to search district names across all Peru.\n\n"
            "Returns id_geografia, ubigeo, nombre, departamento, provincia, distrito."
        ),
    )
    async def inei_get_districts(
        ccdd: Annotated[
            str | None,
            Field(default=None, description="2-digit department code (required with ccpp)"),
        ] = None,
        ccpp: Annotated[
            str | None,
            Field(default=None, description="2-digit province code (required with ccdd)"),
        ] = None,
        search: Annotated[
            str | None,
            Field(default=None, description="Search term to find districts by name across Peru."),
        ] = None,
    ) -> dict:
        if not ccdd and not search:
            raise ToolError("Provide either (ccdd + ccpp) to list a province's districts, or search to find districts by name.")

        try:
            if ccdd and ccpp:
                raw = await client.get(f"/ubigeo/{ccdd.zfill(2)}/{ccpp.zfill(2)}/")
            else:
                params = {}
                if search:
                    params["search"] = search
                raw = await client.get("/ubigeo/distritos/", params=params)

            districts = format_geography_list(raw)
            return {
                "count": len(districts),
                "districts": districts,
                "tip": "Use id_geografia with inei_get_geography_profile for census data.",
            }
        except INEINotFoundError as exc:
            raise ToolError(str(exc)) from exc
        except (INEIAPIError, INEITimeoutError) as exc:
            raise ToolError(str(exc)) from exc
