import requests
import pandas as pd
import time
import random

# --- CONFIGURACIÓN ---
KEYWORD = "Data analyst"
PAGINAS_A_SCRAPEAR = 10  # ¡Súbelo a 10 o 20 ahora que sabemos que funciona!
FILENAME = "ofertas_infojobs_completo.csv"

url = "https://www.infojobs.net/webapp/offers/search"

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'es-ES,es;q=0.9,en;q=0.8,pl;q=0.7',
    # IMPORTANTE: Aquí están tus cookies de sesión
    'cookie': 'IJUSERUID=ce3585de-3781-4bc7-9d1e-969d2ef20dc5; ajs_anonymous_id=41a8449e-7f1d-4765-b847-e1c9dd221b4f; IJ_MCMID=18794288263694300216784712382366122773; ijreactcvskills=0; reese84=3:XTlsyJGc0sDSeQI4N2X6ow==:Orqw5s6llCgCcjKCP/tPrwhtIV/ftCK47H4UMXCb6eS43FUqzlfy6SWvXy80UWpfUzSP8tkm3miV/O7Vbgi6DjcFXuxrxXIVGJf8p4vadR7eKqDL8OWLJ6bdQrL4REObGAvEdrvkgU3s8+mWxxeiTyek5h5bU4De8wVGEw7Uqa6qOSTX/CbHPkHe+w60GWz4mFsIlmgOtxKlG2fKLCkKQiJVbMbPXOhyWH6MUNUwm8H2miLoiByqD484S+WWIgjCKhIbhBeSZKSwKqCTj0QT0soe9ba1hqYOHD0NV91gLywhKv2+PlVT11MPjuUNcANkrV3D5N74UQqluFs85D7fbgTdJhqrrNRSTZqynB4ElTFSBEhGDohmE25S6A6nalbq6VBq0y9CRDUxG8ufSu5L+ywYO3HyrrVrw5k+akSJLdH5951sV5bM75wetGpO7fgukVpxmM4/oEVAVm+N7DXDVg==:fsVT9RlynwzJrroOyLF2gwCPjzLUS9Sm3XuJ9lXlji8=; ab.storage.deviceId.c4bab0fe-f380-482a-8ef3-ae8338147fc7=%7B%22g%22%3A%22c6fc0791-2548-9ab4-b2a9-5cb61ac152da%22%2C%22c%22%3A1771267109627%2C%22l%22%3A1771267109627%7D; _gcl_au=1.1.2027612430.1771267110; didomi_token=eyJ1c2VyX2lkIjoiMTljNjdiZjMtMjY3ZS02YjM2LThmZGMtOGUxMDk3ZDZlNzAxIiwiY3JlYXRlZCI6IjIwMjYtMDItMTZUMTg6Mzg6MjkuNDc5WiIsInVwZGF0ZWQiOiIyMDI2LTAyLTE2VDE4OjM4OjMxLjIwNVoiLCJ2ZW5kb3JzIjp7ImVuYWJsZWQiOlsiZ29vZ2xlIiwiYzphZGV2aW50YS1tb3Rvci1tb3RvciIsImM6Z29vZ2xlYW5hLTRUWG5KaWdSIl19LCJwdXJwb3NlcyI6eyJlbmFibGVkIjpbImRldmljZV9jaGFyYWN0ZXJpc3RpY3MiLCJnZW9sb2NhdGlvbl9kYXRhIiwidHJhbnNmZXItdG8tbW90b3IiXX0sInZlbmRvcnNfbGkiOnsiZW5hYmxlZCI6WyJnb29nbGUiXX0sInZlcnNpb24iOjJ9; euconsent-v2=CQft6wAQft6wAAHABBENCSFsAP_gAEPgAAiQL_NR_G__bWlr-bb3aftkeYxP9_hr7sQxBgbJk24FzLvW7JwXx2E5NAzatqIKmRIAu3TBIQNlHIDURUCgKIgFryDMaE2U4TNKJ6BkiFMZA2tYCFxvm4tjWQCY4vr99lc1mB-t7dr82dzyy6hHn3a5_2S1UJCdIYetDfv8ZBOT-9IEd_x8v4v4_EbpEm-eS1n_pGvp4jd-YnM_dBmxt-Tyff7Pn__rl_e7X_vc_n3zv84XH77v____fv-7___2b_-___Bf8AEw0KiCMsiBAIFAwggQAKCsIAKBAEAACQNEBACYMCHIGAC6wmQAgBQADBACAAEGAAIAABIAEIgAgAIBACBAIFAAGABAEBAAQMAAYALEQCAAEB0DFMCCAQLABIzKoNMCUABIICWyoQSgYEFcIQizwCCBETBQAAAkAFAQAgPBYCEkgJWJBAFxBNAAAQAABRAiQIpCzAEFQZotAWBJwGRpgGD5gmSU6DJAmCEhJMiE3oTDxTFEKCHKDYpZgDp4goARcAAA.IL_tX_H__bX9v-f736ft0eY1f9_j77uQxBhfJs-4FzLvW_JwX32E7NF36tqYKmRIEu3bBIQNtHJnUTVihaogVrzHsak2c4TtKJ-BkiHMZe29YCF5vm4tj-QKZ5_r_93d92T_9_dv-3dzy3_1nv3f9_-f1eLida5_tH_v_bROb-_I_9_7-_4v8_t_rk2_eT1v_9evv7__-________9_____________-____f________________________f_____g.f_wACHwAAAAA; borosTcf=eyJwb2xpY3lWZXJzaW9uIjoyLCJjbXBWZXJzaW9uIjoxLCJwdXJwb3NlIjp7ImNvbnNlbnRzIjp7IjEiOnRydWUsIjIiOnRydWUsIjMiOnRydWUsIjQiOnRydWUsIjUiOnRydWUsIjYiOnRydWUsIjciOnRydWUsIjgiOnRydWUsIjkiOnRydWUsIjEwIjp0cnVlfX0sInNwZWNpYWxGZWF0dXJlcyI6eyIxIjp0cnVlfSwiZ29vZ2xlQW5hbHl0aWNzIjp7ImFuYWx5dGljc19zdG9yYWdlIjoiR1JBTlRFRCJ9fQ==; segment_ga=GA1.1.1056093534.1771267112; IJ_GA_SESSION_ID=1771267111; IJ_GA_CLIENT_ID=1056093534.1771267112; _hjSession_223746=eyJpZCI6Ijg4ZWNkZjliLTkxYzEtNGYyMC1iYjdjLTliYWZmMzlkNjQ4ZiIsImMiOjE3NzEyNjcxMTE2MjAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; __gads=ID=3b5c27b05f7749b7:T=1771267112:RT=1771267112:S=ALNI_MY2YLm629-mtpafaIbWi_BIltbQ0Q; __gpi=UID=000012fc5e18ed5b:T=1771267112:RT=1771267112:S=ALNI_MYrvp1k862_h3IH_O5yEsXJerclgA; __eoi=ID=0daf0ab08d6e01f5:T=1771267112:RT=1771267112:S=AA-AfjZ9wHrYcRtQv9LG27r4C5eO; _fbp=fb.1.1771267111966.337133390448318797; _hjSessionUser_223746=eyJpZCI6ImZkMGVlMzM5LTQyNDMtNTFiYi04YzU0LTg5YmU3NjM4ZDVhNSIsImNyZWF0ZWQiOjE3NzEyNjcxMTE2MTksImV4aXN0aW5nIjp0cnVlfQ==; IJTESTUID=2f6e283f-c373-4258-b11f-45492e0abf60; AWSALBCORS=h6St+rtYpf1JCPp4v0PztvpwLBYr8GESZRERx7RCnsbxlsBhpAmdCUFaxb6PposLPZYUtQkiizruq/pjF5CqT6FwLt07OxFYaIJaKum+IESSdUVr/XRGSRV2fXA3; segment_ga_7SHGGRXFWG=GS2.1.s1771267111$o1$g1$t1771267372$j31$l0$h0; cto_bundle=0gNZUl85RHptWGhmWDFwQ0UweXBDaWhNc3lXbDZWZ25nQlRhZm1lOHUlMkZoT3NTR1Y0bURlTGtYQkg3d0xjd1h3UURBRlVVaEVLb3NNdVU2OFklMkZ6NHlFckE0bHVxbmFoWGs2anA4R0x1dThKMXdOcHk1ZElibDgyM2M3M05WJTJGSjhvVUY5Q0RNVGZGaDBkUkpHT3VBZkNXSiUyQnJPUSUzRCUzRA; AWSALB=IjInHGR1YsFmd6hnla7VdoCQ8tXt0W/sjPbttCytYmb4/DmlbGwGzzMO1VO3Pn1S8J3kdtHq8PHvVAk3f9Qx+rTIqBre7zWbK5WZntR9iKrCVLCOVCSzk+0KmicV; JSESSIONID=tJudRo8QIB1d-zglC8+7oHFA; ab.storage.sessionId.c4bab0fe-f380-482a-8ef3-ae8338147fc7=%7B%22g%22%3A%228cb3249c-6e8b-b244-bb0a-3eb5d7ed04cc%22%2C%22e%22%3A1771267419565%2C%22c%22%3A1771267364102%2C%22l%22%3A1771267389565%7D',
    'origin': 'https://www.infojobs.net',
    'referer': 'https://www.infojobs.net/jobsearch/search-results/list.xhtml',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'x-adevinta-channel': 'web',
    'x-infojobs-gaclientid': '1056093534.1771267112',
    'x-infojobs-gasessionid': '1771267111',
    'x-schibsted-tenant': 'infojobs'
}

all_offers = []

print(f"🚀 Iniciando extracción de ofertas para: '{KEYWORD}'")

for page in range(1, PAGINAS_A_SCRAPEAR + 1):
    print(f"📄 Procesando página {page}...")
    
    params = {
        'keyword': KEYWORD,
        'normalizedJobTitleIds': '2511_d3edb8f8-3a06-47a0-8fb9-9b212c006aa2', # ID de Data Analyst
        'page': page,
        'sortBy': 'RELEVANCE',
        'countryIds': '17', # España
        'sinceDate': 'ANY'
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # InfoJobs a veces usa 'items' y a veces 'offers', probamos ambos
            items = data.get('items', []) or data.get('offers', [])
            
            if not items:
                print("⚠️ No hay más ofertas en esta página.")
                break
                
            for item in items:
                # --- AQUÍ ESTÁ LA CORRECCIÓN BASADA EN TU DEBUG ---
                offer = {
                    'id': item.get('code'),         # Antes era 'id'
                    'title': item.get('title'),
                    'company': item.get('companyName'), # Antes era 'author'
                    'city': item.get('city'),
                    'teleworking': item.get('teleworking'), # ¡Dato útil!
                    'contractType': item.get('contractType'),
                    'salaryDescription': item.get('salaryDescription'), # A veces viene, a veces no
                    'published': item.get('publishedAt'),
                    'link': "https:" + item.get('link') if item.get('link') else None,
                    # LA JOYA DE LA CORONA:
                    'description': item.get('description') 
                }
                all_offers.append(offer)
                
            print(f"   ✅ Extraídas {len(items)} ofertas.")
            
        elif response.status_code == 403:
            print("❌ ERROR 403: Cookies caducadas. Tienes que sacar el cURL nuevo de Chrome.")
            break
        else:
            print(f"⚠️ Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error crítico: {e}")

    # Pausa humana aleatoria
    time.sleep(random.uniform(2, 4))

# --- GUARDADO ---
if all_offers:
    df = pd.DataFrame(all_offers)
    # Filtramos por si acaso alguna fila vacía
    df = df.dropna(subset=['title'])
    
    print(f"\n📊 Resumen de datos extraídos:")
    print(f"   - Total filas: {len(df)}")
    print(f"   - Columnas: {list(df.columns)}")
    
    # Guardamos
    df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
    print(f"\n💾 ¡GUARDADO! Abre el archivo '{FILENAME}' para verlo.")
else:
    print("\n☹️ No se extrajo nada. Revisa los headers.")