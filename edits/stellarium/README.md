# Dataset Stellarium para verificar las efemérides

Exportación independiente de Stellarium: diez cuerpos según `analysis_config.json`,
dos pares de coordenadas por fecha (J2000 y equinoccio de la fecha), grados decimales.
No se modifica TYCHOS ni se reemplaza el TXT de JPL. No se presentan coordenadas
Stellarium como si fueran datos astrométricos ICRF de Horizons.

El perfil de exportación usa Tierra, cálculo planetocéntrico (geocéntrico),
tiempo detenido, sin atmósfera, sin tiempo de luz y sin aberración. Esto es un
experimento geométrico, distinto de la vista observacional habitual de Stellarium.
Las RA/Dec de la fecha incluyen las convenciones de orientación de Stellarium;
no deben identificarse automáticamente con las coordenadas de TYCHOS.

## Ejecutar desde la raíz del repositorio

Primero preparar un mes de prueba, con el paso y cuerpos del JSON de análisis:

```powershell
.venv/Scripts/python.exe -B edits/stellarium/dataset.py prepare --stop "2000-07-21 00:00" --wait 0.2
.venv/Scripts/python.exe -B edits/stellarium/dataset.py prepare --start "2025-06-21 00:00" --stop "2025-07-21 00:00" --wait 0.2
```

Abrir una instancia de Stellarium **con ventana visible** y perfil separado.
En esta instalación, la ejecución oculta devolvió coordenadas sin actualizar:
no usarla para producir referencias. El siguiente comando es para ejecución
interactiva por el usuario:

```powershell
$exportProfile = (Resolve-Path edits/stellarium/profile).Path
& 'C:/Program Files/Stellarium/stellarium.exe' --user-dir $exportProfile --startup-script export.ssc --full-screen no
```

Esperar a que el script termine. Produce `profile/stellarium_export.jsonl` con
una marca final `complete`; la mera existencia del archivo no prueba una exportación
nueva. Antes de repetir, cerrar la instancia anterior y usar un perfil nuevo
(`--profile`) para conservar los resultados anteriores si son necesarios.

```powershell
.venv/Scripts/python.exe -B edits/stellarium/dataset.py collect
```

La recolección valida cobertura exacta del intervalo solicitado, cuerpos, fechas,
coordenadas finitas, duplicados, opciones de cálculo y posiciones consecutivas
idénticas que indicarían falta de actualización. TYCHOS puede tener un intervalo
mayor, pero debe contener cada instante solicitado; no se interpola.

Se guardan en `edits/data/stellarium/`:

- `stellarium_ephemerides.jsonl`: dataset con procedencia explícita y ambas referencias.
- `comparison.csv`: comparación con TYCHOS, diferencias RA/Dec y separación angular.
- `report.md`, `report.json`: métricas por cuerpo, configuración, hashes y fechas.
- `stellarium_log.txt`, `stellarium_config.ini`: versión, motores y opciones de la ejecución.

Para el intervalo completo, ejecutar `prepare` sin `--stop`; toma inicio, final
inclusivo y paso de `edits/scripts/analysis_config.json`. Puede tardar bastante:
con 37.985 fechas y espera de 0,2 s son al menos unas dos horas, además del cálculo.
No reducir la espera sin verificar primero que las coordenadas se actualizan.
Comparar un piloto con dos esperas distintas ayuda a detectar resultados obsoletos.

**El menor error no establece qué referencia es correcta.** Esta prueba permite
comparar dos convenciones explícitas. El dataset no entra todavía en el pipeline
ML, que identifica sus etiquetas como JPL. Tampoco representa una observación
independiente: Stellarium calcula posiciones mediante sus propias efemérides,
que pueden compartir fuentes con JPL.

## Verificación

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s edits/stellarium -p "test_*.py"
```

Referencias: [API de scripting](https://stellarium.org/doc/head/classStelMainScriptAPI.html)
(`getObjectInfo`, `setPlanetocentricCalculations`, `saveOutputAs`) y
[guía de Stellarium](https://stellarium.org/guide/) (perfil y script de inicio).
La versión instalada detectada durante la preparación fue Stellarium 26.2.0.
