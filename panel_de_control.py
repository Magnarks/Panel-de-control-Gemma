import flet as ft
import platform
import psutil
import pynvml
import threading
import subprocess
import sys
import os
import asyncio

# Ruta al Python del sistema (sys.executable en el .exe apunta al runtime bundled de Flet)
_python_exe = r"C:\Users\diego\AppData\Local\Python\pythoncore-3.14-64\python.exe"

async def main(page: ft.Page):
    page.title = "Panel de control de Gemma"
    #page.window.icon = r"C:\Users\diego\Documents\Python\IA\interfaz_gemma\assets\gemma.ico"
    page.window.icon = "gemma.ico"
    page.window.width = 1200
    page.window.height = 900
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#263646"
    page.window.prevent_close = True
    # 1. Datos estáticos del sistema
    os_name = platform.system()
    os_release = platform.release()
    cpu_cores = psutil.cpu_count(logical=False)

    # 2. Elementos visuales reactivos
    cpu_text = ft.Text("Uso de CPU: 0%", size=16)
    cpu_progress = ft.ProgressBar(value=0, color=ft.Colors.BLUE)
    
    ram_text = ft.Text("Uso de RAM: 0%", size=16)
    ram_progress = ft.ProgressBar(value=0, color=ft.Colors.ORANGE)

    gpu_text = ft.Text("Uso de GPU: 0%", size=16)
    gpu_progress = ft.ProgressBar(value=0, color=ft.Colors.PURPLE)

    vram_total_text = ft.Text("Vram Total: 0 GB", size=16)
    vram_total_progress = ft.ProgressBar(value=0, color=ft.Colors.GREEN)

    vram_usada_text = ft.Text("Uso de Vram: 0 GB", size=16)
    vram_usada_progress = ft.ProgressBar(value=0, color=ft.Colors.RED)

    vram_libre_text = ft.Text("Vram Libre: 0 GB", size=16)
    vram_libre_progress = ft.ProgressBar(value=0, color=ft.Colors.YELLOW)

    # 3. Procesos de servicios y paneles de salida
    procesos = {"openwa": None, "gemma": None, "chatbot": None}

    lista_openwa = ft.ListView(height=160, spacing=0, auto_scroll=True)
    panel_openwa = ft.Container(
        content=lista_openwa,
        bgcolor="#0d1117",
        border_radius=8,
        padding=8,
        visible=False,
        border=ft.Border.all(1, ft.Colors.GREEN_700),
    )

    lista_gemma = ft.ListView(height=160, spacing=0, auto_scroll=True)
    panel_gemma = ft.Container(
        content=lista_gemma,
        bgcolor="#0d1117",
        border_radius=8,
        padding=8,
        visible=False,
        border=ft.Border.all(1, ft.Colors.BLUE_700)
    )

    lista_chatbot = ft.ListView(height=160, spacing=0, auto_scroll=True)
    panel_chatbot = ft.Container(
        content=lista_chatbot,
        bgcolor="#0d1117",
        border_radius=8,
        padding=8,
        visible=False,
        border=ft.Border.all(1, ft.Colors.PURPLE_700),
    )

    def leer_salida(proceso, lista, panel, color):
        panel.visible = True
        page.update()
        try:
            for linea in proceso.stdout:
                lista.controls.append(
                    ft.Text(linea.rstrip(), size=11, color=color, selectable=True, font_family="monospace")
                )
                page.update()
        except Exception:
            pass

    def terminar_proceso(clave):
        """Mata el proceso y todos sus procesos hijos en Windows."""
        proc = procesos.get(clave)
        if proc is None:
            return
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass
        procesos[clave] = None

    def toggle_openwa(e):
        if e.control.value:
            lista_openwa.controls.clear()
            procesos["openwa"] = subprocess.Popen(
                "npm run dev",
                cwd=r"C:\Users\diego\Documents\Javascript\OpenWA\OpenWA",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            threading.Thread(
                target=leer_salida,
                args=(procesos["openwa"], lista_openwa, panel_openwa, ft.Colors.GREEN_300),
                daemon=True,
            ).start()
        else:
            terminar_proceso("openwa")
            panel_openwa.visible = False
            page.update()

    def toggle_gemma(e):
        cmd = (
            'llama-server '
            '--model "C:\\Users\\diego\\.cache\\huggingface\\hub\\models--FreedomAISVR--Gemma-4-12B-it-Uncensored-Heretic-NVFP4-GGUF'
            '\\snapshots\\f720996e52fc1861ede325c5be720a3f6aa42820\\gemma4-12b-heretic-nvfp4.gguf" '
            '--mmproj "C:\\Users\\diego\\.cache\\huggingface\\hub\\models--FreedomAISVR--Gemma-4-12B-it-Uncensored-Heretic-NVFP4-GGUF'
            '\\snapshots\\f720996e52fc1861ede325c5be720a3f6aa42820\\mmproj-gemma-4-12b-heretic-f16.gguf" '
            '--flash-attn on --no-mmap --n-gpu-layers all '
            '--cache-type-k q8_0 --cache-type-v q8_0 --port 11434'
        )
        if e.control.value:
            lista_gemma.controls.clear()
            procesos["gemma"] = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            threading.Thread(
                target=leer_salida,
                args=(procesos["gemma"], lista_gemma, panel_gemma, ft.Colors.BLUE_300),
                daemon=True,
            ).start()
        else:
            terminar_proceso("gemma")
            panel_gemma.visible = False
            page.update()

    def toggle_chatbot(e):
        if e.control.value:
            lista_chatbot.controls.clear()
            env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
            env.pop("PYTHONHOME", None)
            env.pop("PYTHONPATH", None)
            procesos["chatbot"] = subprocess.Popen(
                [_python_exe, r"C:\Users\diego\Documents\Python\IA\chatbot\app_chatbot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            threading.Thread(
                target=leer_salida,
                args=(procesos["chatbot"], lista_chatbot, panel_chatbot, ft.Colors.PURPLE_300),
                daemon=True,
            ).start()
        else:
            terminar_proceso("chatbot")
            panel_chatbot.visible = False
            page.update()

    switch_openwa = ft.Switch(
        label="OpenWA (npm run dev)",
        value=False,
        on_change=toggle_openwa,
        active_color=ft.Colors.GREEN,
    )
    switch_gemma = ft.Switch(
        label="Gemma 4 12B (llama.cpp)",
        value=False,
        on_change=toggle_gemma,
        active_color=ft.Colors.BLUE,
    )
    switch_chatbot = ft.Switch(
        label="Chatbot (app_chatbot.py)",
        value=False,
        on_change=toggle_chatbot,
        active_color=ft.Colors.PURPLE,
    )

    # 4. Cierre limpio de la ventana
    async def handle_window_event(e):
        if e.type == ft.WindowEventType.CLOSE:
            try:
                for clave in list(procesos.keys()):
                    terminar_proceso(clave)
            except Exception:
                pass
            page.window.prevent_close = False
            page.window.close()

    page.window.on_event = handle_window_event

    # 5. Diseño de la interfaz
    col_monitor = ft.Column(
        [
            ft.Text("Monitoreo en Tiempo Real", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Actualización automática cada 5 segundos", size=12, italic=True),
            ft.Divider(),
            ft.Text(f"Sistema Operativo: {os_name} {os_release}"),
            ft.Text(f"Núcleos de CPU Físicos: {cpu_cores}"),
            ft.Divider(),
            cpu_text,
            cpu_progress,
            ft.Container(height=10),
            ram_text,
            ram_progress,
            ft.Container(height=10),
            gpu_text,
            gpu_progress,
            ft.Container(height=10),
            vram_total_text,
            vram_total_progress,
            ft.Container(height=10),
            vram_usada_text,
            vram_usada_progress,
            ft.Container(height=10),
            vram_libre_text,
            vram_libre_progress,
        ],
        expand=True,
    )

    col_servicios = ft.Column(
        [
            ft.Text("Servicios", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            switch_openwa,
            panel_openwa,
            ft.Container(height=6),
            switch_gemma,
            panel_gemma,
            ft.Container(height=6),
            switch_chatbot,
            panel_chatbot,
        ],
        expand=True,
    )

    page.add(
        ft.Container(
            content=ft.Row(
                [col_monitor, ft.VerticalDivider(), col_servicios],
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
            expand=True,
            padding=20,
        )
    )

    # 5. Función en segundo plano para actualizar los datos
    async def monitor_sistema():
        while True:
            try:
                # Obtener métricas reales (cpu_percent con interval bloquea, usamos to_thread)
                cpu_percent = await asyncio.to_thread(lambda: psutil.cpu_percent(interval=1))
                ram_percent = psutil.virtual_memory().percent

                cpu_text.value = f"Uso de CPU: {cpu_percent}%"
                cpu_progress.value = cpu_percent / 100

                ram_text.value = f"Uso de RAM: {ram_percent}%"
                ram_progress.value = ram_percent / 100

                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                uso_gpu = pynvml.nvmlDeviceGetUtilizationRates(handle)
                pynvml.nvmlShutdown()

                gpu_text.value = f"Uso de GPU: {uso_gpu.gpu}%"
                gpu_progress.value = uso_gpu.gpu / 100
                vram_total_text.value = f"VRAM Total: {info.total / 1024**3:.2f} GB"
                vram_usada_text.value = f"VRAM Usada: {info.used / 1024**3:.2f} GB"
                vram_libre_text.value = f"VRAM Libre: {info.free / 1024**3:.2f} GB"

                vram_total_progress.value = info.total / info.total
                vram_usada_progress.value = info.used / info.total
                vram_libre_progress.value = info.free / info.total

                page.update()
            except Exception:
                pass

            # Pausa de 4s (+ 1s del cpu_percent = 5s totales entre actualizaciones)
            await asyncio.sleep(4)

    # 6. Iniciar el monitor automático como tarea async
    asyncio.create_task(monitor_sistema())

ft.run(main)
