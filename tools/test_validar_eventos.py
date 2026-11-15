import json
import unittest
from pathlib import Path

from validar_eventos import validar


def base(**evento):
    ev = {
        "id": "2026-11-18-arg-bra",
        "titulo": "Argentina vs Brasil",
        "competencia": "Eliminatorias",
        "tipo": "futbol",
        "inicio": "2026-11-18T23:00:00Z",
        "fin": "2026-11-19T01:00:00Z",
        "canales": ["TyC Sports", "TV Pública"],
        "palabras": ["Argentina", "Brasil"],
        "destacado": True,
    }
    ev.update(evento)
    return {
        "version": 1,
        "semana": "2026-11-16",
        "actualizado": "2026-11-15T08:00:00Z",
        "eventos": [ev],
    }


class ValidarEventos(unittest.TestCase):
    def test_archivo_del_repositorio(self):
        raiz = Path(__file__).resolve().parent.parent
        datos = json.loads((raiz / "eventos.json").read_text("utf-8"))
        self.assertEqual(validar(datos, 100, raiz), [])

    def test_evento_correcto(self):
        self.assertEqual(validar(base()), [])

    def test_horas_sin_z_o_al_reves(self):
        self.assertTrue(validar(base(inicio="2026-11-18T20:00:00-03:00")))
        self.assertTrue(validar(base(fin="2026-11-18T22:00:00Z")))
        self.assertTrue(validar(base(fin="2026-11-19T12:00:00Z")))

    def test_fuera_de_la_semana(self):
        self.assertTrue(validar(base(inicio="2026-12-20T20:00:00Z", fin="2026-12-20T22:00:00Z")))

    def test_ids_repetidos_y_tipo(self):
        datos = base()
        datos["eventos"].append(dict(datos["eventos"][0]))
        self.assertTrue(any("repetido" in e for e in validar(datos)))
        self.assertTrue(validar(base(tipo="curling")))

    def test_necesita_canales_o_palabras(self):
        self.assertTrue(validar(base(canales=[], palabras=[])))
        self.assertEqual(validar(base(canales=[])), [])

    def test_sin_enlaces(self):
        self.assertTrue(validar(base(canales=["http://servidor/live/1.ts"])))
        self.assertTrue(validar(base(titulo="Partido www.ejemplo.com")))
        self.assertTrue(validar(base(imagen="https://otro.sitio/foto.jpg")))

    def test_campos_desconocidos_y_semana_lunes(self):
        self.assertTrue(validar(base(url="x")))
        datos = base()
        datos["semana"] = "2026-11-17"
        self.assertTrue(any("lunes" in e for e in validar(datos)))

    def test_tamano(self):
        self.assertTrue(validar(base(), 400 * 1024))


if __name__ == "__main__":
    unittest.main()
