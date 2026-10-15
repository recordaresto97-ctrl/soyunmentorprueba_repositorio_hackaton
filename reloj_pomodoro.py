import tkinter as tk
from tkinter import ttk, colorchooser
from datetime import datetime
import pygame
from plyer import notification
import time

class PomodoroClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj Digital & Pomodoro")
        self.root.geometry("400x500")
        self.root.configure(bg="#2c3e50")

        # Inicializar Pygame para el sonido
        pygame.mixer.init()

        # Variables de estado
        self.timer_running = False
        self.current_mode = "Concentración" # "Concentración" o "Descanso"
        self.time_left = 30 * 60  # 30 minutos en segundos
        self.focus_time = 30 * 60
        self.break_time = 5 * 60

        # --- Interfaz Gráfica ---
        
        # 1. Reloj Digital
        self.lbl_clock = tk.Label(root, font=("Helvetica", 48), fg="white", bg="#2c3e50")
        self.lbl_clock.pack(pady=20)

        # 2. Sección de Color
        self.btn_color = tk.Button(root, text="Cambiar Color de Fondo", command=self.change_bg_color)
        self.btn_color.pack(pady=10)

        # 3. Sección Pomodoro
        self.lbl_mode = tk.Label(root, text="Modo: Concentración", font=("Helvetica", 18), fg="#ecf0f1", bg="#2c3e50")
        self.lbl_mode.pack(pady=10)

        self.lbl_timer = tk.Label(root, text="30:00", font=("Helvetica", 60, "bold"), fg="#e74c3c", bg="#2c3e50")
        self.lbl_timer.pack(pady=10)

        # Botones de control
        self.btn_frame = tk.Frame(root, bg="#2c3e50")
        self.btn_frame.pack(pady=20)

        self.btn_start = tk.Button(self.btn_frame, text="Iniciar", command=self.toggle_timer, width=10)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_reset = tk.Button(self.btn_frame, text="Reiniciar", command=self.reset_timer, width=10)
        self.btn_reset.grid(row=0, column=1, padx=5)

        # Iniciar actualización del reloj
        self.update_digital_clock()

    # --- Funcionalidades ---

    def update_digital_clock(self):
        """Actualiza la hora actual cada segundo"""
        now = datetime.now().strftime("%H:%M:%S")
        self.lbl_clock.config(text=now)
        self.root.after(1000, self.update_digital_clock)

    def change_bg_color(self):
        """Permite elegir un color de fondo mediante una paleta"""
        color = colorchooser.askcolor(title="Selecciona un color")[1]
        if color:
            self.root.configure(bg=color)
            self.lbl_clock.configure(bg=color)
            self.lbl_mode.configure(bg=color)
            self.lbl_timer.configure(bg=color)
            self.btn_frame.configure(bg=color)

    def toggle_timer(self):
        """Inicia o pausa el temporizador"""
        if not self.timer_running:
            self.timer_running = True
            self.btn_start.config(text="Pausar")
            self.countdown()
        else:
            self.timer_running = False
            self.btn_start.config(text="Iniciar")

    def reset_timer(self):
        """Reinicia el temporizador al estado inicial"""
        self.timer_running = False
        self.btn_start.config(text="Iniciar")
        self.current_mode = "Concentración"
        self.time_left = self.focus_time
        self.update_timer_display()
        self.lbl_mode.config(text="Modo: Concentración")

    def countdown(self):
        """Lógica de cuenta regresiva"""
        if self.timer_running:
            if self.time_left > 0:
                self.time_left -= 1
                self.update_timer_display()
                self.root.after(1000, self.countdown)
            else:
                self.timer_finished()

    def update_timer_display(self):
        """Convierte segundos a formato MM:SS"""
        mins, secs = divmod(self.time_left, 60)
        self.lbl_timer.config(text=f"{mins:02d}:{secs:02d}")

    def timer_finished(self):
        """Acciones al terminar el tiempo"""
        self.timer_running = False
        self.btn_start.config(text="Iniciar")
        
        # Determinar si terminó concentración o descanso
        if self.current_mode == "Concentración":
            msg = "¡Tiempo de concentrarte terminado! Toca un descanso."
            self.current_mode = "Descanso"
            self.time_left = self.break_time
            self.lbl_mode.config(text="Modo: Descanso")
        else:
            msg = "¡Descanso terminado! A volver al trabajo."
            self.current_mode = "Concentración"
            self.time_left = self.focus_time
            self.lbl_mode.config(text="Modo: Concentración")

        # Notificación y Alarma
        self.play_alarm()
        notification.notify(
            title="Pomodoro Alert",
            message=msg,
            app_name="Pomodoro Clock",
            timeout=10
        )
        
        self.update_timer_display()

    def play_alarm(self):
        """Reproduce el archivo de sonido"""
        try:
            pygame.mixer.music.load("alarma.mp3") # Asegúrate de tener este archivo
            pygame.mixer.music.play()
        except:
            print("No se encontró el archivo alarma.mp3, se omitió el sonido.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroClock(root)
    root.mainloop()