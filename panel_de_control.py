import flet as ft
import platform
import psutil
import pynvml
import time
import threading

def main(page: ft.Page):
    page.title = "Panel de control de Gemma"
    page.window.width = 800
    page.window.height = 600
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#263646"

    # 1. Datos estáticos del sistema
    os_name = platform.system()
    os_release = platform.release()
    cpu_cores = psutil.cpu_count(logical=False)

    # 2. Elementos visuales reactivos
    cpu_text = ft.Text("Uso de CPU: 0%", size=16)
    cpu_progress = ft.ProgressBar(value=0, color=ft.Colors.BLUE)
    
    ram_text = ft.Text("Uso de RAM: 0%", size=16)
    ram_progress = ft.ProgressBar(value=0, color=ft.Colors.ORANGE)

    vram_total_text = ft.Text("Vram Total: 0 GB", size=16)
    vram_total_progress = ft.ProgressBar(value=0, color=ft.Colors.GREEN)

    vram_usada_text = ft.Text("Uso de Vram: 0 GB", size=16)
    vram_usada_progress = ft.ProgressBar(value=0, color=ft.Colors.RED)

    vram_libre_text = ft.Text("Vram Libre: 0 GB", size=16)
    vram_libre_progress = ft.ProgressBar(value=0, color=ft.Colors.YELLOW)

    # 3. Diseño de la interfaz
    page.add(
        ft.Container(
            content=ft.Column([
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
                vram_total_text,
                vram_total_progress,
                ft.Container(height=10),
                vram_usada_text,
                vram_usada_progress,
                ft.Container(height=10),
                vram_libre_text,
                vram_libre_progress,
            ]),
            padding=20
        )
    )

    # 4. Función en segundo plano para actualizar los datos
    def monitor_sistema():
        while True:
            # Obtener métricas reales
            cpu_percent = psutil.cpu_percent(interval=1) # El intervalo ayuda a medir bien el uso de CPU
            ram_percent = psutil.virtual_memory().percent

            # Modificar los textos y las barras (valores de 0.0 a 1.0)
            cpu_text.value = f"Uso de CPU: {cpu_percent}%"
            cpu_progress.value = cpu_percent / 100

            ram_text.value = f"Uso de RAM: {ram_percent}%"
            ram_progress.value = ram_percent / 100

            pynvml.nvmlInit()

            # Obtener el primer handle de GPU (índice 0)
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)

            print(f"VRAM Total: {info.total / 1024**3:.2f} GB")
            print(f"VRAM Usada: {info.used / 1024**3:.2f} GB")
            print(f"VRAM Libre: {info.free / 1024**3:.2f} GB")

            # Cerrar la conexión
            pynvml.nvmlShutdown()

            vram_total_text.value = f"VRAM Total: {info.total / 1024**3:.2f} GB"
            vram_usada_text.value = f"VRAM Usada: {info.used / 1024**3:.2f} GB"
            vram_libre_text.value = f"VRAM Libre: {info.free / 1024**3:.2f} GB"

            vram_total_progress.value = info.total / info.total
            vram_usada_progress.value = info.used / info.total
            vram_libre_progress.value = info.free / info.total

            # Refrescar la interfaz gráfica
            page.update()

            # Pausa el hilo por 5 segundos antes de la siguiente lectura
            time.sleep(5)

    # 5. Iniciar el monitor automático en un hilo separado
    # daemon=True asegura que el hilo muera si cierras la ventana de la app
    hilo = threading.Thread(target=monitor_sistema, daemon=True)
    hilo.start()

ft.run(main)
