import dataclasses
import importlib
from collections.abc import Callable
from pathlib import Path

from algokit_utils import Account, ApplicationSpecification
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient


import os
from Crypto.Random import get_random_bytes

# Cấu hình khóa AES
AES_KEY_SIZE = 32  # 256 bit
AES_KEY = os.environ.get('AES_KEY') or get_random_bytes(AES_KEY_SIZE)

# Cấu hình mã hóa
ENCRYPTION_CONFIG = {
    'algorithm': 'AES',
    'mode': 'CBC',
    'key_size': AES_KEY_SIZE,
    'iv_size': 16,  # 128 bit
}

# Hàm tạo IV ngẫu nhiên
def generate_iv():
    return get_random_bytes(ENCRYPTION_CONFIG['iv_size'])

# Cấu hình bảo mật
SECURITY_CONFIG = {
    'min_password_length': 12,
    'password_complexity': {
        'uppercase': 1,
        'lowercase': 1,
        'digits': 1,
        'special_chars': 1
    },
    'max_login_attempts': 5,
    'session_timeout': 30 * 60,  # 30 phút
}

# Cấu hình lưu trữ khóa
KEY_STORAGE_CONFIG = {
    'use_keyring': True,
    'keyring_service_name': 'UTC2-AlgoLib',
}
