import os, sys, json, requests, itertools
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY    = os.getenv("GODADDY_API_KEY")
API_SECRET = os.getenv("GODADDY_API_SECRET")
BASE_URL   = "https://api.ote-godaddy.com/v1"  # Sandbox
MAX_BATCH  = 500

if not (API_KEY and API_SECRET):
    sys.exit("❌  Faltan GODADDY_API_KEY y/o GODADDY_API_SECRET en el entorno")

HEADERS = {
    "Authorization": f"sso-key {API_KEY}:{API_SECRET}",
    "Accept": "application/json"
}

def chunks(iterable, size):
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, size))
        if not batch:
            break
        yield batch

def batch_available(domains):
    resultado = {}
    endpoint = f"{BASE_URL}/domains/available"

    for lote in chunks(domains, MAX_BATCH):
        try:
            resp = requests.post(
                endpoint,
                headers=HEADERS,
                json=lote,
                params={"checkType": "FAST"},
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()

            dominios_info = data.get("domains", [])
            if not isinstance(dominios_info, list):
                print("💥 Respuesta inesperada de GoDaddy:")
                print(json.dumps(data, indent=2))
                raise SystemExit("❌ No se pudo extraer la lista de dominios de la respuesta.")

            for info in dominios_info:
                resultado[info["domain"].lower()] = info["available"]
        except requests.HTTPError as e:
            print("❌ Error HTTP:", e)
            print("🔎 Detalle de la respuesta:", resp.text)
            raise
    return resultado

def leer_entrada(argv):
    if len(argv) < 2:
        sys.exit("Uso:\n  python godaddy_batch_check.py dominio1.com dominio2.net ...\n  python godaddy_batch_check.py -f lista.txt")

    if argv[1] == "-f":
        path = Path(argv[2])
    elif len(argv) == 2 and Path(argv[1]).is_file():
        path = Path(argv[1])
    else:
        return [d.lower() for d in argv[1:]]

    if not path.exists():
        sys.exit(f"❌ No encuentro el archivo: {path}")
    with path.open(encoding="utf-8") as fh:
        return [line.strip().lower() for line in fh if line.strip()]

if __name__ == "__main__":
    dominios = leer_entrada(sys.argv)
    try:
        estado = batch_available(dominios)
        disponibles = []

        for dom in dominios:
            dispo = estado.get(dom)
            if dispo is None:
                print(f"❓  {dom}: sin respuesta")
            elif dispo:
                print(f"✅  {dom}: DISPONIBLE")
                disponibles.append(dom)
            else:
                print(f"🚫  {dom}: tomado")

        # Guardar disponibles en archivo
        if disponibles:
            with open("disponibles.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(disponibles))
            print(f"\n📝 Guardado: {len(disponibles)} dominios disponibles en 'disponibles.txt'")
        else:
            print("\n📭 No se encontró ningún dominio disponible.")
    except Exception as e:
        print("💥 Error general:", e)
