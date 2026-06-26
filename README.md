[![MCP Badge](https://lobehub.com/badge/mcp/josetra44-inei-mcp)](https://lobehub.com/mcp/josetra44-inei-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![No Auth Required](https://img.shields.io/badge/auth-none%20required-brightgreen.svg)]()

# INEI MCP Server

Connects any MCP-compatible AI agent to **INEI Estadist** — the official statistics platform of Peru's [Instituto Nacional de Estadística e Informática (INEI)](https://www.inei.gob.pe/).

Access Census 2017 data, population indicators, geographic profiles, and social statistics for all 25 departments, 196 provinces, and 1,874 districts of Peru — **no API key required**.

**Works with:** Claude Desktop · Claude Code · Cursor · VS Code Copilot · Windsurf · any MCP client

---

## Quickstart

```bash
# From source (development)
git clone https://github.com/JOSETRA44/inei-mcp.git
cd inei-mcp
uv sync
uv run inei-mcp
```

---

## Available Tools (7)

| Tool | Description |
|------|-------------|
| `inei_get_departments` | List all 25 Peruvian departments with ubigeo codes and IDs |
| `inei_get_provinces` | List provinces of a department by ccdd code |
| `inei_get_districts` | List districts of a province, or search districts by name |
| `inei_search_indicators` | Search statistical indicators by keyword |
| `inei_get_indicator_data` | Get indicator values across geographies |
| `inei_browse_topics` | Browse the full thematic indicator tree |
| `inei_get_geography_profile` | Census 2017 population profile for a region |
| `inei_get_census_dashboard` | National demographic or social dashboard |
| `inei_get_data_sources` | List official data sources |

---

## Available Prompts (3)

| Prompt | Description |
|--------|-------------|
| `demographic_analysis` | Structured demographic analysis for a department |
| `regional_comparison` | Compare an indicator across Peru's regions |
| `census_deep_dive` | Comprehensive Census 2017 analysis |

---

## Available Resources (3)

| URI | Contents |
|-----|----------|
| `inei://api-guide` | Complete API reference |
| `inei://department-codes` | All 25 department codes and IDs |
| `inei://thematic-categories` | Indicator categories with example IDs |

---

## Configuration (Claude Code / Claude Desktop)

### From source (development)
```json
{
  "mcpServers": {
    "inei": {
      "command": "uv",
      "args": ["--directory", "C:\\Users\\USER\\source\\MCPs\\INEI-mcp", "run", "inei-mcp"]
    }
  }
}
```

---

## Data Source

All data from **INEI Estadist** — Peru's official national statistics platform.
Primary data: **Censos Nacionales 2017** — XII de Población y VII de Vivienda.

---

## License

[MIT](LICENSE) — © 2026 JOSETRA44
