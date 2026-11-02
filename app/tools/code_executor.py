import ast
import asyncio
import sys
import tempfile
import os
from typing import Dict, Any

class CodeExecutorTool:
    """
    Tool untuk memverifikasi sintaks dan mengeksekusi kode program secara aman.
    """
    def __init__(self, timeout_seconds: int = 5):
        self.timeout = timeout_seconds

    def validate_syntax(self, code_str: str) -> Dict[str, Any]:
        """Memeriksa kevalidan sintaks Python menggunakan AST."""
        try:
            ast.parse(code_str)
            return {"is_valid": True, "error": None}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "error": f"SyntaxError pada baris {e.lineno}: {e.msg}"
            }

    async def execute_python(self, code_str: str) -> Dict[str, Any]:
        """
        Mengeksekusi skrip python dalam proses terpisah dengan batas waktu (timeout).
        """
        # 1. Validasi sintaks dulu
        validation = self.validate_syntax(code_str)
        if not validation["is_valid"]:
            return {
                "success": False,
                "output": "",
                "error": validation["error"],
                "exit_code": 1
            }

        # 2. Tulis ke file sementara
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code_str)
            temp_path = f.name

        try:
            # 3. Jalankan subprocess
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    proc.communicate(), timeout=self.timeout
                )
                stdout = stdout_data.decode("utf-8", errors="replace")
                stderr = stderr_data.decode("utf-8", errors="replace")
                exit_code = proc.returncode

                return {
                    "success": exit_code == 0,
                    "output": stdout.strip(),
                    "error": stderr.strip() if exit_code != 0 else None,
                    "exit_code": exit_code
                }
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "success": False,
                    "output": "",
                    "error": f"Eksekusi melebihi batas waktu ({self.timeout} detik).",
                    "exit_code": -1
                }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
