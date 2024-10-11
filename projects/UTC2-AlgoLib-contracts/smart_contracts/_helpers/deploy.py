# mypy: disable-error-code="no-untyped-call, misc"


import logging
from collections.abc import Callable
from pathlib import Path

from algokit_utils import (
    Account,
    ApplicationSpecification,
    EnsureBalanceParameters,
    ensure_funded,
    get_account,
    get_algod_client,
    get_indexer_client,
    OnSchemaBreak,
    OnUpdate,
)
from algosdk.util import algos_to_microalgos
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

logger = logging.getLogger(__name__)


from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import os

def generate_encryption_key():
    """Tạo khóa mã hóa AES ngẫu nhiên"""
    return get_random_bytes(32)  # 256 bit

def encrypt_data(data: str, key: bytes) -> str:
    """Mã hóa dữ liệu sử dụng AES với GCM mode"""
    nonce = get_random_bytes(12)  # GCM khuyến nghị sử dụng nonce 12 bytes
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def secure_deploy(client: AlgodClient, app_spec: ApplicationSpecification, deployer: Account):
    """Triển khai hợp đồng với bảo mật tích hợp"""
    # Tạo khóa mã hóa
    encryption_key = generate_encryption_key()
    
    # Lưu khóa mã hóa vào biến môi trường (chỉ cho mục đích demo, trong thực tế nên sử dụng phương pháp bảo mật hơn)
    os.environ['ENCRYPTION_KEY'] = base64.b64encode(encryption_key).decode('utf-8')
    
    # Mã hóa dữ liệu nhạy cảm trong app_spec nếu cần
    if 'sensitive_data' in app_spec:
        app_spec['sensitive_data'] = encrypt_data(app_spec['sensitive_data'], encryption_key)
    
    # Tiến hành triển khai hợp đồng
    app_client = client.deploy(
        app_spec,
        sender=deployer,
        on_schema_break=OnSchemaBreak.ReplaceApp,
        on_update=OnUpdate.UpdateApp,
        allow_delete=True,
        allow_update=True,
    )
    
    logger.info(f"Đã triển khai hợp đồng với ID: {app_client.app_id}")
    return app_client

# Sử dụng hàm secure_deploy thay vì client.deploy trong quá trình triển khai

