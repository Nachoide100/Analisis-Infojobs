# 📊 Data Analyst Market Pulse: InfoJobs Edition

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

> **Un análisis End-to-End del mercado laboral de datos en España.** > Desde la extracción de ofertas en tiempo real hasta la visualización de relaciones entre tecnologías.

---

## 📖 Visión General del Proyecto

Este proyecto tiene como objetivo analizar la demanda real de perfiles **Data Analyst** en España utilizando datos de InfoJobs. A diferencia de los informes anuales estáticos, este pipeline permite obtener una radiografía en tiempo real de:

* Las tecnologías más demandadas (Top Skills).
* El "Tech Stack" real: ¿Qué herramientas se piden juntas? (Ej: Python + SQL).
* Distribución geográfica y modalidades de trabajo (Remoto vs Presencial).
* Nivel de exigencia por rol y ciudad.

# 🏗️ Arquitectura del Proyecto

## 🚀 Paso 1: Extracción y Procesamiento (Python)

Se desarrolló un script en Python para realizar **Web Scraping ético** sobre el portal de InfoJobs.

* **📚 Librerías:** `requests`, `pandas`, `re` (Expresiones Regulares).
* **💪 Desafíos Resueltos:**
    * **Paginación automática:** Manejo de iteraciones y errores de servidor (Status Code 500).
    * **Feature Engineering:** Implementación de un diccionario de Regex para escanear descripciones de ofertas y detectar más de **30 habilidades técnicas** (Python, Power BI, AWS, Spark, etc.) independientemente de variaciones en su escritura.
    * **Limpieza de Datos:** Eliminación de ofertas duplicadas (promocionadas) mediante algoritmos de desduplicación por ID único.
* **📂 Output:** Generación de dos datasets normalizados:
    * `dim_ofertas.csv`: Metadatos de la oferta.
    * `fact_skills.csv`: Relación *One-to-Many* entre ofertas y habilidades.

---

## 💾 Paso 2: Data Warehousing (PostgreSQL)

Los datos procesados se ingectaron en una base de datos PostgreSQL diseñada bajo un **Esquema de Estrella**.

### 🏗️ Modelo de Datos
* **Tabla de Dimensiones (`dim_ofertas`):** Contiene el ID, título, empresa, ciudad, modalidad (híbrido/remoto) y enlace a la oferta.
```sql
CREATE TABLE dim_ofertas (
    job_id VARCHAR(50) PRIMARY KEY, 
    title TEXT,
    company TEXT,
    city TEXT,
    teleworking TEXT,
    contract_type TEXT,
    published TEXT, 
    link TEXT
);
```
* **Tabla de Hechos (`fact_skills`):** Tabla transaccional que vincula cada oferta con las herramientas requeridas.
```sql
CREATE TABLE fact_skills (
    job_id VARCHAR(50),
    skill VARCHAR(100),
    -- Creamos la relación (Foreign Key)
    CONSTRAINT fk_oferta FOREIGN KEY (job_id) REFERENCES dim_ofertas(job_id) ON DELETE CASCADE,
    -- Evitamos duplicados 
    PRIMARY KEY (job_id, skill)
);
```


### 🧠 Consultas SQL Avanzadas
Se crearon Vistas (`VIEWS`) para alimentar el dashboard, incluyendo lógica compleja como:

**1. Matriz de correlación entre skills**
* **Objetivo:** Calcular la probabilidad de que dos tecnologías se pidan juntas. Lo hacemos a través de un SELF JOIN: 

```sql
SELECT 
    a.skill AS skill_origen,
    b.skill AS skill_destino,
    COUNT(*) AS frecuencia,
    -- % de veces que aparecen juntas
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_ofertas)), 2) as porcentaje_mercado
FROM fact_skills a
JOIN fact_skills b 
    ON a.job_id = b.job_id -- Misma oferta
    AND a.skill <> b.skill -- pero distinta skill
WHERE a.skill < b.skill -- Evitar duplicados
GROUP BY a.skill, b.skill
ORDER BY frecuencia DESC
LIMIT 50;
```
**2. Matriz de importancia**

* **Objetivo:** Con gráficos de barras normales, las ciudades grandes eclipsan en ofertas a las ciudades pequeñas. Para ello usaremos las **window functions** para ver el ranking de skills más solicitadas en cada ciudad, independientemente de su tamaño o cantidad de ofertas. 
```sql
CREATE VIEW vw_top_skills_ciudad AS
WITH Ranking AS (
    SELECT 
        o.city,
        s.skill,
        COUNT(*) as total_ofertas,
        -- La función ventana
        DENSE_RANK() OVER (PARTITION BY o.city ORDER BY COUNT(*) DESC) as ranking
    FROM dim_ofertas o
    JOIN fact_skills s ON o.job_id = s.job_id
    WHERE o.city IS NOT NULL AND o.city <> ''
    GROUP BY o.city, s.skill
)
SELECT * FROM Ranking
WHERE ranking <= 3; -- Mostramos las 3 primeras
```
**3. Demanda de perfiles**

* **Objetivo:** En las ofertas tenemos información sobre skill sueltas, pero por ejemplo, herramientas como Looker, Tableau o Power BI son todas herramientas de visualización. Por ello, vamos a juntas skills en categorías, con el objetivo de determinar que tipo de perfil solicitan las empresas: Visualización & BI, Bases de datos...
```sql
CREATE VIEW vw_categorias_tech AS
SELECT 
    CASE 
        WHEN skill IN ('Python', 'R','VBA', 'SAS') THEN 'Lenguajes de Programación'
        WHEN skill IN ('SQL') THEN 'Bases de Datos'
        WHEN skill IN ('Power BI', 'Tableau', 'Qlik', 'Looker', 'Excel') THEN 'Visualización & BI'
        WHEN skill IN ('AWS', 'Azure', 'GCP', 'Snowflake', 'Databricks', 'Spark') THEN 'Cloud & Big Data'
        WHEN skill IN ('Git') THEN 'Ingeniería/DevOps'
        WHEN skill IN ('Inglés') THEN 'Soft Skills'
        ELSE 'Otros'
    END AS categoria,
    COUNT(DISTINCT job_id) as cantidad_ofertas,
    ROUND(COUNT(DISTINCT job_id) * 100.0 / (SELECT COUNT(*) FROM dim_ofertas), 2) as porcentaje_mercado
FROM fact_skills
GROUP BY 1 
ORDER BY cantidad_ofertas DESC;
```
**4. Índice de exigencia**

* **Objetivo:** Vamos a descubrir si es más díficil acceder a un puesto de tipo presencial, híbrido o teletrabajo. Para ello, calcularemos el promedio de skills requeridas por oferta y lo agruparemos según el tipo de trabajo.
```sql
CREATE VIEW vw_exigencia_mercado AS
SELECT 
    o.teleworking,
    COUNT(DISTINCT o.job_id) as total_ofertas,
    ROUND(AVG(conteo_skills), 2) as promedio_skills_pedidas
FROM dim_ofertas o
JOIN (
    SELECT job_id, COUNT(*) as conteo_skills
    FROM fact_skills
    GROUP BY job_id
) s ON o.job_id = s.job_id
GROUP BY o.teleworking
ORDER BY promedio_skills_pedidas DESC;
```
## 📊 Paso 3: Visualización e Insights (Power BI)
El informe final consta de 3 páginas interactivas diseñadas en Dark Mode para resaltar la visualización de datos complejos y mejorar la experiencia de usuario.

### 📄 Página 1: Visión General

* **Sankey Chart:** Visualización de grafos que muestra clústeres tecnológicos. Permite observar cómo SQL actúa como el nexo conector entre herramientas de BI y Lenguajes de Programación.

* **KPIs:** Indicadores clave como Total de ofertas, Top Skill del mercado y % de adopción de teletrabajo / híbrido.

* **DAX:** Medidas personalizadas para calcular rankings dinámicos y porcentajes de trabajo flexible.

```dax
Top Skill =
VAR TopSkillTable = TOPN(1, VALUES('fact_skills'[skill]), CALCULATE(COUNTROWS('fact_skills')))
RETURN CONCATENATEX(TopSkillTable, 'fact_skills'[skill], ", ")
```
```dax
% Trabajo Flexible = 
VAR OfertasFlexibles = CALCULATE(
    COUNTROWS('dim_ofertas'), 
    'dim_ofertas'[teleworking] IN {"Híbrido", "Solo teletrabajo", "Teletrabajo"} 
)
VAR Total = COUNTROWS('dim_ofertas')
RETURN
    DIVIDE(OfertasFlexibles, Total, 0)
```

### 📄 Página 2: Análisis profundo

* **Matriz de Calor:** Visualización de intensidad que cruza habilidades principales vs. secundarias.

* **Análisis de Contratación:** Desglose detallado por tipo de contrato (Indefinido vs Temporal) y modalidad laboral además de proporción según la modalidad. 

* **Detalle de Ofertas:** Tabla interactiva con iconos de URL para acceder directamente a la vacante original.

### 📄 Página 3: Advanced Segmentation

* **Índice de Exigencia:** Gráfico analítico que calcula el promedio de skills solicitadas por oferta según la modalidad (revelando, por ejemplo, que el trabajo presencial exige un perfil técnico más amplio).

* **Categorización:** Agrupación mediante SQL (CASE WHEN) para clasificar skills en segmentos como "Cloud", "Visualización", "Ingeniería", etc.
