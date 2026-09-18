# Machine learning para investigar TYCHOS

Experimento inicial, ahora disponible por cuerpo: **¿los patrones del residuo lunar aprendidos en años anteriores
permiten anticipar las diferencias TYCHOS–JPL en años posteriores?**
Es regresión supervisada interpretable por mínimos cuadrados, implementada con
NumPy. No requiere GPU, redes neuronales ni un dataset nuevo. El modelo aprende
coeficientes de funciones periódicas y, opcionalmente, una tendencia.

Esto es un laboratorio de diagnóstico. No modifica la geometría, los parámetros,
las efemérides ni las carpetas de resultados de `edits`. Predecir una diferencia
no establece su causa física ni mejora por sí mismo el simulador.

## Los diez cuerpos seleccionados

`config.json` incluye Moon, Sun, Mercury, Venus, Mars, Jupiter, Saturn, Uranus,
Neptune y Pluto. La selecci?n del exportador visual **no descarga datos ni cambia
este archivo autom?ticamente**. Todos comparten las fechas y particiones de abajo.

El comando normal exige datos de los diez cuerpos. Mientras se completan los exports:

```powershell
.venv/Scripts/python.exe -B edits/machine_learning/run.py --available
# O seleccionar expresamente un subconjunto:
.venv/Scripts/python.exe -B edits/machine_learning/run.py --bodies moon sun mercury mars
```

`--available` permite exclusivamente cuerpos ausentes, con aviso y reporte PARCIAL;
no omite errores de formato ni huecos de fechas. El resumen de la ejecuci?n queda
 en `outputs/overview.md` y `outputs/overview.json`. Cada cuerpo tiene sus propios
`dataset.csv`, `report.md`, `report.json` y `annual_metrics.csv` en `outputs/<body>/`.
Los archivos antiguos en la ra?z de outputs corresponden al experimento lunar anterior.
El overview indica exactamente qu? cuerpos pertenecen a esta ejecuci?n.

### Completar los datos

En TYCHOS exportar los diez cuerpos marcados, desde **2000-06-21 00:00 UTC**
hasta **2026-01-01 00:00 UTC**, cada **6 horas**, y guardar el TXT combinado en
`edits/data/raw/tychos_ephemerides.txt`. Preservar primero el export anterior si se
quiere conservar la comparaci?n. Mantener la misma configuraci?n geom?trica en
el export completo y registrar los ajustes usados. No concatenar versiones distintas.
El ML descarta el timestamp final del 1 de enero de 2026, por su l?mite exclusivo.

Para obtener la referencia correspondiente, el comando existente es:

```powershell
.venv/Scripts/python.exe -B edits/scripts/download_jpl.py moon sun mercury venus mars jupiter saturn uranus neptune pluto --start "2000-06-21 00:00" --stop "2026-01-01 00:00" --step "6 h"
.venv/Scripts/python.exe -B edits/machine_learning/run.py
```

La descarga reemplaza el bundle JPL configurado despu?s de validar todos los
cuerpos. No se ejecuta autom?ticamente al entrenar. No hace falta modificar
`edits/scripts/analysis_config.json`: la lista y las fechas del comando son expl?citas.

### Qu? aprende para cada planeta

Se entrena y selecciona un modelo separado por cuerpo, con el mismo protocolo
train/validaci?n/test. `periods_by_body` fija las caracter?sticas antes del ajuste:

- Luna: las cuatro componentes hist?ricas del experimento inicial.
- Sol y dem?s planetas: una componente de 365.256363 d?as, con/sin tendencia,
  adem?s de controles cero y media. Es un baseline anual deliberadamente limitado,
  no una estimaci?n del periodo orbital del planeta ni un modelo completo de su error.

No se buscan periodos en test. Las ocho caracter?sticas peri?dicas descritas abajo
son espec?ficas de la Luna; el baseline anual tiene dos. Los planetas exteriores
necesitar?n una ventana m?s larga para estudiar su comportamiento orbital lento.
La selecci?n por validaci?n puede empeorar en test; el reporte lo conserva.
No se promedian estos resultados como si fueran una calibraci?n geom?trica global.

## Ejecutar

Desde la raíz del repositorio, en PowerShell:

```powershell
# Si todavía no existe el entorno:
py -m venv .venv
.venv/Scripts/python.exe -m pip install -r edits/machine_learning/requirements.txt

.venv/Scripts/python.exe -B edits/machine_learning/run.py
.venv/Scripts/python.exe -B -m unittest discover -s edits/machine_learning -p "test_*.py"
```

Abrir `edits/machine_learning/outputs/overview.md` y los reportes por cuerpo. `outputs/` se regenera y está ignorado
por Git. Para conservar otro experimento, usar `--output edits/machine_learning/outputs/trial_02`.
Los parámetros e inputs se cambian en [config.json](config.json), o con `--config`.
Las rutas de inputs son relativas a la raíz del repositorio. Repetir el comando
con el mismo output reemplaza sus resultados.

## Dataset y variables

Se leen directamente los dos TXT existentes en `edits/data/raw`, reutilizando
los lectores estrictos de `edits/scripts`. No se depende de CSV derivados que
puedan haber quedado desactualizados. Se exige igualdad de fechas, cobertura
completa y cadencia regular; no se interpolan ni completan registros.

Cada fila representa el cuerpo seleccionado observado desde el geocentro en un instante UTC.
El intervalo inicial empieza el 21 de junio de 2000 porque es el inicio de los
exports disponibles; no se inventan los meses anteriores.

| Partición | Inicio inclusivo | Fin exclusivo | Uso |
|---|---|---|---|
| Train | 2000-06-21 | 2014-01-01 | Ajustar coeficientes |
| Validación | 2014-01-01 | 2020-01-01 | Elegir una de cuatro alternativas |
| Test | 2020-01-01 | 2026-01-01 | Evaluar la alternativa congelada |

La cadencia es de seis horas. Los registros posteriores a 2025 se excluyen
deliberadamente. No hay mezcla aleatoria ni timestamps compartidos entre particiones.
No se usan ventanas móviles ni etiquetas retrasadas, por lo que no hay ventanas
que crucen los cortes. Los registros cercanos están correlacionados: el número de
filas no equivale al número de observaciones independientes.

| Variable | Función | Disponible sin JPL futuro |
|---|---|---|
| `date_utc`, `body`, `split` | Identificación y auditoría | Sí |
| `t_days` | Días desde el inicio fijo del experimento | Sí |
| Seno y coseno de cuatro fases | Ocho entradas periódicas | Sí |
| `years_from_train_center` | Tendencia opcional, centro calculado solo en train | Sí |
| `intercept` | Constante para aprender un sesgo | Sí |
| `target_lon_tychos_minus_jpl_deg` | Etiqueta a aprender, en grados | No |
| `predicted_residual_deg` | Salida del modelo elegido | Sí, con sus coeficientes |
| `unexplained_residual_deg` | Etiqueta menos predicción; evaluación | No |

**Solo las columnas indicadas en `features` de `report.json` entran al modelo.**
Las columnas de etiqueta, predicción y evaluación no son entradas. El dataset
incluye todas las características para inspección; cada candidato selecciona las suyas.

El objetivo es `wrap(longitud_TYCHOS - longitud_JPL)` en [-180°, 180°).
Las longitudes se calculan rotando ambos conjuntos de RA/Dec con la misma
oblicuidad J2000, reutilizando el análisis existente. Esta rotación común **no
resuelve** una incompatibilidad entre marcos de origen. Se rechazan residuos
de magnitud >=90°: este experimento lineal no está diseñado para saltos de envoltura.

Periodos fijados antes de esta ejecución: 14.765294, 27.554551, 31.811938 y
365.256363 días. Provienen de los diagnósticos históricos del repositorio, no de
una búsqueda automática en train. Sus etiquetas tradicionales no identifican
la causa del error observado.

## Modelos y evaluación

1. `zero`: predecir residuo cero; mide la diferencia original.
2. `mean`: aprender solo la media de train.
3. `periodic`: constante y ocho coeficientes seno/coseno.
4. `periodic_trend`: lo anterior más una pendiente por año juliano.

Se elige el menor RMSE de validación entre los cuatro. Se conservan los
coeficientes de train, sin reajustar con validación. Después se calcula el test
del elegido y de los dos controles; no se evalúan otros candidatos en test para
elegir retrospectivamente. Cambiar el experimento después de ver test lo convierte
en exploración: para otra confirmación se necesita un periodo reservado nuevo.

Se informan RMSE, MAE, sesgo y percentil 95 absoluto, en grados de longitud.
No son errores de separación angular total. El CSV anual permite ver deterioros
que un promedio de seis años podría ocultar; no se calculan intervalos de confianza
suponiendo independencia de muestras.

Archivos generados:

- `report.md`: tabla breve del experimento.
- `report.json`: configuración, fechas, versiones, hashes de inputs y del script,
  características, coeficientes, centro temporal, métricas y limitaciones.
- `dataset.csv`: entradas, etiquetas, particiones y predicción diagnóstica.
- `annual_metrics.csv`: RMSE original y no explicado por año y partición.

Los ajustes utilizados para producir los TXT se registran como desconocidos.
El JSON actual de parámetros no acredita cómo se generó un export anterior.

## Alcance científico y referencias

Las frecuencias ya fueron exploradas en 2000–2026. Por eso esta separación prueba
transferencia de coeficientes, **no descubrimiento completamente independiente**
de periodicidades. El test tampoco es evidencia independiente de que la propia
geometría del simulador nunca se haya ajustado usando esas fechas.

La compatibilidad del marco TYCHOS con ICRF está pendiente. Además, las posiciones
geométricas instantáneas del simulador no tienen el mismo contrato que las
coordenadas astrométricas de Horizons con tiempo de luz. Consultar el
[handoff](../README_handoff.md) y las
[definiciones de Horizons](https://ssd.jpl.nasa.gov/horizons/manual.html).
La separación temporal sigue el principio documentado en
[TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html),
aunque aquí implementamos tres bloques fijos, no validación cruzada.

El libro TYCHOS, segunda edición (2024), sección 14.3, páginas impresas 131–132
(páginas PDF 147–148), propone una explicación de la evección mediante el movimiento
terrestre. Esa propuesta es una hipótesis a contrastar con las transformaciones
implementadas; este ajuste no la verifica. El PDF se encuentra en
`edits/data/docs/TYCHOS book 2nd Edition Final_2024.pdf`.

El documento aportado `TYCHOS_Machine_Learning_Project.pdf` se toma como una idea
de identificación global, no como una instrucción de implementar sus 28 puntos.
Esta primera fase aborda una pregunta más pequeña y comprobable.

## Camino hacia identificación geométrica global

**La regresión diagnóstica ya funciona. Los siguientes pasos están pendientes:**

1. Auditar las cadenas de `PlotSolarSystem` y `SolarSystem`, incluyendo el plano
   lunar que no aparece explícitamente en la jerarquía visual. Construir por nodo:
   padre, hijos, velocidad, fase, radio, offsets, inclinaciones y transformación.
2. Implementar un evaluador geométrico por planeta. Comparar matrices, posiciones,
   orientaciones y RA/Dec con el motor actual en múltiples fechas, tamaños reales
   y modos visuales. Fusionar matrices puede preservar el movimiento, pero no
   demuestra redundancia de parámetros. Conservar la orientación heredada por
   satélites y el marco local terrestre; no basta con igualar posiciones.
3. Establecer origen, ejes, época, escala temporal y tratamiento de tiempo de luz
   para comparar observables equivalentes antes de optimizar geometría.
4. Exportar primero un mes de Luna, Sol, Mercurio, Venus, Marte, Júpiter y Saturno.
   Verificar identidades, precisión y fechas; luego ampliar al intervalo común.
   Para 2000-01-01–2026-01-01 cada seis horas serían unas 266.000 filas en total.
   Aplicar los mismos cortes temporales a todos los cuerpos. No usar periodos
   lunares automáticamente para otros planetas.
5. Medir sensibilidad de parámetros existentes con pequeñas variaciones,
   evaluando todos los cuerpos. Mantener congelados los parámetros de referencia
   y velocidades hasta resolver el contrato de coordenadas. Examinar degeneraciones
   antes de declarar un parámetro identificable.
6. Calibrar solo parámetros geométricos justificados con un objetivo global:
   promedio por cuerpo de errores normalizados por una escala fijada en train,
   junto con métricas individuales y peor cuerpo. La escala necesita un mínimo
   positivo para evitar divisiones por errores casi nulos. No seleccionar una
   mejora promedio que oculte deterioros en otros cuerpos.

Distancia todavía no es un objetivo: estos lectores de exports solo proporcionan
RA/Dec. Una serie temporal con una sola configuración no permite aprender cómo
responderá el motor al cambiar parámetros; harán falta ejecuciones controladas
del evaluador, con snapshots de configuración y procedencia.

Para planetas exteriores hará falta un intervalo más largo y menos denso, con
bloques temporales reservados propios. Ninguna fase autoriza introducir correcciones
empíricas en el simulador: las propuestas deben conservar una interpretación
geométrica explícita. Los términos ajustados aquí permanecen en el laboratorio.
