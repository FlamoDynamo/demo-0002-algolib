from algopy import ARC4Contract, String
from algopy.arc4 import abimethod
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
# Xóa import Crypto.Util.Padding vì không cần thiết nữa
import base64
from algosdk import abi
from algosdk.abi import UintType


class Contract(ARC4Contract):
    resources = {}

    def __init__(self):
        super().__init__()
        self.access_rights = {}  # Biến trạng thái cho quyền truy cập
        self.resource_owners = {}  # Biến trạng thái cho quyền sở hữu tài nguyên
        self.user_tokens = {}  # Biến trạng thái cho quản lý token

    @abimethod()
    def add_resource(self, resource_id: String, resource_data: String) -> String:
        """Thêm tài nguyên mới"""
        self.resources[resource_id] = resource_data
        return "Đã thêm tài nguyên thành công"

    @abimethod()
    def access_resource(self, resource_id: String, user_token: String) -> String:
        """Truy cập tài nguyên"""
        if self.verify_token(user_token):
            if resource_id in self.resources:
                return self.resources[resource_id]
            else:
                return "Tài nguyên không tồn tại"
        else:
            return "Không có quyền truy cập"

    def verify_token(self, token: String) -> bool:
        """Xác thực token của người dùng"""
        # Triển khai logic xác thực token
        import hashlib
        import time
        
        # Tạo một chuỗi ngẫu nhiên dựa trên thời gian hiện tại
        random_string = str(time.time()).encode('utf-8')
        
        # Tạo một token ngẫu nhiên bằng cách mã hóa chuỗi ngẫu nhiên
        valid_token = hashlib.sha256(random_string).hexdigest()
        
        # So sánh token nhập vào với token hợp lệ
        return token == valid_token
    
    @abimethod()
    def store_data_hash(self, data: String) -> String:
        """Lưu trữ hash của dữ liệu trên blockchain"""
        import hashlib
        
        # Tạo hash từ dữ liệu
        data_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
        
        # Lưu hash vào blockchain
        self.resources[data_hash] = data
        
        return f"Đã lưu hash của dữ liệu: {data_hash}"

    @abimethod()
    def verify_data_integrity(self, data: String) -> String:
        """Xác minh tính toàn vẹn của dữ liệu"""
        import hashlib
        
        # Tạo hash từ dữ liệu đầu vào
        data_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
        
        # Kiểm tra xem hash có tồn tại trong blockchain không
        if data_hash in self.resources:
            stored_data = self.resources[data_hash]
            if stored_data == data:
                return "Dữ liệu không bị thay đổi và toàn vẹn"
            else:
                return "Dữ liệu đã bị thay đổi"
        else:
            return "Không tìm thấy hash của dữ liệu trên blockchain"
        
    @abimethod()
    def set_resource_owner(self, resource_id: String, owner_address: String) -> String:
        """Thiết lập quyền sở hữu cho tài nguyên"""
        if self.verify_token(self.token):
            if resource_id in self.resources:
                self.resource_owners[resource_id] = owner_address
                return f"Đã thiết lập quyền sở hữu cho tài nguyên {resource_id}"
            else:
                return "Tài nguyên không tồn tại"
        else:
            return "Không có quyền truy cập"

    @abimethod()
    def set_access_rights(self, resource_id: String, user_address: String, rights: String) -> String:
        """Thiết lập quyền truy cập cho người dùng"""
        if self.verify_token(self.token):
            if resource_id in self.resources:
                if resource_id not in self.access_rights:
                    self.access_rights[resource_id] = {}
                self.access_rights[resource_id][user_address] = rights
                return f"Đã thiết lập quyền truy cập {rights} cho người dùng {user_address} đối với tài nguyên {resource_id}"
            else:
                return "Tài nguyên không tồn tại"
        else:
            return "Không có quyền truy cập"

    @abimethod()
    def check_access_rights(self, resource_id: String, user_address: String, action: String) -> String:
        """Kiểm tra quyền truy cập của người dùng"""
        if resource_id in self.resources:
            if resource_id in self.access_rights and user_address in self.access_rights[resource_id]:
                user_rights = self.access_rights[resource_id][user_address]
                if action in user_rights:
                    return f"Người dùng {user_address} có quyền {action} đối với tài nguyên {resource_id}"
                else:
                    return f"Người dùng {user_address} không có quyền {action} đối với tài nguyên {resource_id}"
            elif user_address == self.resource_owners.get(resource_id):
                return f"Người dùng {user_address} là chủ sở hữu của tài nguyên {resource_id}"
            else:
                return f"Người dùng {user_address} không có quyền truy cập tài nguyên {resource_id}"
        else:
            return "Tài nguyên không tồn tại"
        
    @abimethod()
    def buy_tokens(self, amount: int) -> String:
        """Mua token để truy cập tài nguyên"""
        if amount <= 0:
            return "Số lượng token không hợp lệ"
        
        # Giả sử giá 1 token là 1 Algo
        payment = self.txn.note()
        if payment.amount < amount:
            return "Không đủ Algo để mua token"
        
        self.user_tokens[self.sender] = self.user_tokens.get(self.sender, 0) + amount
        return f"Đã mua thành công {amount} token"

    @abimethod()
    def transfer_tokens(self, recipient: String, amount: int) -> String:
        """Chuyển token cho người dùng khác"""
        if self.sender not in self.user_tokens or self.user_tokens[self.sender] < amount:
            return "Không đủ token để chuyển"
        
        if recipient not in self.user_tokens:
            self.user_tokens[recipient] = 0
        self.user_tokens[self.sender] -= amount
        self.user_tokens[recipient] += amount
        return f"Đã chuyển {amount} token cho {recipient}"

    @abimethod()
    def access_resource(self, resource_id: String, token_amount: int) -> String:
        """Truy cập tài nguyên bằng cách sử dụng token"""
        if resource_id not in self.resources:
            return "Tài nguyên không tồn tại"
        
        if self.sender not in self.user_tokens or self.user_tokens[self.sender] < token_amount:
            return "Không đủ token để truy cập tài nguyên"
        
        # Kiểm tra quyền truy cập
        access_rights = self.check_access_rights(resource_id, self.sender, "read")
        if "không có quyền" in access_rights:
            return "Không có quyền truy cập tài nguyên này"
        
        # Trừ token và cho phép truy cập
        self.user_tokens[self.sender] -= token_amount
        return f"Đã truy cập tài nguyên {resource_id}. Token còn lại: {self.user_tokens[self.sender]}"

    @abimethod()
    def get_token_balance(self) -> int:
        """Lấy số dư token của người dùng"""
        return self.user_tokens.get(self.sender, 0)

    def encrypt_data(self, data: str, key: bytes) -> str:
        """Mã hóa dữ liệu sử dụng AES-GCM"""
        nonce = get_random_bytes(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

    def decrypt_data(self, encrypted_data: str, key: bytes) -> str:
        """Giải mã dữ liệu đã được mã hóa bằng AES-GCM"""
        encrypted_data = base64.b64decode(encrypted_data)
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_data.decode('utf-8')

    @abimethod()
    def add_encrypted_resource(self, resource_id: str, resource_data: str, encryption_key: str) -> str:
        """Thêm tài nguyên mới với dữ liệu được mã hóa"""
        if resource_id in self.resources:
            return "Tài nguyên đã tồn tại"
        
        key = base64.b64decode(encryption_key)
        encrypted_data = self.encrypt_data(resource_data, key)
        self.resources[resource_id] = encrypted_data
        return f"Đã thêm và mã hóa tài nguyên {resource_id}"

    @abimethod()
    def access_encrypted_resource(self, resource_id: str, token_amount: int, encryption_key: str) -> str:
        """Truy cập tài nguyên đã mã hóa bằng cách sử dụng token"""
        if resource_id not in self.resources:
            return "Tài nguyên không tồn tại"
        
        if self.sender not in self.user_tokens or self.user_tokens[self.sender] < token_amount:
            return "Không đủ token để truy cập tài nguyên"
        
        # Kiểm tra quyền truy cập
        access_rights = self.check_access_rights(resource_id, self.sender, "read")
        if "không có quyền" in access_rights:
            return "Không có quyền truy cập tài nguyên này"
        
        # Trừ token và giải mã dữ liệu
        self.user_tokens[self.sender] -= token_amount
        key = base64.b64decode(encryption_key)
        decrypted_data = self.decrypt_data(self.resources[resource_id], key)
        return f"Đã truy cập và giải mã tài nguyên {resource_id}. Nội dung: {decrypted_data}. Token còn lại: {self.user_tokens[self.sender]}"
    
    @abimethod()
    def add_document(self, doc_id: str, title: str, author: str, year: int, field: str, content: str) -> str:
        """Thêm tài liệu mới với thông tin chi tiết"""
        if doc_id in self.resources:
            return "Tài liệu đã tồn tại"
        
        document = {
            "title": title,
            "author": author,
            "year": year,
            "field": field,
            "content": content
        }
        self.resources[doc_id] = document
        
        # Thêm vào các chỉ mục tìm kiếm
        if "index_field" not in self.resources:
            self.resources["index_field"] = {}
        if field not in self.resources["index_field"]:
            self.resources["index_field"][field] = []
        self.resources["index_field"][field].append(doc_id)
        
        if "index_author" not in self.resources:
            self.resources["index_author"] = {}
        if author not in self.resources["index_author"]:
            self.resources["index_author"][author] = []
        self.resources["index_author"][author].append(doc_id)
        
        if "index_year" not in self.resources:
            self.resources["index_year"] = {}
        if year not in self.resources["index_year"]:
            self.resources["index_year"][year] = []
        self.resources["index_year"][year].append(doc_id)
        
        return f"Đã thêm tài liệu {doc_id} thành công"

    @abimethod()
    def search_documents(self, field: str = None, author: str = None, year: int = None) -> str:
        """Tìm kiếm tài liệu dựa trên các tiêu chí"""
        results = set()
        
        if field and "index_field" in self.resources and field in self.resources["index_field"]:
            results.update(self.resources["index_field"][field])
        
        if author and "index_author" in self.resources and author in self.resources["index_author"]:
            if results:
                results.intersection_update(self.resources["index_author"][author])
            else:
                results.update(self.resources["index_author"][author])
        
        if year and "index_year" in self.resources and year in self.resources["index_year"]:
            if results:
                results.intersection_update(self.resources["index_year"][year])
            else:
                results.update(self.resources["index_year"][year])
        
        if not results:
            return "Không tìm thấy tài liệu phù hợp"
        
        result_str = "Các tài liệu phù hợp:\n"
        for doc_id in results:
            doc = self.resources[doc_id]
            result_str += f"ID: {doc_id}, Tiêu đề: {doc['title']}, Tác giả: {doc['author']}, Năm: {doc['year']}, Lĩnh vực: {doc['field']}\n"
        
        return result_str

    @abimethod()
    def get_document_content(self, doc_id: str) -> str:
        """Lấy nội dung của tài liệu"""
        if doc_id not in self.resources:
            return "Tài liệu không tồn tại"
        
        return f"Nội dung của tài liệu {doc_id}: {self.resources[doc_id]['content']}"

    @abimethod()
    def create_token(self, name: abi.String) -> UintType(64):
        # Triển khai logic tạo token ở đây
        # Ví dụ:
        token_id = self._generate_token_id()  # Giả sử đây là một phương thức nội bộ tạo ID
        # Lưu thông tin token vào storage
        self._store_token_info(token_id, name)
        return UintType(64)(token_id)

    @abimethod()
    def get_token_owner(self, token_id: UintType(64)) -> abi.Address:
        # Triển khai logic lấy chủ sở hữu token
        # Ví dụ:
        owner = self._get_token_owner(token_id.value)
        return abi.Address(owner)

    @abimethod()
    def create_resource(self, name: abi.String) -> UintType(64):
        # Triển khai logic tạo tài nguyên
        resource_id = self._generate_resource_id()
        self._store_resource_info(resource_id, name)
        return UintType(64)(resource_id)

    @abimethod()
    def check_resource_access(self, resource_id: UintType(64), address: abi.Address) -> abi.Bool:
        # Triển khai logic kiểm tra quyền truy cập
        has_access = self._check_access(resource_id.value, address.value)
        return abi.Bool(has_access)