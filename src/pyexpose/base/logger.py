import logging
import asyncssh

def enable_logging():
    """Enable logging for debugging purposes.
    """
    logging.basicConfig(level='DEBUG')
    asyncssh.set_sftp_log_level('DEBUG')
    asyncssh.set_debug_level(2)

logger = logging.getLogger("pyexpose")