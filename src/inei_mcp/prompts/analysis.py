from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:

    @mcp.prompt(
        name="demographic_analysis",
        description="Structured workflow to analyze population demographics for a Peruvian department or region",
    )
    def demographic_analysis(
        geography: str = "Lima",
        id_geografia: str = "2150000",
    ) -> str:
        return f"""Perform a complete demographic analysis for {geography} (id_geografia: {id_geografia}) using INEI Census 2017 data.

Follow these steps in order:

**Step 1 — Geographic Profile**
Use `inei_get_geography_profile` with id_geografia={id_geografia} to get the census population profile.
Extract: total population, urban/rural split, gender breakdown, population density.

**Step 2 — Age Structure**
Use `inei_search_indicators` with query='poblacion censada grupos quinquenales' to find age-group indicators.
Use `inei_get_indicator_data` with each indicator and id_geografia={id_geografia} to get age pyramids.

**Step 3 — Population Comparison**
Use `inei_get_departments` to list all departments.
Use `inei_get_indicator_data` with id_indicador=262215 (Población Censada) to compare {geography} against other regions.

**Step 4 — Summary**
Based on the data, provide:
- Total population and national ranking
- Urban vs rural percentage
- Gender ratio (masculinity index)
- Key demographic insights specific to {geography}
- Population trends relative to national average"""

    @mcp.prompt(
        name="regional_comparison",
        description="Compare a statistical indicator across multiple Peruvian regions",
    )
    def regional_comparison(
        topic: str = "acceso agua potable",
        indicator_keyword: str = "agua",
    ) -> str:
        return f"""Perform a regional comparison of '{topic}' across Peru's departments using INEI data.

**Step 1 — Find the Indicator**
Use `inei_search_indicators` with query='{indicator_keyword}' to find relevant indicator IDs.
Select the most appropriate indicator(s) — look for the one with the broadest geographic coverage.

**Step 2 — Get National Data**
Use `inei_get_indicator_data` with the selected id_indicador (no id_geografia filter) to get all departments.

**Step 3 — Geographic Context**
Use `inei_get_departments` to cross-reference id_geografia values with department names.

**Step 4 — Analysis**
Present the results as:
- Ranking of departments from highest to lowest
- National average / median
- Top 5 and bottom 5 departments
- Notable regional disparities (coastal vs highland vs jungle)
- Absolute vs percentage comparison

**Step 5 — Deeper Drill-Down**
For the top and bottom performers, use `inei_get_geography_profile` to add demographic context."""

    @mcp.prompt(
        name="census_deep_dive",
        description="Comprehensive Census 2017 analysis combining demographics, social indicators, and housing",
    )
    def census_deep_dive(
        geography: str = "Peru (nacional)",
        id_geografia: str | None = None,
    ) -> str:
        geo_filter = f" with id_geografia={id_geografia}" if id_geografia else " (national level)"
        return f"""Conduct a comprehensive Census 2017 analysis for {geography}{geo_filter}.

**Phase 1 — Demographic Foundation**
{'Use `inei_get_geography_profile` with id_geografia=' + id_geografia + ' for the regional profile.' if id_geografia else 'Use `inei_get_census_dashboard` with tipo="demografico" for national population data.'}
Extract: total population, age median, gender ratio, urban/rural breakdown.

**Phase 2 — Social Indicators**
Use `inei_get_census_dashboard` with tipo="social" for education, housing, and health data.
Complement with:
- `inei_search_indicators` with query='educacion' → get literacy and school attendance indicators
- `inei_search_indicators` with query='salud' → get health insurance coverage indicators
- `inei_search_indicators` with query='vivienda' → get housing quality indicators

**Phase 3 — Infrastructure Access**
Use `inei_search_indicators` to find indicators for:
- 'agua potable' (safe water access)
- 'electricidad' (electricity coverage)
- 'desague' or 'alcantarillado' (sanitation)
For each, use `inei_get_indicator_data`{' with id_geografia=' + id_geografia if id_geografia else ''}.

**Phase 4 — Synthesis Report**
Present findings organized by:
1. Who lives here (demographics)
2. How educated are they (education)
3. How healthy are they (health)
4. What are their living conditions (housing, water, electricity)
5. What are the most critical gaps or disparities
6. Data sources and census year context"""
