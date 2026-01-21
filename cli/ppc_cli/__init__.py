"""
pyPPC CLI - Command Line Interface for pyPPC
"""

# CLI version syncs with library version
try:
    from ppc import __version__
except ImportError:
    __version__ = "0.0.0"
