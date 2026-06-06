"""
Demonstracao de protecao de dados
Disciplina: Ciberseguranca Cognitiva — Global Solution 2026

Demonstra:
  1. Hash SHA-256 de dados de sensor
  2. Criptografia simetrica (Fernet / AES-128)
  3. Criptografia assimetrica (RSA-2048) — chave publica/privada
"""

import hashlib
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# ─────────────────────────────────────────
# 1. HASH SHA-256
# ─────────────────────────────────────────

def demo_hash():
    print("\n── HASH SHA-256 ──────────────────────────────")
    dado = {"quadrante": "Q1-NorteA", "umidade_solo_pct": 28.5, "timestamp": "2026-06-01T10:00:00"}
    texto = json.dumps(dado, sort_keys=True)
    hash_original = hashlib.sha256(texto.encode()).hexdigest()
    print(f"  Dado original : {texto}")
    print(f"  SHA-256       : {hash_original}")

    # Simulando adulteracao
    dado_adulterado = dado.copy()
    dado_adulterado["umidade_solo_pct"] = 99.9
    texto_adulterado = json.dumps(dado_adulterado, sort_keys=True)
    hash_adulterado = hashlib.sha256(texto_adulterado.encode()).hexdigest()
    print(f"\n  Dado adulterado: {texto_adulterado}")
    print(f"  SHA-256        : {hash_adulterado}")
    print(f"\n  Hashes iguais? {'SIM ✅' if hash_original == hash_adulterado else 'NAO ❌ — adulteracao detectada!'}")

# ─────────────────────────────────────────
# 2. CRIPTOGRAFIA SIMETRICA — Fernet (AES-128-CBC)
# ─────────────────────────────────────────

def demo_simetrica():
    print("\n── CRIPTOGRAFIA SIMETRICA (Fernet/AES) ───────")
    chave = Fernet.generate_key()
    f = Fernet(chave)

    mensagem = b"COMANDO:Q2-NorteB:LIGAR:2026-06-01T10:05:00"
    cifrado = f.encrypt(mensagem)
    decifrado = f.decrypt(cifrado)

    print(f"  Mensagem original : {mensagem.decode()}")
    print(f"  Chave simetrica   : {chave.decode()[:40]}... (truncada)")
    print(f"  Cifrado (base64)  : {cifrado.decode()[:60]}...")
    print(f"  Decifrado         : {decifrado.decode()}")
    print(f"  Integridade OK?   {'SIM ✅' if decifrado == mensagem else 'NAO ❌'}")

# ─────────────────────────────────────────
# 3. CRIPTOGRAFIA ASSIMETRICA — RSA-2048
# ─────────────────────────────────────────

def demo_assimetrica():
    print("\n── CRIPTOGRAFIA ASSIMETRICA (RSA-2048) ───────")
    # Gera par de chaves
    chave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    chave_publica = chave_privada.public_key()

    mensagem = b"Leitura sensor: umidade=32.1%, temp=29.3C"
    # Cifra com chave PUBLICA (somente o dono da privada pode ler)
    cifrado = chave_publica.encrypt(
        mensagem,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    # Decifra com chave PRIVADA
    decifrado = chave_privada.decrypt(
        cifrado,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    pub_pem = chave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    print(f"  Mensagem original : {mensagem.decode()}")
    print(f"  Chave publica (PEM):\n{pub_pem[:120]}...")
    print(f"  Cifrado (hex)     : {cifrado.hex()[:60]}...")
    print(f"  Decifrado         : {decifrado.decode()}")
    print(f"  Integridade OK?   {'SIM ✅' if decifrado == mensagem else 'NAO ❌'}")

if __name__ == "__main__":
    print("=" * 55)
    print("  DEMONSTRACAO DE PROTECAO DE DADOS")
    print("  Ciberseguranca Cognitiva | Global Solution 2026")
    print("=" * 55)
    demo_hash()
    demo_simetrica()
    demo_assimetrica()
    print("\n" + "=" * 55)
    print("  Demonstracao concluida.")
    print("=" * 55)
