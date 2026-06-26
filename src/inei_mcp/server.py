import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .client import INEIClient
from .config import get_settings
from .prompts.analysis import register_prompts
from .resources.guides import register_resources
from .tools.census import register_census_tools
from .tools.indicators import register_indicator_tools
from .tools.ubigeo import register_ubigeo_tools


def create_app() -> FastMCP:
    settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    client = INEIClient(settings)

    @asynccontextmanager
    async def lifespan(app: FastMCP) -> AsyncIterator[None]:
        async with client:
            yield

    mcp = FastMCP(
        "INEI Peru Statistics",
        instructions=(
            "You have access to the INEI (Instituto Nacional de Estadística e Informática) "
            "Estadist API — Peru's official national statistics platform.\n\n"
            "Data covers the National Census 2017 (XII Census de Población, VII de Vivienda) "
            "and official indicators from MINSA, RENIEC, MEF, and SEAS.\n\n"
            "**Workflow:**\n"
            "1. Use `inei_get_departments` to find geography IDs (id_geografia).\n"
            "2. Use `inei_search_indicators` to find indicator IDs (id_indicador).\n"
            "3. Use `inei_get_indicator_data` to retrieve statistical values.\n"
            "4. Use `inei_get_geography_profile` for a rich census profile of a region.\n\n"
            "Read `inei://api-guide` and `inei://department-codes` for reference data."
        ),
        lifespan=lifespan,
    )

    # Register tools
    register_ubigeo_tools(mcp, client)
    register_indicator_tools(mcp, client)
    register_census_tools(mcp, client)

    # Register prompts
    register_prompts(mcp)

    # Register resources
    register_resources(mcp)

    return mcp


def main() -> None:
    load_dotenv()
    create_app().run(transport="stdio")
