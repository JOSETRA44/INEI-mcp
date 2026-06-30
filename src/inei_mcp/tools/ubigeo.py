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
            raw = await client.get("/ubigeo/")
            all_depts = format_geography_list(raw)
            code = ccdd.zfill(2)
            match = [d for d in all_depts if d.get("ccdd") == code]
            if not match:
                raise ToolError(f"Department ccdd='{code}' not found. Use inei_get_departments for valid codes.")
            return {
                "ccdd": code,
                "department": match[0],
                "note": (
                    "The current INEI Estadist API only exposes department-level geography. "
                    "Use id_geografia with inei_get_geography_profile for census data."
                ),
            }
        except (INEIAPIError, INEITimeoutError) as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="inei_get_districts",
        description=(
            "Returns all 25 Peruvian departments (province/district data not available via current API).\n\n"
            "Note: The INEI Estadist API currently only exposes department-level geography. "
            "Use id_geografia from the results with inei_get_geography_profile for census data."
        ),
    )
    async def inei_get_districts(
        ccdd: Annotated[
            str | None,
            Field(default=None, description="Department code (optional filter)"),
        ] = None,
        ccpp: Annotated[
            str | None,
            Field(default=None, description="Province code (not used, API not available)"),
        ] = None,
        search: Annotated[
            str | None,
            Field(default=None, description="Search term (client-side filter on department names)"),
        ] = None,
    ) -> dict:
        try:
            raw = await client.get("/ubigeo/")
            all_depts = format_geography_list(raw)
            filtered = all_depts
            if ccdd:
                filtered = [d for d in all_depts if d.get("ccdd") == ccdd.zfill(2)]
            if search:
                kw = search.lower()
                filtered = [d for d in filtered if kw in (d.get("nombre") or "").lower()]
            return {
                "available_data": "departments_only",
                "count": len(filtered),
                "departments": filtered,
                "note": (
                    "Province and district endpoints are not available in the current INEI API. "
                    "Use inei_get_geography_profile with a department id_geografia for census profile data."
                ),
            }
        except (INEIAPIError, INEITimeoutError) as exc:
            raise ToolError(str(exc)) from exc
