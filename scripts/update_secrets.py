import requests
import json
import base64
from nacl import public

def encrypt(public_key: str, secret_value: str) -> str:
    pub = public.PublicKey(base64.b64decode(public_key))
    sealed = public.SealedBox(pub)
    encrypted = sealed.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def set_secret(token, owner, repo, secret_name, secret_value):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    req = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key",
        headers=headers
    )
    pub_data = req.json()
    encrypted = encrypt(pub_data["key"], secret_value)
    
    body = json.dumps({"encrypted_value": encrypted, "key_id": pub_data["key_id"]})
    
    requests.put(
        f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}",
        data=body,
        headers={**headers, "Content-Type": "application/json"}
    )
    print(f"Secret '{secret_name}' OK")

GITHUB_TOKEN = "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"
OWNER = "matrizarqconsciente-beep"
REPO = "oraculo-pitoniso-publisher"

# El page token real (que funciona) viene de me/accounts
USER_TOKEN = "EAAjUezcqdDcBSEt6WeAje6T9Rte03pQhJb3CYrh3MOPL1MfZC4PeexOYZABC34rPOpVgcDI1MRmJ9iCuyJo4dDiqhZCjieMZAb67nvPwn3EXRSWlliQN43NsImzc27rzZCBnfcoFkotqNcZAO8hngeF1fOvXhdLhMaBjQc6TmE4TsZAPZCYAbEP1UfDudV1Gvxoi4mIFxjwuugL9P0cMUGEBXZC1ZBGFZCLb7dvsYFkPrVuQ8w8bN9k1fClITO1MmB9pEJKEO6jxZBHIeLhkj6ZAvZApxBFobD"

# Obtener el Page Token real
r = requests.get(f"https://graph.facebook.com/v25.0/me/accounts?access_token={USER_TOKEN}")
pages = r.json().get("data", [])
page = pages[0]
PAGE_ID = page["id"]
PAGE_ACCESS_TOKEN = page["access_token"]

print(f"Page ID: {PAGE_ID}")
print(f"Page Token: {PAGE_ACCESS_TOKEN[:40]}...")

# Actualizar secrets en GitHub
set_secret(GITHUB_TOKEN, OWNER, REPO, "PAGE_ACCESS_TOKEN", PAGE_ACCESS_TOKEN)
set_secret(GITHUB_TOKEN, OWNER, REPO, "PAGE_ID", PAGE_ID)
set_secret(GITHUB_TOKEN, OWNER, REPO, "USER_TOKEN", USER_TOKEN)

print("Secrets actualizados!")
