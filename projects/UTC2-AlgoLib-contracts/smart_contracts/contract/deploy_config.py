import logging
import os
from dotenv import load_dotenv

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

logger = logging.getLogger(__name__)

# Tải biến môi trường từ file .env
load_dotenv()

# Lấy thông tin cấu hình từ biến môi trường
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN")
ALGOD_ADDRESS = "https://mainnet-api.algonode.cloud"
INDEXER_TOKEN = os.getenv("INDEXER_TOKEN")
INDEXER_ADDRESS = "https://mainnet-idx.algonode.cloud"

# Định nghĩa hành vi triển khai dựa trên thông số ứng dụng được cung cấp
def deploy(
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:

    # Khởi tạo kết nối Algod và Indexer
    algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    indexer_client = IndexerClient(INDEXER_TOKEN, INDEXER_ADDRESS)

    # Triển khai ứng dụng với AlgodClient
    # Ở đây bạn có thể viết mã tùy chỉnh để tương tác với AlgodClient, thay thế ContractClient
    # Ví dụ: gửi yêu cầu tạo ứng dụng Algorand
    app_id = algod_client.compile(app_spec.code)["app_id"]

    # In ra log triển khai thành công
    logger.info(
        f"Đã triển khai {app_spec.contract.name} (ID ứng dụng: {app_id}) "
        f"trên mạng chính (mainnet)"
    )