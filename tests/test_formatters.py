"""Unit tests for INEI MCP formatters — no network required."""

import pytest

from inei_mcp.formatters import (
    format_census_dashboard,
    format_comp_filters,
    format_geography_list,
    format_geography_profile,
    format_indicator_filters,
    format_indicator_search,
    format_thematic_tree,
)


class TestFormatGeographyList:
    def _dept(self, ccdd: str, nombre: str, id_geo: int) -> dict:
        return {
            "idGeografia": id_geo,
            "idAmbito": 2,
            "ubigeo": f"{ccdd}0000",
            "ccdd": ccdd,
            "ccpp": "00",
            "ccdi": "00",
            "departamento": nombre,
            "provincia": "",
            "distrito": "",
            "nombccpp": None,
            "nombre": nombre,
            "sea": None,
        }

    def test_departments_returns_list(self):
        raw = [
            self._dept("15", "LIMA", 2150000),
            self._dept("08", "CUSCO", 2080000),
        ]
        result = format_geography_list(raw)
        assert len(result) == 2

    def test_department_fields(self):
        raw = [self._dept("15", "LIMA", 2150000)]
        result = format_geography_list(raw)
        item = result[0]
        assert item["id_geografia"] == 2150000
        assert item["ubigeo"] == "150000"
        assert item["nombre"] == "LIMA"
        assert item["ccdd"] == "15"
        assert "ccpp" not in item
        assert "ccdi" not in item

    def test_null_sea_excluded(self):
        raw = [self._dept("15", "LIMA", 2150000)]
        result = format_geography_list(raw)
        assert "sea" not in result[0]

    def test_district_has_full_hierarchy(self):
        raw = [{
            "idGeografia": 2150101,
            "idAmbito": 3,
            "ubigeo": "150101",
            "ccdd": "15",
            "ccpp": "01",
            "ccdi": "01",
            "departamento": "LIMA",
            "provincia": "LIMA",
            "distrito": "LIMA",
            "nombre": "LIMA CERCADO",
            "nombccpp": None,
            "sea": None,
        }]
        result = format_geography_list(raw)
        item = result[0]
        assert item["ccdd"] == "15"
        assert item["ccpp"] == "01"
        assert item["ccdi"] == "01"
        assert item["departamento"] == "LIMA"
        assert item["provincia"] == "LIMA"
        assert item["distrito"] == "LIMA"


class TestFormatThematicTree:
    def test_category_node(self):
        raw = [{
            "idTema": 2,
            "descripTema": "DEMOGRAFICO",
            "idTemaPadre": 0,
            "idIndicador": None,
            "idProyecto": 100,
            "estado": 1,
            "tipo": 1,
            "orden": 1,
            "idTemaPadreRaiz": None,
            "descripTemaIndicador": "DEMOGRAFICO",
        }]
        result = format_thematic_tree(raw)
        assert len(result) == 1
        node = result[0]
        assert node["id_tema"] == 2
        assert node["descripcion"] == "DEMOGRAFICO"
        assert node["tipo"] == 1
        assert "id_indicador" not in node
        assert "id_tema_padre" not in node  # padre=0 excluded

    def test_leaf_indicator_node(self):
        raw = [{
            "idTema": 4,
            "descripTema": "Poblacion Total",
            "idTemaPadre": 3,
            "idIndicador": 516654,
            "idProyecto": 100,
            "estado": 1,
            "tipo": 2,
            "orden": 1,
            "idTemaPadreRaiz": 2,
            "descripTemaIndicador": "DEMOGRAFICO, POBLACION TOTAL",
        }]
        result = format_thematic_tree(raw)
        node = result[0]
        assert node["id_indicador"] == 516654
        assert node["id_tema_padre"] == 3
        assert node["ruta"] == "DEMOGRAFICO, POBLACION TOTAL"


class TestFormatIndicatorSearch:
    def _item(self, id_tema: int, id_ind: int, nombre: str) -> dict:
        return {
            "idTema": id_tema,
            "descripTema": nombre,
            "idTemaPadre": 1,
            "idIndicador": id_ind,
            "tipo": 2,
            "descripTemaIndicador": f"ROOT, {nombre}",
        }

    def test_only_leaf_indicators_included(self):
        raw = [
            {"idTema": 1, "descripTema": "ROOT", "tipo": 1, "idIndicador": None},
            self._item(4, 516654, "Poblacion Total"),
            self._item(5, 516687, "Poblacion Masculina"),
        ]
        result = format_indicator_search(raw, total=3)
        assert result["count"] == 2
        assert result["total"] == 3

    def test_indicator_fields(self):
        raw = [self._item(4, 516654, "Poblacion Total")]
        result = format_indicator_search(raw)
        ind = result["indicators"][0]
        assert ind["id_indicador"] == 516654
        assert ind["nombre"] == "Poblacion Total"

    def test_empty_returns_zero(self):
        result = format_indicator_search([])
        assert result["count"] == 0
        assert result["indicators"] == []


class TestFormatIndicatorFilters:
    def test_basic_filter(self):
        raw = [{
            "idGeografia": 2150000,
            "ubigeo": "150000",
            "indicador": "Poblacion Total",
            "vAbsoluto": "10135009",
            "vPorcentaje": None,
            "anualA1": None,
        }]
        result = format_indicator_filters(raw)
        assert len(result) == 1
        assert result[0]["id_geografia"] == 2150000
        assert result[0]["valor_absoluto"] == pytest.approx(10135009.0)

    def test_null_values_excluded(self):
        raw = [{
            "idGeografia": 2150000,
            "ubigeo": "150000",
            "indicador": "Test",
            "vAbsoluto": None,
            "vPorcentaje": None,
            "anualA1": None,
        }]
        result = format_indicator_filters(raw)
        assert "valor_absoluto" not in result[0]
        assert "valor_porcentaje" not in result[0]


class TestFormatGeographyProfile:
    def test_basic_profile(self):
        raw = {
            "idGeografia": "2150000",
            "titulo": "LIMA",
            "subtitulosGeografia": [],
            "body1": [
                {"label": "Poblacion 2025", "vAbsoluto": 11461995.0, "vPorcentaje": None},
                {"label": "Poblacion 2017", "vAbsoluto": 10135009.0, "vPorcentaje": None},
            ],
            "body2": [],
        }
        result = format_geography_profile(raw)
        assert result["id_geografia"] == "2150000"
        assert len(result["seccion1"]) == 2
        assert result["seccion1"][0]["label"] == "Poblacion 2025"
        assert result["seccion1"][0]["valor"] == 11461995.0

    def test_empty_body_excluded(self):
        raw = {
            "idGeografia": "2080000",
            "titulo": "CUSCO",
            "body1": [{"label": "Poblacion", "vAbsoluto": 1200000.0, "vPorcentaje": None}],
            "body2": [],
        }
        result = format_geography_profile(raw)
        assert "seccion2" not in result


class TestFormatCensusDashboard:
    def test_subtitulos_mapped(self):
        raw = {
            "subtitulos": [
                {"label": "Poblacion proyectada 2020", "value": 34350244.0},
                {"label": "Poblacion total 2017", "value": 31237385.0},
            ],
            "subtitulosGeografia": [],
            "grafico1": [],
        }
        result = format_census_dashboard(raw)
        assert "resumen_nacional" in result
        assert result["resumen_nacional"][0]["indicador"] == "Poblacion proyectada 2020"
        assert result["resumen_nacional"][0]["valor"] == 34350244.0

    def test_grafico_included(self):
        raw = {
            "subtitulos": [],
            "grafico1": [
                {"label": "Urbana", "value": 22000000.0, "porcentaje": 79.3},
                {"label": "Rural", "value": 6000000.0, "porcentaje": 20.7},
            ],
        }
        result = format_census_dashboard(raw)
        assert "grafico1" in result
        assert len(result["grafico1"]) == 2
