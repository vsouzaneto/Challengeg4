# Makes tests/ importable so test modules can share fixtures/helpers.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
