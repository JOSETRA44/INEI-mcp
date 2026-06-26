from mcp.server.fastmcp import FastMCP


def register_resources(mcp: FastMCP) -> None:

    @mcp.resource(
        uri="inei://api-guide",
        name="INEI API Guide",
        description="Complete reference for the INEI Estadist API — endpoints, IDs, and data model",
        mime_type="text/markdown",
    )
    def api_guide() -> str:
        return """# INEI Estadist API — Reference Guide

## Overview
**Base URL:** `https://estadistapi.inei.gob.pe/api/v1`
**Auth:** None required (public API, HTTPS only)
**Data:** Primarily Census 2017 (XII Censo de Población, VII de Vivienda)

---

## Key Concepts

### idGeografia (Geography ID)
A 7-digit integer uniquely identifying a geographic unit:
- Format: `{2}{ccdd}{ccpp}{ccdi}` where each part is 2 digits, zero-padded
- Department level: ccpp=00, ccdi=00 (e.g. Lima = 2150000)
- Province level: ccdi=00 (e.g. Lima province = 2150101)
- District level: all 3 parts non-zero

### Ubigeo
6-character code: `{ccdd}{ccpp}{ccdi}` (e.g. "150101" for Lima Cercado)

### idIndicador / idTema
- `idTema`: node in the thematic tree (1977 nodes)
- `idIndicador`: actual data indicator (only on leaf nodes, tipo=2)
- Use `/thematics/indicator/?search=` to find indicators

---

## Endpoints

### Geography (Ubigeo)
| Endpoint | Description |
|----------|-------------|
| `GET /ubigeo/` | All 25 departments |
| `GET /ubigeo/{ccdd}/` | Provinces of a department |
| `GET /ubigeo/{ccdd}/{ccpp}/` | Districts of a province |
| `GET /ubigeo/distritos/?search=` | Search districts by name |
| `GET /ubigeo/geografia/?id_ambito=2` | Departments by scope |

### Thematic Indicators
| Endpoint | Description |
|----------|-------------|
| `GET /thematics/` | Full topic tree (1977 items) |
| `GET /thematics/indicator/?search=&limit=&offset=` | Search indicators |
| `GET /thematics/indicator/filters/?id_indicador=` | Data by geography for one indicator |
| `GET /thematics/indicator/comp-filters/?id_indicador=&id_geografia=` | Comparative data |

### Census (CPV 2017)
| Endpoint | Description |
|----------|-------------|
| `GET /cpv/dashboard/demografico/` | National demographic dashboard |
| `GET /cpv/dashboard/social/` | National social indicators dashboard |
| `GET /cpv/fuente/` | Data sources list |
| `GET /cpv/indicator/datos_popup/{id_geografia}/` | Census profile for a geography |

---

## Department Codes (ccdd)
| ccdd | Department | idGeografia |
|------|-----------|-------------|
| 01 | Amazonas | 2010000 |
| 02 | Ancash | 2020000 |
| 03 | Apurimac | 2030000 |
| 04 | Arequipa | 2040000 |
| 05 | Ayacucho | 2050000 |
| 06 | Cajamarca | 2060000 |
| 07 | Callao | 2070000 |
| 08 | Cusco | 2080000 |
| 09 | Huancavelica | 2090000 |
| 10 | Huanuco | 2100000 |
| 11 | Ica | 2110000 |
| 12 | Junin | 2120000 |
| 13 | La Libertad | 2130000 |
| 14 | Lambayeque | 2140000 |
| 15 | Lima | 2150000 |
| 16 | Loreto | 2160000 |
| 17 | Madre de Dios | 2170000 |
| 18 | Moquegua | 2180000 |
| 19 | Pasco | 2190000 |
| 20 | Piura | 2200000 |
| 21 | Puno | 2210000 |
| 22 | San Martin | 2220000 |
| 23 | Tacna | 2230000 |
| 24 | Tumbes | 2240000 |
| 25 | Ucayali | 2250000 |

---

## Common Indicator IDs (Census 2017)
| id_indicador | Description |
|--------------|-------------|
| 516654 | Población Total (censada + omitida) |
| 262215 | Población Censada |
| 516687 | Población Total Masculina |
| 516688 | Población Total Femenina |
| 262218 | Población Censada Urbana |
| 262221 | Población Censada Rural |

---

## API Limitations
- Some endpoints are slow (5-30s) — especially `/cpv/dashboard/` and `/cpv/indicator/`
- `/thematics/indicator_map/get_datos/` returns HTTP 500 (known API bug)
- `/cpv/dashboard/` (base) times out; use `/demografico/` or `/social/` instead
- Data reflects Census 2017; population projections may be available for 2020/2025
"""

    @mcp.resource(
        uri="inei://department-codes",
        name="Peru Department Codes",
        description="Quick reference table of all 25 Peruvian departments with ubigeo codes and IDs",
        mime_type="text/markdown",
    )
    def department_codes() -> str:
        return """# Peru — Department Reference Codes

| Departamento | ccdd | Ubigeo | idGeografia |
|-------------|------|--------|-------------|
| Amazonas | 01 | 010000 | 2010000 |
| Ancash | 02 | 020000 | 2020000 |
| Apurimac | 03 | 030000 | 2030000 |
| Arequipa | 04 | 040000 | 2040000 |
| Ayacucho | 05 | 050000 | 2050000 |
| Cajamarca | 06 | 060000 | 2060000 |
| Callao | 07 | 070000 | 2070000 |
| Cusco | 08 | 080000 | 2080000 |
| Huancavelica | 09 | 090000 | 2090000 |
| Huanuco | 10 | 100000 | 2100000 |
| Ica | 11 | 110000 | 2110000 |
| Junin | 12 | 120000 | 2120000 |
| La Libertad | 13 | 130000 | 2130000 |
| Lambayeque | 14 | 140000 | 2140000 |
| Lima | 15 | 150000 | 2150000 |
| Loreto | 16 | 160000 | 2160000 |
| Madre de Dios | 17 | 170000 | 2170000 |
| Moquegua | 18 | 180000 | 2180000 |
| Pasco | 19 | 190000 | 2190000 |
| Piura | 20 | 200000 | 2200000 |
| Puno | 21 | 210000 | 2210000 |
| San Martin | 22 | 220000 | 2220000 |
| Tacna | 23 | 230000 | 2230000 |
| Tumbes | 24 | 240000 | 2240000 |
| Ucayali | 25 | 250000 | 2250000 |

## Usage Notes
- **ccdd**: Use with `inei_get_provinces` to list provinces
- **idGeografia**: Use with `inei_get_geography_profile` for census data
- **Ubigeo**: 6-digit code standard for Peruvian geographic references
"""

    @mcp.resource(
        uri="inei://thematic-categories",
        name="INEI Thematic Categories",
        description="Top-level thematic categories in the INEI indicator database with example indicator IDs",
        mime_type="text/markdown",
    )
    def thematic_categories() -> str:
        return """# INEI Estadist — Thematic Categories

The INEI database organizes ~1977 statistical indicators from Census 2017 into a hierarchical tree.

## Top-Level Categories (idTema, idTemaPadre=0)

| idTema | Category | Topics Include |
|--------|----------|----------------|
| 2 | DEMOGRAFICO | Población total, censada, grupos de edad, sexo, migracion |
| — | SOCIAL | Educacion, salud, seguro, idioma, etnia |
| — | VIVIENDA | Tipo vivienda, materiales, servicios basicos |
| — | HOGARES | Composicion hogares, jefe hogar |
| — | ECONOMICO | Actividad economica, empleo, ocupacion |

## Commonly Used Indicators

### Demografico
| id_indicador | Indicator |
|--------------|-----------|
| 516654 | Poblacion Total (censada + omitida) |
| 262215 | Poblacion Censada |
| 516687 | Poblacion Total Masculina |
| 516688 | Poblacion Total Femenina |
| 262218 | Poblacion Censada Urbana |
| 262221 | Poblacion Censada Rural |
| 262220 | Poblacion Censada Urbana Masculina |
| 262219 | Poblacion Censada Urbana Femenina |

### Age Groups (Quinquennial)
| id_indicador | Indicator |
|--------------|-----------|
| 516755 | Poblacion 0-4 años |
| 516756 | Poblacion 5-9 años |
| 516757 | Poblacion 10-14 años |
| 516758 | Poblacion 15-19 años |
| 516759 | Poblacion 20-24 años |
| 516760 | Poblacion 25-29 años |

## Searching
Use `inei_search_indicators` with Spanish keywords:
- `'poblacion'` → population indicators
- `'vivienda'` → housing indicators
- `'educacion'` → education (literacy, schooling)
- `'salud'` → health and insurance
- `'agua'` → water access
- `'electricidad'` → electricity coverage
- `'empleo'` → employment
- `'pobreza'` → poverty indicators

Then use the returned `id_indicador` with `inei_get_indicator_data`.
"""
