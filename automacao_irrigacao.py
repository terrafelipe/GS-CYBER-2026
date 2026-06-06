"""
Gemeo Digital para Irrigacao de Precisao
Disciplina: Ciberseguranca Cognitiva — Global Solution 2026

Script de automacao: coleta dados climaticos via Open-Meteo (API publica, sem chave),
simula leitura de sensores IoT e gera alerta de irrigacao com base em umidade do solo.
"""

import json
import csv
import hashlib
import datetime
import random
import urllib.request

# ─────────────────────────────────────────
# PARTE 2 — OSINT: API publica Open-Meteo
# Coleta dados climaticos reais de uma coordenada agricola
# ─────────────────────────────────────────
LAT = -23.55   # Exemplo: regiao agricola de SP
LON = -46.63

def coletar_dados_climaticos():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        f"&timezone=America%2FSao_Paulo"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            dados = json.loads(resp.read().decode())
            atual = dados["current"]
            return {
                "fonte": "Open-Meteo API (publica, sem autenticacao)",
                "latitude": LAT,
                "longitude": LON,
                "temperatura_c": atual["temperature_2m"],
                "umidade_relativa_pct": atual["relative_humidity_2m"],
                "precipitacao_mm": atual["precipitation"],
                "vento_kmh": atual["wind_speed_10m"],
                "timestamp": atual["time"],
            }
    except Exception as e:
        # Fallback simulado caso sem rede
        return {
            "fonte": "Simulado (sem conexao)",
            "latitude": LAT,
            "longitude": LON,
            "temperatura_c": 28.4,
            "umidade_relativa_pct": 62,
            "precipitacao_mm": 0.0,
            "vento_kmh": 12.3,
            "timestamp": datetime.datetime.now().isoformat(),
        }

# ─────────────────────────────────────────
# PARTE 3 — AUTOMACAO: Sensores IoT simulados + decisao de irrigacao
# ─────────────────────────────────────────

QUADRANTES = ["Q1-NorteA", "Q2-NorteB", "Q3-SulA", "Q4-SulB"]
LIMITE_UMIDADE_SOLO = 35   # % abaixo disso → ligar irrigacao

def simular_sensores_iot():
    leituras = []
    for q in QUADRANTES:
        umidade_solo = round(random.uniform(20, 70), 1)
        temperatura_solo = round(random.uniform(18, 38), 1)
        leituras.append({
            "quadrante": q,
            "umidade_solo_pct": umidade_solo,
            "temperatura_solo_c": temperatura_solo,
            "timestamp": datetime.datetime.now().isoformat(),
        })
    return leituras

def decidir_irrigacao(sensores, clima):
    comandos = []
    for s in sensores:
        # Logica do agente inteligente:
        # liga se solo seco E sem chuva prevista E umidade do ar baixa
        solo_seco = s["umidade_solo_pct"] < LIMITE_UMIDADE_SOLO
        sem_chuva = clima["precipitacao_mm"] < 1.0
        ar_seco = clima["umidade_relativa_pct"] < 70

        if solo_seco and sem_chuva and ar_seco:
            acao = "LIGAR"
            motivo = f"Solo seco ({s['umidade_solo_pct']}%), sem chuva, ar seco"
        elif s["umidade_solo_pct"] > 60:
            acao = "MANTER_DESLIGADO"
            motivo = f"Solo umido ({s['umidade_solo_pct']}%), sem necessidade"
        else:
            acao = "AGUARDAR"
            motivo = "Condicao intermediaria, monitorando"

        comandos.append({
            "quadrante": s["quadrante"],
            "acao_pivo": acao,
            "motivo": motivo,
            "umidade_solo": s["umidade_solo_pct"],
        })
    return comandos

def salvar_csv(dados, nome_arquivo):
    if not dados:
        return
    with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)
    print(f"  [CSV] Salvo: {nome_arquivo}")

def salvar_json(dados, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"  [JSON] Salvo: {nome_arquivo}")

def gerar_hash_registro(dados):
    texto = json.dumps(dados, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(texto.encode()).hexdigest()

# ─────────────────────────────────────────
# EXECUCAO PRINCIPAL
# ─────────────────────────────────────────

def main():
    print("=" * 60)
    print("  GEMEO DIGITAL — IRRIGACAO DE PRECISAO")
    print("  Ciberseguranca Cognitiva | Global Solution 2026")
    print("=" * 60)

    print("\n[1] Coletando dados climaticos via OSINT (Open-Meteo)...")
    clima = coletar_dados_climaticos()
    print(f"    Fonte    : {clima['fonte']}")
    print(f"    Temp     : {clima['temperatura_c']} C")
    print(f"    Umidade ar: {clima['umidade_relativa_pct']}%")
    print(f"    Chuva    : {clima['precipitacao_mm']} mm")

    print("\n[2] Lendo sensores IoT dos quadrantes da lavoura...")
    sensores = simular_sensores_iot()
    for s in sensores:
        print(f"    {s['quadrante']}: solo {s['umidade_solo_pct']}% umidade")

    print("\n[3] Agente inteligente decidindo irrigacao...")
    comandos = decidir_irrigacao(sensores, clima)
    for c in comandos:
        simbolo = "💧" if c["acao_pivo"] == "LIGAR" else ("✅" if c["acao_pivo"] == "MANTER_DESLIGADO" else "⏳")
        print(f"    {simbolo} {c['quadrante']} → {c['acao_pivo']} | {c['motivo']}")

    print("\n[4] Salvando dados...")
    registro_completo = {
        "clima": clima,
        "sensores": sensores,
        "comandos": comandos,
        "gerado_em": datetime.datetime.now().isoformat(),
    }
    salvar_json(registro_completo, "/home/claude/registro_irrigacao.json")
    salvar_csv(comandos, "/home/claude/comandos_pivos.csv")

    print("\n[5] Gerando hash SHA-256 de integridade do registro...")
    hash_val = gerar_hash_registro(registro_completo)
    print(f"    SHA-256: {hash_val}")

    # Salva hash separadamente para auditoria
    with open("/home/claude/hash_registro.txt", "w") as f:
        f.write(f"SHA-256: {hash_val}\nTimestamp: {datetime.datetime.now().isoformat()}\n")
    print("    Hash salvo em hash_registro.txt")

    print("\n[6] Alertas gerados:")
    alertas = [c for c in comandos if c["acao_pivo"] == "LIGAR"]
    if alertas:
        for a in alertas:
            print(f"    ⚠️  ALERTA: Irrigar {a['quadrante']} imediatamente!")
    else:
        print("    Nenhum quadrante necessita irrigacao agora.")

    print("\n" + "=" * 60)
    print("  Automacao concluida com sucesso.")
    print("=" * 60)

if __name__ == "__main__":
    main()
