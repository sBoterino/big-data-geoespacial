# Registro del dataset con el docente

## Asunto

Registro de dataset — Proyecto Big Data Geoespacial — Echeverri, Botero y Villamizar

## Mensaje

Profesor Andrés Felipe Hernández Marulanda:

Por medio de este mensaje registramos para nuestro equipo el dataset **NYC Motor Vehicle
Collisions – Crashes**, disponible en Kaggle con el identificador
`muzammilrizvi1/motor-vehicle-collisions-crashes`.

Verificamos el dataset mediante la API de Kaggle y un perfilador reproducible incluido en el
repositorio. La versión consultada contiene **1.972.121 registros**, **29 columnas** y ocupa
**420.704.526 bytes**, por lo que cumple el requisito mínimo de un millón de registros. Incluye
las columnas numéricas `LATITUDE` y `LONGITUDE`, además de `CRASH DATE` y `CRASH TIME`.

El perfilado encontró **226.028 registros con coordenadas nulas**, **4.115 registros en
`(0,0)`** y **106 registros con coordenadas fuera de rango**. Estos casos se documentarán y
justificarán en la etapa de limpieza. Después de esas validaciones quedan 1.741.872 registros
con coordenadas válidas.

La arquitectura adoptada utiliza MongoDB en Docker para almacenar puntos GeoJSON e índices
`2dsphere`; Dask realizará la ingesta y limpieza, Spark las agregaciones espaciales y
temporales, Flask expondrá las consultas y Jenkins automatizará las pruebas y el despliegue.

Integrantes del equipo:

- Juan Guillermo Echeverri
- Sebastián Botero Velásquez
- Santiago Villamizar Mejía

Quedamos atentos si el dataset ya fue registrado por otro equipo o si existe alguna objeción.

Cordialmente,

Juan Guillermo Echeverri, Sebastián Botero Velásquez y Santiago Villamizar Mejía
