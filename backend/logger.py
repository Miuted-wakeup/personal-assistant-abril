import logging
import colorlog
from backend.config import LOG_LEVEL

def setup_logger(name):
    # configura consola con colores
    logger = colorlog.getLogger(name)
    
    if not logger.hasHandlers():
        logger.setLevel(LOG_LEVEL)
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={'DEBUG':'cyan','INFO':'green','WARNING':'yellow','ERROR':'red','CRITICAL':'red,bg_white'}
        ))
        logger.addHandler(handler)
        
    return logger
