"""Pure formatting functions: raw INEI API JSON -> clean AI-friendly dicts."""

from typing import Any


def _safe(value: Any, default: Any = None) -> Any:
    if value is None or value == "":
        return default
    return value


def format_geography_list(raw: list[dict]) -> list[dict]:
    """Clean a list of Geography objects."""
    result = []
    for g in raw:
        entry: dict[str, Any] = {
            "id_geografia": g.get("idGeografia"),
            "ubigeo": _safe(g.get("ubigeo")),
            "nombre": _safe(g.get("nombre")) or _safe(g.get("departamento")),
        }
        dept = _safe(g.get("departamento"))
        prov = _safe(g.get("provincia"))
        dist = _safe(g.get("distrito"))
        if dist:
            entry["departamento"] = dept
            entry["provincia"] = prov
            entry["distrito"] = dist
        elif prov:
            entry["departamento"] = dept
            entry["provincia"] = prov
        elif dept:
            entry["departamento"] = dept
        ccdd = _safe(g.get("ccdd"))
        ccpp = _safe(g.get("ccpp"))
        ccdi = _safe(g.get("ccdi"))
        if ccdd and ccdd != "00":
            entry["ccdd"] = ccdd
        if ccpp and ccpp != "00":
            entry["ccpp"] = ccpp
        if ccdi and ccdi != "00":
            entry["ccdi"] = ccdi
        result.append({k: v for k, v in entry.items() if v is not None})
    return result


def format_thematic_tree(raw: list[dict]) -> list[dict]:
    """Clean thematic indicator tree nodes."""
    result = []
    for t in raw:
        entry: dict[str, Any] = {
            "id_tema": t.get("idTema"),
            "descripcion": _safe(t.get("descripTema")),
            "tipo": t.get("tipo"),  # 1=category, 2=leaf indicator
        }
        if t.get("idIndicador"):
            entry["id_indicador"] = t["idIndicador"]
        if t.get("idTemaPadre") and t["idTemaPadre"] != 0:
            entry["id_tema_padre"] = t["idTemaPadre"]
        if t.get("descripTemaIndicador"):
            entry["ruta"] = t["descripTemaIndicador"]
        result.append(entry)
    return result


def format_indicator_search(raw: list[dict], total: int | None = None) -> dict[str, Any]:
    """Format paginated indicator search results."""
    indicators = []
    for t in raw:
        if t.get("tipo") == 2 and t.get("idIndicador"):
            indicators.append({
                "id_indicador": t["idIndicador"],
                "nombre": _safe(t.get("descripTema")),
                "ruta": _safe(t.get("descripTemaIndicador")),
                "id_tema": t.get("idTema"),
            })
    return {
        "total": total,
        "count": len(indicators),
        "indicators": indicators,
        "tip": "Use id_indicador with inei_get_indicator_data to retrieve values for a geography.",
    }


def format_indicator_filters(raw: list[dict]) -> list[dict]:
    """Format Report objects from indicator filters endpoint."""
    result = []
    for r in raw:
        entry: dict[str, Any] = {}
        if r.get("idGeografia"):
            entry["id_geografia"] = r["idGeografia"]
        if r.get("ubigeo"):
            entry["ubigeo"] = r["ubigeo"]
        if r.get("indicador"):
            entry["indicador"] = r["indicador"]
        v_abs = _safe(r.get("vAbsoluto"))
        v_pct = _safe(r.get("vPorcentaje"))
        a1 = _safe(r.get("anualA1"))
        if v_abs is not None:
            entry["valor_absoluto"] = float(v_abs)
        if v_pct is not None:
            entry["valor_porcentaje"] = float(v_pct)
        if a1 is not None:
            entry["anual"] = float(a1)
        if entry:
            result.append(entry)
    return result


def format_comp_filters(raw: list[dict]) -> list[dict]:
    """Format ReportComp objects — comparative indicator data by geography."""
    result = []
    for r in raw:
        entry: dict[str, Any] = {}
        for key, alias in [
            ("idGeografia", "id_geografia"),
            ("ubigeo", "ubigeo"),
            ("departamento", "departamento"),
            ("provincia", "provincia"),
            ("distrito", "distrito"),
            ("ambito", "ambito"),
            ("descripIndicador", "indicador"),
            ("descripUnidadMedida", "unidad"),
            ("frecuencia", "frecuencia"),
            ("definicion", "definicion"),
        ]:
            v = _safe(r.get(key))
            if v is not None:
                entry[alias] = v
        for key, alias in [
            ("vAbsoluto", "valor_absoluto"),
            ("vPorcentaje", "valor_porcentaje"),
            ("anualA1", "anual"),
        ]:
            v = _safe(r.get(key))
            if v is not None:
                try:
                    entry[alias] = float(v)
                except (ValueError, TypeError):
                    pass
        if entry:
            result.append(entry)
    return result


def format_geography_profile(raw: dict) -> dict[str, Any]:
    """Format datos_popup response — census profile for a specific geography."""
    result: dict[str, Any] = {
        "id_geografia": _safe(raw.get("idGeografia")),
        "titulo": _safe(raw.get("titulo")),
    }

    def _clean_body(items: list) -> list:
        out = []
        for item in items or []:
            e: dict[str, Any] = {"label": item.get("label")}
            v_abs = item.get("vAbsoluto")
            v_pct = item.get("vPorcentaje")
            if v_abs is not None:
                e["valor"] = v_abs
            if v_pct is not None:
                e["porcentaje"] = v_pct
            out.append(e)
        return out

    for key in ("body1", "body2", "body3", "body4"):
        items = raw.get(key)
        if items:
            cleaned = _clean_body(items)
            if cleaned:
                result[key.replace("body", "seccion")] = cleaned

    return {k: v for k, v in result.items() if v is not None}


def format_census_dashboard(raw: dict) -> dict[str, Any]:
    """Format CPV demographic or social dashboard response."""
    result: dict[str, Any] = {}

    subtitulos = raw.get("subtitulos", [])
    if subtitulos:
        result["resumen_nacional"] = [
            {"indicador": s.get("label"), "valor": s.get("value")}
            for s in subtitulos
        ]

    for key in ("grafico1", "grafico2", "grafico3", "grafico4"):
        grafico = raw.get(key)
        if grafico and isinstance(grafico, list):
            result[key] = [
                {
                    "label": g.get("label") or g.get("nombre"),
                    "valor": g.get("value") or g.get("vAbsoluto"),
                    "porcentaje": g.get("porcentaje") or g.get("vPorcentaje"),
                }
                for g in grafico
                if g.get("label") or g.get("nombre")
            ]

    return result
