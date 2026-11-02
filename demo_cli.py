#!/usr/bin/env python3
"""
JARVIS Autonomous Agent Interactive CLI Demonstration
Menampilkan eksekusi langsung alur Plan -> Execute -> Verify -> Output di terminal.
"""
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint
from app.workflow.engine import AutonomousWorkflowEngine

console = Console()

async def demo_quiz_flow(engine: AutonomousWorkflowEngine):
    console.print("\n[bold cyan]===========================================================[/bold cyan]")
    console.print("[bold yellow]🚀 DEMO 1: EKSEKUSI OTOMATIS SOAL PILIHAN GANDA (PG)[/bold yellow]")
    console.print("[bold cyan]===========================================================[/bold cyan]\n")

    soal_pg = (
        "Soal Pilihan Ganda:\n"
        "Manakah dari pernyataan berikut yang paling tepat mengenai prinsip ACID dalam database relasional?\n"
        "A. Atomicity memastikan transaksi berjalan dengan kecepatan konstan.\n"
        "B. Consistency memastikan database berpindah dari satu kondisi valid ke kondisi valid lainnya sesuai constraint.\n"
        "C. Isolation mengharuskan database tidak boleh diakses oleh lebih dari satu user per hari.\n"
        "D. Durability berarti data disimpan hanya di RAM untuk performa tinggi."
    )

    console.print(Panel(soal_pg, title="[green]Input Soal Pengguna[/green]", border_style="green"))
    
    with console.status("[bold green]JARVIS sedang memproses (Plan -> Execute -> Verify)...[/bold green]"):
        state = await engine.run(user_input=soal_pg, session_id="demo_quiz_session")

    # Tampilkan logs
    table = Table(title="Alur Eksekusi Agen", show_header=True, header_style="bold magenta")
    table.add_column("Langkah", style="cyan", width=12)
    table.add_column("Aktivitas Internal", style="white")
    for idx, log in enumerate(state.execution_logs, 1):
        table.add_row(f"Step {idx}", log)
    console.print(table)

    console.print("\n[bold green]Hasil Akhir Disintesis & Terverifikasi:[/bold green]")
    console.print(Markdown(state.final_output))


async def demo_essay_flow(engine: AutonomousWorkflowEngine):
    console.print("\n[bold cyan]===========================================================[/bold cyan]")
    console.print("[bold yellow]🚀 DEMO 2: EKSEKUSI OTOMATIS RISET & PENULISAN ESAI[/bold yellow]")
    console.print("[bold cyan]===========================================================[/bold cyan]\n")

    instruksi_esai = (
        "Tolong buatkan esai akademis mendalam mengenai: "
        "'Penerapan Autonomous AI Agents dan Self-Correction Feedback Loop dalam Pengembangan Perangkat Lunak'."
    )

    console.print(Panel(instruksi_esai, title="[green]Instruksi Penulisan Esai[/green]", border_style="green"))

    with console.status("[bold green]JARVIS sedang meriset, menyusun outline, dan menulis draf...[/bold green]"):
        state = await engine.run(user_input=instruksi_esai, session_id="demo_essay_session")

    console.print("\n[bold green]Hasil Akhir Disintesis & Terverifikasi:[/bold green]")
    console.print(Markdown(state.final_output))


async def demo_coding_flow(engine: AutonomousWorkflowEngine):
    console.print("\n[bold cyan]===========================================================[/bold cyan]")
    console.print("[bold yellow]🚀 DEMO 3: EKSEKUSI OTOMATIS TUGAS CODING & UNIT TEST[/bold yellow]")
    console.print("[bold cyan]===========================================================[/bold cyan]\n")

    instruksi_coding = (
        "Tuliskan fungsi Python bernama `process_data` yang menerima list bilangan bulat, "
        "menghitung total, jumlah elemen, dan rata-rata dengan penanganan list kosong. "
        "Sertakan unit test yang memvalidasinya."
    )

    console.print(Panel(instruksi_coding, title="[green]Instruksi Coding[/green]", border_style="green"))

    with console.status("[bold green]JARVIS sedang menulis kode, validasi sintaks AST, dan menguji...[/bold green]"):
        state = await engine.run(user_input=instruksi_coding, session_id="demo_coding_session")

    console.print("\n[bold green]Hasil Akhir Disintesis & Terverifikasi:[/bold green]")
    console.print(Markdown(state.final_output))


async def main():
    engine = AutonomousWorkflowEngine()
    console.print("[bold green]✨ Memulai JARVIS Autonomous Multi-Agent Demonstration ✨[/bold green]")
    
    await demo_quiz_flow(engine)
    await demo_essay_flow(engine)
    await demo_coding_flow(engine)

    console.print("\n[bold blue]Seluruh demo berhasil dijalankan![/bold blue]")

if __name__ == "__main__":
    asyncio.run(main())
