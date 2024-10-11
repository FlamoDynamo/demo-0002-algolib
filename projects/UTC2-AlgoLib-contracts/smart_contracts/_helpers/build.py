import logging
import subprocess
from pathlib import Path
from shutil import rmtree
from algosdk.v2client.algod import AlgodClient
from pyteal import compileTeal, Mode
from algosdk.abi import Contract

logger = logging.getLogger(__name__)
deployment_extension = "py"

def _get_output_path(output_dir: Path, deployment_extension: str) -> Path:
    return output_dir / Path(
        "{contract_name}"
        + ("_client" if deployment_extension == "py" else "Client")
        + f".{deployment_extension}"
    )

def build(output_dir: Path, contract_path: Path) -> Path:
    output_dir = output_dir.resolve()
    if output_dir.exists():
        rmtree(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"Đang xuất {contract_path} sang {output_dir}")

    # Bước 1: Biên dịch hợp đồng
    build_result = subprocess.run(
        [
            "algokit",
            "--no-color",
            "compile",
            "python",
            contract_path.absolute(),
            f"--out-dir={output_dir}",
            "--output-arc32",
            "--debug-level=0",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if build_result.returncode:
        raise Exception(f"Không thể biên dịch hợp đồng:\n{build_result.stdout}")

    # Bước 2: Kiểm tra tính hợp lệ của các phương thức ABI
    app_spec_file_names = [file.name for file in output_dir.glob("*.arc32.json")]
    for app_spec_file_name in app_spec_file_names:
        with open(output_dir / app_spec_file_name, 'r') as f:
            contract = Contract.from_json(f.read())
        for method in contract.methods:
            if not method.is_valid():
                raise Exception(f"Phương thức ABI không hợp lệ: {method.name}")

    # Bước 3: Kiểm tra trạng thái hợp đồng
    algod_client = AlgodClient("", "http://localhost:4001")
    approval_program = compileTeal(contract.approval_program(), mode=Mode.Application, version=6)
    clear_program = compileTeal(contract.clear_program(), mode=Mode.Application, version=6)
    
    approval_result = algod_client.compile(approval_program)
    clear_result = algod_client.compile(clear_program)
    
    if 'result' not in approval_result or 'result' not in clear_result:
        raise Exception("Không thể biên dịch chương trình approval hoặc clear")

    # Bước 4: Tạo client được định kiểu
    for app_spec_file_name in app_spec_file_names:
        generate_result = subprocess.run(
            [
                "algokit",
                "generate",
                "client",
                output_dir,
                "--output",
                _get_output_path(output_dir, deployment_extension),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if generate_result.returncode:
            if "No such command" in generate_result.stdout:
                raise Exception(
                    "Không thể tạo client được định kiểu, yêu cầu AlgoKit 2.0.0 trở lên. "
                    "Vui lòng cập nhật AlgoKit"
                )
            else:
                raise Exception(
                    f"Không thể tạo client được định kiểu:\n{generate_result.stdout}"
                )

    logger.info("Quá trình build hoàn tất thành công")
    return output_dir / app_spec_file_name
