import io
import pyAesCrypt
import csv
import secrets
import string
import os
import bcrypt
from hashlib import pbkdf2_hmac

def log_event(message, exception=None):
    """Registra eventos no console."""
    if exception:
        print(f"ERROR: {message}: {exception}")
    else:
        print(f"INFO: {message}")

def read_encrypted_file(filepath, password):
    """Lê e descriptografa um arquivo diretamente em memória."""
    try:
        with open(filepath, "rb") as f_in:
            output = io.BytesIO()
            file_size = os.path.getsize(filepath)
            pyAesCrypt.decryptStream(f_in, output, password, Config.BUFFER_SIZE, file_size)
            output.seek(0)
            return list(csv.reader(io.StringIO(output.read().decode("utf-8"))))
    except ValueError:
        log_event("Senha incorreta ou arquivo corrompido")
        raise ValueError("Senha incorreta ou arquivo corrompido")
    except Exception as e:
        log_event("Erro ao ler arquivo criptografado", e)
        raise

def write_encrypted_file(filepath, data, password):
    """Escreve e criptografa um arquivo diretamente em memória."""
    try:
        csv_data = io.StringIO()
        csv.writer(csv_data).writerows(data)
        csv_data.seek(0)
        with open(filepath, "wb") as f_out:
            pyAesCrypt.encryptStream(io.BytesIO(csv_data.read().encode("utf-8")), f_out, password, Config.BUFFER_SIZE)
    except Exception as e:
        log_event("Erro ao escrever arquivo criptografado", e)
        raise

def validate_password_strength(password):
    """Valida a força da senha."""
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in string.punctuation for c in password)

    issues = []
    if length < 12:
        issues.append("Menos de 12 caracteres")
    if not has_upper:
        issues.append("Sem letras maiúsculas")
    if not has_lower:
        issues.append("Sem letras minúsculas")
    if not has_digit:
        issues.append("Sem números")
    if not has_special:
        issues.append("Sem caracteres especiais")

    if not issues:
        return "Forte", "green", issues
    elif length >= 8:
        return "Média", "orange", issues
    return "Fraca", "red", issues

def generate_password(length=16):
    """Gera uma senha segura."""
    if length < 4:
        length = 4

    all_chars = string.ascii_letters + string.digits + string.punctuation
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
        *[secrets.choice(all_chars) for _ in range(length - 4)]
    ]
    random.shuffle(password)
    return ''.join(password)

def create_temp_file(data, temp_filename="temp_file.csv"):
    """Cria um arquivo temporário com os dados fornecidos."""
    try:
        with open(temp_filename, mode="w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerows(data)
        return temp_filename
    except Exception as e:
        log_event("Erro ao criar arquivo temporário", e)
        raise

def hash_password(password):
    """Gera o hash de uma senha usando bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    """Verifica se a senha corresponde ao hash armazenado."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def derive_encryption_key(password, salt, iterations=100000):
    """Deriva uma chave de criptografia usando PBKDF2."""
    return pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)

# Configurações centralizadas
class Config:
    BUFFER_SIZE = 64 * 1024
    DB_FILE = "db.aes"
    BACKUP_FILE = "db.bak"
