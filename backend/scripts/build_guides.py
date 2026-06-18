#!/usr/bin/env python3
"""Genera los bundles JSON del Centro de aprendizaje a partir de los Markdown
fuente (intranet/static/guide). Ejecutar tras editar las guías:

    python3 backend/scripts/build_guides.py

Escribe backend/application/guides_data/{fdm_bambu,fdm_other,lcd}.json con el
contenido ya parseado a HTML. Las imágenes usan el placeholder __GUIDE_BASE__
(el API lo reemplaza por la base pública de uploads según el entorno; los
archivos viven en /shared_uploads/guides/<tipo>/...).
"""
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GUIDE_SRC = os.path.join(ROOT, "intranet", "static", "guide")
OUT_DIR = os.path.join(ROOT, "backend", "application", "guides_data")

_spec = importlib.util.spec_from_file_location(
    "guide_wiki", os.path.join(ROOT, "backend", "application", "guide_wiki.py"))
gw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gw)

VARIANTS = {
    "fdm_bambu": {
        "type": "fdm", "label": "Centro de aprendizaje FDM", "folder": "fdm",
        "tabs": [
            ("Guía rápida de Bambu Studio", "guia_bambu_studio_fdm.md", "Básico"),
            ("Errores comunes", "guia_errores_comunes_fdm.md", "Intermedio"),
            ("Tips de impresión 3D", "guia_tips_impresion_3d_fdm.md", "Básico"),
            ("Diseño CAD para FDM", "guia_diseno_cad_fdm.md", "Básico"),
        ],
    },
    "fdm_other": {
        "type": "fdm", "label": "Centro de aprendizaje FDM", "folder": "fdm",
        "tabs": [
            ("Guía rápida de Cura", "guia_cura_fdm.md", "Básico"),
            ("Errores comunes", "guia_errores_comunes_fdm.md", "Intermedio"),
            ("Tips de impresión 3D", "guia_tips_impresion_3d_fdm.md", "Básico"),
            ("Diseño CAD para FDM", "guia_diseno_cad_fdm.md", "Básico"),
        ],
    },
    "lcd": {
        "type": "lcd", "label": "Centro de aprendizaje LCD / Resina", "folder": "lcd",
        "tabs": [
            ("Guía rápida de CHITUBOX", "guia_chitubox_lcd_resina.md", "Básico"),
            ("Tecnología LCD / Resina", "guia_intro_tecnologia_lcd_resina.md", "Básico"),
            ("Seguridad con resina", "guia_seguridad_resina.md", "Básico"),
            ("Postproceso: lavado y curado", "guia_postprocesado_wash_cure.md", "Básico"),
            ("Errores comunes", "guia_errores_comunes_lcd_resina.md", "Intermedio"),
            ("Modelos y diseño", "guia_modelos_y_diseno_resina.md", "Básico"),
        ],
    },
}


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    for key, v in VARIANTS.items():
        image_base = f"__GUIDE_BASE__/{v['folder']}"
        tabs = []
        for title, fname, level in v["tabs"]:
            with open(os.path.join(GUIDE_SRC, v["folder"], fname), encoding="utf-8") as fh:
                parsed = gw.parse_guide(fh.read(), image_base)
            tabs.append({
                "title": title,
                "level": level,
                "reading_min": parsed["reading_min"],
                "intro": parsed["intro"],
                "sections": parsed["sections"],
            })
        bundle = {"type": v["type"], "label": v["label"], "tabs": tabs}
        out = os.path.join(OUT_DIR, f"{key}.json")
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(bundle, fh, ensure_ascii=False, indent=1)
        print(f"wrote {out} ({len(tabs)} tabs)")


if __name__ == "__main__":
    build()
