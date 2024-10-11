import pytest
from algosdk.v2client import algod, indexer
from algosdk import account, transaction
from algosdk.encoding import decode_address
from algosdk import transaction

@pytest.fixture(scope="module")
def algod_client():
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return algod.AlgodClient(algod_token, algod_address)

@pytest.fixture(scope="module")
def indexer_client():
    indexer_address = "http://localhost:8980"
    indexer_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return indexer.IndexerClient(indexer_token, indexer_address)

@pytest.fixture(scope="module")
def default_account():
    private_key, address = account.generate_account()
    return {"private_key": private_key, "address": address}

@pytest.fixture(scope="module")
def app_id(algod_client):
    # Giả sử app_id đã được tạo trước đó
    return 1  # Thay thế bằng app_id thực tế của bạn

@pytest.fixture(scope="module")
def funded_account(algod_client):
    private_key, address = account.generate_account()
    
    # Cấp tiền cho tài khoản
    params = algod_client.suggested_params()
    txn = transaction.PaymentTxn(algod_client.suggested_params().min_fee, params, address, 1000000)
    signed_txn = txn.sign("Thay thế bằng private key của tài khoản có sẵn Algos")
    tx_id = algod_client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(algod_client, tx_id, 4)
    
    return {"private_key": private_key, "address": address}

def test_resource_access_and_ownership(algod_client, indexer_client, funded_account, app_id):
    # Tạo tài nguyên mới
    resource_name = "Tài nguyên kiểm tra"
    create_resource_txn = transaction.ApplicationNoOpTxn(
        sender=funded_account["address"],
        sp=algod_client.suggested_params(),
        index=app_id,
        app_args=["create_resource", resource_name]
    )
    
    signed_txn = create_resource_txn.sign(funded_account["private_key"])
    tx_id = algod_client.send_transaction(signed_txn)
    result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
    
    # Lấy resource_id từ kết quả giao dịch
    resource_id = result["logs"][0].decode()  # Giải mã chuỗi byte thành chuỗi
    
    # Kiểm tra quyền truy cập
    check_access_txn = transaction.ApplicationNoOpTxn(
        sender=funded_account["address"],
        sp=algod_client.suggested_params(),
        index=app_id,
        app_args=["check_resource_access", resource_id, funded_account["address"]]
    )
    
    signed_txn = check_access_txn.sign(funded_account["private_key"])
    tx_id = algod_client.send_transaction(signed_txn)
    result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
    
    assert result["logs"][0].decode() == "True", "Người dùng không có quyền truy cập tài nguyên"
    
    # Thiết lập quyền sở hữu tài nguyên
    new_owner = account.generate_account()[1]
    set_owner_txn = transaction.ApplicationNoOpTxn(
        sender=funded_account["address"],
        sp=algod_client.suggested_params(),
        index=app_id,
        app_args=["set_resource_owner", resource_id, new_owner]
    )
    
    signed_txn = set_owner_txn.sign(funded_account["private_key"])
    tx_id = algod_client.send_transaction(signed_txn)
    result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
    
    assert b"success" in result["logs"][0], "Không thể thiết lập quyền sở hữu mới cho tài nguyên"
    
    # Kiểm tra lại quyền truy cập với chủ sở hữu mới
    check_new_owner_access_txn = transaction.ApplicationNoOpTxn(
        sender=new_owner,
        sp=algod_client.suggested_params(),
        index=app_id,
        app_args=["check_resource_access", resource_id, new_owner]
    )
    
    signed_txn = check_new_owner_access_txn.sign(account.generate_account()[0])
    tx_id = algod_client.send_transaction(signed_txn)
    result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
    
    assert result["logs"][0].decode() == "True", "Chủ sở hữu mới không có quyền truy cập tài nguyên"