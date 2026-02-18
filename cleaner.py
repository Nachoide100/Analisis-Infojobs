import pandas as pd

print("Iniciando limpieza profunda de datos...")

# --- 1. CARGAR DATOS SUCIOS ---
# Asegúrate de usar los nombres de archivo que generó tu extractor.py
df_ofertas = pd.read_csv('dim_ofertas.csv') 
df_skills = pd.read_csv('fact_skills.csv')


# --- 2. LIMPIAR OFERTAS (DIMENSIÓN) ---
# Eliminamos duplicados por ID. Nos quedamos con la primera aparición.
df_ofertas_clean = df_ofertas.drop_duplicates(subset='job_id', keep='first')

# --- 3. LIMPIAR SKILLS (HECHOS) ---
# Paso A: Eliminar duplicados exactos (Mismo ID + Misma Skill repetida)
df_skills_clean = df_skills.drop_duplicates(subset=['job_id', 'skill'], keep='first')

# Paso B: INTEGRIDAD REFERENCIAL (¡Muy Importante!)
# Solo nos quedamos con las skills cuyo job_id exista en la tabla de ofertas limpia.
# Si borramos una oferta duplicada, hay que borrar sus skills asociadas también.
ids_validos = df_ofertas_clean['job_id'].unique()
df_skills_clean = df_skills_clean[df_skills_clean['job_id'].isin(ids_validos)]

# --- 4. RESULTADOS ---
print(f"📈 Filas limpias   -> Ofertas: {len(df_ofertas_clean)} | Skills: {len(df_skills_clean)}")
print(f"🗑️ Se eliminaron {len(df_ofertas) - len(df_ofertas_clean)} ofertas y {len(df_skills) - len(df_skills_clean)} skills duplicadas.")

# --- 5. GUARDAR ---
df_ofertas_clean.to_csv('dim_ofertas_final.csv', index=False, encoding='utf-8-sig')
df_skills_clean.to_csv('fact_skills_final.csv', index=False, encoding='utf-8-sig')

