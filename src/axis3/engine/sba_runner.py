# axis3/engine/sba_runner.py

from axis3.rules.sba.rules import run_sbas as sba_core

def run_sbas(game_state):
    """
    Wrapper for SBAs.
    """
    sba_core(game_state)
