"""
src/utils.py
Utility functions for the Wine Quality ML project.

Includes:
- get_logger(): returns a Prefect logger if available, otherwise falls back to standard Python logging.
"""

import logging

def get_logger():
    """
    Returns a logger instance.

    - If inside a Prefect flow or task, returns the Prefect run logger.
    - If outside Prefect (e.g., during unit tests or CLI usage), returns a standard Python logger.

    This allows all modules to use consistent logging behavior without crashing when Prefect context is missing.

    Returns:
        Logger: Either a Prefect run logger or a standard Python logger.
    """
    try:
        from prefect import get_run_logger
        return get_run_logger()
    except RuntimeError:
        # No active Prefect context; use fallback logger
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("fallback")
