# TV FULL PRO: eventos

Agenda semanal de eventos que muestra TV FULL PRO en la fila «Eventos de hoy».

- **Archivo publicado:** https://luchochavezfacebook-byte.github.io/tvfull_eventos/eventos.json
- **Quién lo carga:** Codex, una vez por semana, con un PR (ver [AGENTS.md](AGENTS.md)).
- **Quién lo aprueba:** el dueño del repositorio. Al mezclar el PR en `main`,
  GitHub Pages lo publica y las TV lo toman en hasta 3 horas.

Este repositorio está separado del de la app y de la OTA: un error acá nunca
afecta `update.json` ni las actualizaciones de las TV.

## Controles automáticos

`.github/workflows/validar.yml` corre en cada PR y en cada push:

- pruebas del validador (`tools/test_validar_eventos.py`);
- `tools/validar_eventos.py`: formato, horas en UTC, rango de la semana, `id`
  únicos, sin enlaces y tamaño máximo;
- en las ramas `eventos/…`, que el PR sólo cambie `eventos.json` e
  `imagenes/`.

`.github/workflows/publicar.yml` vuelve a validar y publica en GitHub Pages
sólo `eventos.json` e `imagenes/`.

## Probar en la computadora

```bash
cd tools && python3 -m unittest test_validar_eventos && cd ..
python3 tools/validar_eventos.py eventos.json
```

## Imágenes para los eventos destacados

Las imágenes van en `imagenes/biblioteca/`. Se las pasás a Codex como links
en el pedido semanal (él las descarga, las achica y las guarda), o las subís
vos en GitHub (**Add file → Upload files** dentro de esa carpeta). Codex nunca
busca imágenes por su cuenta. El control automático rechaza las que no cumplan:

- **JPG** (o PNG/WEBP) de **960×540**, de **150 KB como máximo**.
- Nombre en minúsculas con guiones que diga qué muestra:
  `champions-noche.jpg`, `clasico-argentino.jpg`, `f1-noche.jpg`.
- **Genéricas**: sin personas reconocibles, escudos, camisetas reales ni
  logos de ligas o canales.
- La parte de abajo un poco oscura (ahí va el texto de la tarjeta).

