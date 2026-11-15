# Instrucciones para Codex: eventos semanales de TV FULL PRO

Este repositorio publica `eventos.json`, la agenda de eventos que muestran
las TV con TV FULL PRO en la fila «Eventos de hoy». Tu tarea, una vez por
semana, es preparar la agenda de la semana siguiente y abrir un PR. Nunca
publiques directo en `main`: el dueño revisa y aprueba cada PR.

## Tarea semanal

1. Creá la rama `eventos/AAAA-MM-DD`, donde la fecha es el **lunes** de la
   semana que vas a cargar.
2. Reemplazá el contenido de `eventos.json` por los eventos de esa semana, de
   lunes 00:00 a domingo 23:59 **hora de Argentina (UTC−3)**. Borrá los de
   la semana anterior.
3. Actualizá `semana` (ese lunes, `AAAA-MM-DD`) y `actualizado` (ahora, en
   UTC con `Z`).
4. Corré las dos verificaciones y corregí hasta que pasen:
   ```bash
   cd tools && python3 -m unittest test_validar_eventos && cd ..
   python3 tools/validar_eventos.py eventos.json
   ```
5. Abrí un PR titulado `Eventos semana AAAA-MM-DD`. En la descripción poné:
   cantidad de eventos por `tipo`, las fuentes que consultaste y cualquier
   duda (hora no confirmada, canal dudoso).

El PR sólo puede cambiar `eventos.json` (y `imagenes/` si te lo piden). El
control de GitHub rechaza cualquier otro archivo.

## Formato de cada evento

| Campo | Regla |
| --- | --- |
| `id` | `AAAA-MM-DD-` + nombre corto en minúsculas con guiones: `2026-11-18-arg-bra` |
| `titulo` | `Equipo A vs Equipo B`, `GP de Brasil - Carrera`, `UFC 310: Pantoja vs Asakura`. Máximo 80 caracteres. |
| `competencia` | Torneo o liga: `Liga Profesional`, `Copa Libertadores`, `Fórmula 1`. |
| `tipo` | Uno de: `futbol`, `automovilismo`, `boxeo`, `mma`, `basquet`, `tenis`, `musica`, `otros`. |
| `inicio` | Hora oficial de comienzo **convertida a UTC**, terminada en `Z`. 20:00 de Argentina = `23:00:00Z`. |
| `fin` | Inicio + duración típica: fútbol 2 h 15 min, básquet 2 h 30 min, carrera de F1 2 h, MotoGP 1 h, cartelera principal de UFC 3 h, boxeo 3 h, tenis 3 h, música 3 h. |
| `canales` | Señales de TV que lo transmiten en Argentina o Chile, escritas como se conocen: `ESPN`, `ESPN 2`, `TNT Sports`, `TyC Sports`, `Fox Sports`, `TV Pública`, `DAZN 1`, `Disney+ Premium`, `TNT Sports Chile`, `Chilevisión`. Máximo 6. Nunca direcciones ni enlaces. |
| `palabras` | 2 o 3 palabras que identifican el evento en el nombre de un canal de eventos: nombres de equipos o apellidos de los peleadores (`["Boca", "River"]`, `["Pantoja", "Asakura"]`). Nada genérico como `vs`, `fecha` o `final`. |
| `destacado` | `true` sólo en los más importantes de la semana (clásicos, finales, Selección): como máximo 8. |

Cada evento necesita `canales` o `palabras` (mejor los dos).

## Qué eventos cargar

Entre 40 y 150 por semana, priorizando el público de Argentina y Chile:

- **Fútbol:** Selección Argentina y Chile, Liga Profesional y Copa Argentina,
  Primera de Chile, Copa Libertadores y Sudamericana, Champions League y
  Europa League, y los partidos principales de LaLiga, Premier League, Serie A
  y Bundesliga.
- **Automovilismo:** Fórmula 1 (clasificación y carrera), MotoGP (carrera),
  Turismo Carretera (final).
- **Combate:** UFC (cartelera principal) y peleas de título mundial de boxeo.
- **Básquet:** partidos de NBA con transmisión en la región y Liga Nacional.
- **Tenis:** desde cuartos de final en Grand Slams y Masters 1000, y partidos
  de argentinos y chilenos desde octavos.
- **Música y otros:** sólo shows o premios con transmisión confirmada en TV.

## Fuentes y reglas

- Usá fuentes oficiales: sitios de las ligas y competencias (fixtures), y
  grillas de las señales (ESPN, TNT Sports, TyC Sports, Fox Sports, DAZN,
  Disney+). Si podés, confirmá la hora en dos fuentes.
- Copiá sólo datos (equipos, hora, señal), nunca textos ni imágenes.
- **No inventes.** Si una hora no está confirmada, no cargues el evento. Si
  no estás seguro del canal, dejá `canales` vacío y usá sólo `palabras`.
- Nunca agregues enlaces, direcciones de streams, listas M3U ni datos de
  proveedores de IPTV.
- No toques otros archivos del repositorio.
