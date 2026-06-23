import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.google.com"

try:
    resposta = requests.get(url, timeout=10, verify=False)
    print("Status:", resposta.status_code)
    print("Conexão OK sem verificação SSL")
except Exception as erro:
    print("Erro de conexão:")
    print(erro)