import pandas as pd
import re

# --- 1. CONFIGURACIÓN Y DICCIONARIO ---
INPUT_FILE = "ofertas_infojobs_completo.csv"
OUTPUT_OFERTAS = "dim_ofertas.csv"
OUTPUT_SKILLS = "fact_skills.csv"

# Diccionario: 'Nombre Estandarizado': ['variacion1', 'variacion2', ...]
# Usamos REGEX (expresiones regulares) para evitar falsos positivos
# \b significa "límite de palabra" (para que 'R' no coincida con 'fueron')
SKILLS_DICT = {
    # Lenguajes
    'Python': [r'python'],
    'R': [r'\br\b', r'r studio', r'r-studio'],
    'SQL': [r'sql', r'mysql', r'postgres', r'tsql', r'pl/sql'],
    'SAS': [r'\bsas\b'],
    'VBA': [r'vba', r'visual basic', r'macros'],
    
    # Visualización
    'Power BI': [r'power bi', r'powerbi', r'pbi', r'dax'],
    'Tableau': [r'tableau'],
    'Qlik': [r'qlik', r'qliksense', r'qlikview'],
    'Excel': [r'excel', r'hojas de c\xe1lculo', r'spreadsheet'],
    'Looker': [r'looker'],

    # Cloud & Big Data
    'AWS': [r'aws', r'amazon web services'],
    'Azure': [r'azure'],
    'GCP': [r'gcp', r'google cloud'],
    'Spark': [r'spark', r'pyspark'],
    'Snowflake': [r'snowflake'],
    'Databricks': [r'databricks'],

    # Otros
    'Inglés': [r'ingl\xe9s', r'english', r'nivel c1', r'nivel b2'],
    'Git': [r'git', r'github', r'gitlab']
}

def extract_skills(description):
    """Recibe un texto y devuelve una lista de skills encontradas."""
    if not isinstance(description, str):
        return []
    
    found_skills = []
    desc_lower = description.lower()
    
    for skill_name, patterns in SKILLS_DICT.items():
        for pattern in patterns:
            # Buscamos el patrón en el texto (re.search es más potente que 'in')
            if re.search(pattern, desc_lower):
                found_skills.append(skill_name)
                break # Si encuentra una variación, pasa a la siguiente skill
                
    return found_skills

# --- 2. CARGA Y LIMPIEZA ---
print("⚙️ Cargando datos...")
df = pd.read_csv(INPUT_FILE)

# Rellenar nulos en descripción para que no falle
df['description'] = df['description'].fillna("")

# --- 3. EXTRACCIÓN DE SKILLS ---
print("🕵️‍♂️ Buscando palabras clave en las descripciones...")
# Aplicamos la función a cada fila
df['skills_list'] = df['description'].apply(extract_skills)

# --- 4. CREACIÓN DE LAS DOS TABLAS ---

# A) Tabla de Hechos (Skills) - Técnica "Explode"
# Esto separa la lista [Python, SQL] en dos filas duplicando el ID
df_skills = df[['id', 'skills_list']].explode('skills_list')
df_skills = df_skills.dropna(subset=['skills_list']) # Eliminar filas si no hubo skills
df_skills.columns = ['job_id', 'skill'] # Renombrar para SQL

# B) Tabla de Dimensiones (Ofertas) - Limpiamos columnas que no necesitamos
cols_to_keep = ['id', 'title', 'company', 'city', 'teleworking', 'contractType', 'published', 'link']
# Si tienes salario en tu CSV original, añádelo aquí
if 'salaryMin' in df.columns: 
    cols_to_keep.extend(['salaryMin', 'salaryMax'])

df_ofertas = df[cols_to_keep].copy()
df_ofertas.columns = ['job_id'] + cols_to_keep[1:] # Renombrar id a job_id para coherencia

# --- 5. EXPORTACIÓN ---
df_ofertas.to_csv(OUTPUT_OFERTAS, index=False, encoding='utf-8-sig')
df_skills.to_csv(OUTPUT_SKILLS, index=False, encoding='utf-8-sig')

print("\n✅ ¡PROCESO COMPLETADO!")
print(f"   📂 Generado: {OUTPUT_OFERTAS} ({len(df_ofertas)} ofertas)")
print(f"   📂 Generado: {OUTPUT_SKILLS} ({len(df_skills)} relaciones skill-oferta)")
print("\n🔍 Ejemplo de skills detectadas:")
print(df_skills.head(10))