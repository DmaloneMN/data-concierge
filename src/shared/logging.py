"""Shared structured logging setup."
import logging

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    # TODO: Configure structured logging / App Insights handler
    return logger
