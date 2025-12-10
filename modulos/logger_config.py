import logging
import os

# Garante que o diretório de logs existe
os.makedirs("logs", exist_ok=True)

# Configuração básica do logger
logging.basicConfig(
    filename='logs/logs_app.log',
    level=logging.INFO,  # Pode ser DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Exporta o logger principal
logger = logging.getLogger("mt5_logger")