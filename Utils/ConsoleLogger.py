import sys
import datetime
import os
import sys
import ctypes

kernel32 = ctypes.windll.kernel32
handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
kernel32.SetConsoleMode(handle, 7)   # ENABLE_VIRTUAL_TERMINAL_PROCESSING


class ConsoleLogger:
    LEVELS = {
        'DEBUG': '\033[94m',   # Azul
        'INFO': '\033[92m',    # Verde
        'WARNING': '\033[93m', # Amarillo
        'ERROR': '\033[91m',   # Rojo
        'RESET': '\033[0m'     # Reset de color
    }

    def __init__(self, name="Logger", level="DEBUG"):
        self.name = name
        self.level = level
        self.level_order = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    def _should_log(self, level):
        return self.level_order.index(level) >= self.level_order.index(self.level)

    def _format_message(self, level, message):
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        color = self.LEVELS.get(level, '')
        reset = self.LEVELS['RESET']
        return f"{color}[{timestamp}] [{self.name}] [{level}] {message}{reset}"

    def log(self, level, message):
        if self._should_log(level):
            print(self._format_message(level, message), file=sys.stdout)

    # metodos a utilizar
    def debug(self, message): self.log('DEBUG', message)
    def info(self, message): self.log('INFO', message)
    def warning(self, message): self.log('WARNING', message)
    def error(self, message): self.log('ERROR', message)

"""
    Ejemplo de uso

    logger = ConsoleLogger(name="GameServer", level="INFO")
    
    logger.debug("Este mensaje no se mostrará si el nivel es INFO")
    logger.info("Servidor iniciado correctamente")
    logger.warning("Latencia elevada detectada")
    logger.error("Conexión perdida con el jugador")
"""