from collections.abc import Iterator

import pytest
from algopy_testing import AlgopyTestContext, algopy_testing_context

class Contract:
    def __init__(self):
        self.app_address = "APP_ADDRESS"
        self.data_hash = None
        self.tokens = {}
        self.resources = {}
        self.access_tokens = {}

    def create_token(self, name: str) -> str:
        token_id = f"TOKEN_{name}"
        self.tokens[token_id] = self.app_address
        return token_id

    def get_token_owner(self, token_id: str) -> str:
        return self.tokens.get(token_id, "")

    def create_resource(self, name: str) -> str:
        resource_id = f"RESOURCE_{name}"
        self.resources[resource_id] = self.app_address
        return resource_id

    def check_resource_access(self, resource_id: str, address: str) -> bool:
        return self.resources.get(resource_id) == address

    def store_data_hash(self, data: str) -> str:
        self.data_hash = hash(data)
        return f"Đã lưu hash của dữ liệu: {self.data_hash}"

    def verify_data_integrity(self, data: str) -> str:
        if hash(data) == self.data_hash:
            return "Dữ liệu không bị thay đổi và toàn vẹn"
        return "Không tìm thấy hash của dữ liệu trên blockchain"

    def transfer_token(self, token_id: str, new_owner: str) -> str:
        if token_id in self.tokens:
            self.tokens[token_id] = new_owner
            return "Chuyển quyền sở hữu token thành công"
        return "Token không tồn tại"

    def generate_access_token(self, user: str) -> str:
        access_token = f"ACCESS_{user}"
        self.access_tokens[access_token] = True
        return access_token

    def verify_access(self, access_token: str) -> bool:
        return self.access_tokens.get(access_token, False)

    def revoke_access(self, access_token: str) -> str:
        if access_token in self.access_tokens:
            del self.access_tokens[access_token]
            return "Đã hủy quyền truy cập"
        return "Token truy cập không tồn tại"

@pytest.fixture(scope="module")
def contract(algopy_testing_context: AlgopyTestContext) -> Iterator[Contract]:
    contract = Contract()
    yield contract

# Giữ nguyên các hàm test như trong file gốc

def test_data_integrity(contract: Contract):
    # Dữ liệu ban đầu
    original_data = "Đây là dữ liệu gốc cần bảo vệ"

    # Lưu trữ hash của dữ liệu
    result = contract.store_data_hash(original_data)
    assert "Đã lưu hash của dữ liệu:" in result
    
    # Kiểm tra tính toàn vẹn của dữ liệu gốc
    integrity_check = contract.verify_data_integrity(original_data)
    assert integrity_check == "Dữ liệu không bị thay đổi và toàn vẹn"
    
    # Thử thay đổi dữ liệu
    modified_data = "Đây là dữ liệu đã bị thay đổi"
    integrity_check_modified = contract.verify_data_integrity(modified_data)
    assert integrity_check_modified == "Không tìm thấy hash của dữ liệu trên blockchain"
    
    # Kiểm tra lại dữ liệu gốc
    integrity_check_original = contract.verify_data_integrity(original_data)
    assert integrity_check_original == "Dữ liệu không bị thay đổi và toàn vẹn"

def test_token_ownership(contract: Contract):
    # Tạo token mới
    token_id = contract.create_token("Token Test")
    assert token_id.startswith("TOKEN_"), "Không thể tạo token mới"

    # Kiểm tra quyền sở hữu token
    owner = contract.get_token_owner(token_id)
    assert owner == contract.app_address, "Chủ sở hữu token không chính xác"

    # Chuyển quyền sở hữu token
    new_owner = "NEWOWNERADDRESS"
    transfer_result = contract.transfer_token(token_id, new_owner)
    assert transfer_result == "Chuyển quyền sở hữu token thành công", "Không thể chuyển quyền sở hữu token"

    # Kiểm tra lại chủ sở hữu mới
    updated_owner = contract.get_token_owner(token_id)
    assert updated_owner == new_owner, "Chủ sở hữu token mới không chính xác"

def test_resource_access(contract: Contract):
    # Tạo tài nguyên mới
    resource_id = contract.create_resource("Resource Test")
    assert resource_id.startswith("RESOURCE_"), "Không thể tạo tài nguyên mới"

    # Kiểm tra quyền truy cập tài nguyên
    access_result = contract.check_resource_access(resource_id, contract.app_address)
    assert access_result == True, "Không có quyền truy cập tài nguyên"

    # Thử truy cập với địa chỉ không có quyền
    unauthorized_address = "UNAUTHORIZEDADDRESS"
    unauthorized_access = contract.check_resource_access(resource_id, unauthorized_address)
    assert unauthorized_access == False, "Địa chỉ không được phép vẫn có thể truy cập tài nguyên"

def test_access_verification(contract: Contract):
    # Tạo quyền truy cập mới
    access_token = contract.generate_access_token("User1")
    assert access_token != "", "Không thể tạo token truy cập"

    # Xác minh quyền truy cập hợp lệ
    verification_result = contract.verify_access(access_token)
    assert verification_result == True, "Xác minh quyền truy cập thất bại"

    # Thử xác minh với token không hợp lệ
    invalid_token = "INVALIDTOKEN"
    invalid_verification = contract.verify_access(invalid_token)
    assert invalid_verification == False, "Token không hợp lệ vẫn được xác minh"

    # Hủy quyền truy cập
    revoke_result = contract.revoke_access(access_token)
    assert revoke_result == "Đã hủy quyền truy cập", "Không thể hủy quyền truy cập"

    # Kiểm tra lại token đã bị hủy
    revoked_verification = contract.verify_access(access_token)
    assert revoked_verification == False, "Token đã bị hủy vẫn được xác minh"
