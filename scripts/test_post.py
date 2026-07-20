import requests

USER_TOKEN = "EAAjUezcqdDcBSKJmKfhn12C4oqpPQ05qah0GwEvZBZBGssjhZAZBtkVfciZBPKdj6mykZCdUKZCI9ZCPbRfJRyoFNDOBlHShVdZCT7RtOOMsbiHIrjzl1SLztJu3tyTUuCHGlCUx2oo4abLqYZA0JYoix7SBn9SYdi1fQkcjyI61f8bq0zhNjEq8tnjIMec1SrPpVLnt06Y4ZA6jCpZAXOxfucjs1yClfytF2aqt58ZCdcTsDdX3GrE8Yj3u6mELU5Wl4VXMjPb90DkZBeYQXS5jFXMgZCZCyQZDZD"

# 1. Verificar permisos del token
r = requests.get(f"https://graph.facebook.com/v25.0/debug_token?input_token={USER_TOKEN}&access_token={USER_TOKEN}")
print("Permisos:", r.json()["data"]["scopes"])

# 2. Obtener Page Token
r2 = requests.get(f"https://graph.facebook.com/v25.0/me/accounts?access_token={USER_TOKEN}")
data = r2.json()
pages = data.get("data", [])
print(f"Paginas encontradas: {len(pages)}")

for p in pages:
    name = p["name"]
    pid = p["id"]
    page_token = p["access_token"]
    print(f"\nPagina: {name} (ID: {pid})")
    print(f"Page Token: {page_token[:40]}...")

    # 3. Probar publicacion
    url = f"https://graph.facebook.com/v25.0/{pid}/feed"
    params = {
        "message": "El Oraculo Pitoniso ya esta online! Ranking de IAs cada 6h. t.me/PITONISO_BOT",
        "access_token": page_token
    }
    r3 = requests.post(url, params=params)
    print(f"Status: {r3.status_code}")
    if r3.status_code == 200:
        print(f"EXITO! Post ID: {r3.json().get('id')}")
    else:
        print(f"Error: {r3.text[:300]}")
