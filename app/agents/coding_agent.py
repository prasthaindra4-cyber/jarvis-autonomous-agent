import json
import logging
from typing import Any, Dict, Optional
from app.agents.base_agent import BaseAgent
from app.workflow.state import AgentRole
from app.tools.code_executor import CodeExecutorTool

logger = logging.getLogger("jarvis.agents.coding")

class CodingAgent(BaseAgent):
    """
    Spesialis penulisan kode, refactoring, debugging, dan pembuatan unit test.
    Terintegrasi dengan CodeExecutorTool untuk validasi sintaks dan eksekusi mandiri.
    """
    def __init__(self):
        super().__init__(name="CodeEngineerAgent", role=AgentRole.CODING)
        self.executor = CodeExecutorTool()

    async def execute(self, payload: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        instruction = payload.get("instruction") or payload.get("raw_prompt", "")
        language = payload.get("language", "python")

        system_instruction = f"""
        Anda adalah Principal Software Engineer.
        Tugas Anda menulis kode berkualitas tinggi dalam bahasa {language}.
        Kriteria:
        1. Clean Code, modular, dan mengikuti prinsip SOLID.
        2. Dilengkapi Type Hints (untuk Python/TypeScript) dan komentar dokumentasi (docstring).
        3. Wajib menyertakan fungsi unit test (misal `test_...()`) untuk memvalidasi kasus uji.
        4. Analisis kompleksitas waktu dan ruang (Time & Space Complexity).

        Kembalikan output WAJIB dalam format JSON murni:
        {{
          "language": "{language}",
          "code": "Kode program lengkap termasuk unit test di bawahnya",
          "explanation": "Penjelasan arsitektur dan alur logika kode",
          "complexity": {{
            "time": "O(...)",
            "space": "O(...)"
          }}
        }}
        """

        prompt = f"Kebutuhan Kode:\n{instruction}\n\nKonteks Tambahan:\n{context or 'Tidak ada'}"
        raw_output = await self.call_llm(system_instruction, prompt)
        parsed = self.parse_json_safely(raw_output)

        code_str = parsed.get("code", "")
        # Jika kode dalam Python, jalankan validasi AST dan eksekusi test
        execution_report = {"tested": False}
        if language.lower() == "python" and code_str:
            validation = self.executor.validate_syntax(code_str)
            if not validation["is_valid"]:
                parsed["syntax_error"] = validation["error"]
            else:
                exec_res = await self.executor.execute_python(code_str)
                execution_report = {
                    "tested": True,
                    "success": exec_res["success"],
                    "output": exec_res["output"],
                    "error": exec_res["error"]
                }

        parsed["execution_report"] = execution_report
        return parsed
