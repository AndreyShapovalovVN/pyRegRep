from pathlib import Path
import sys

# Ensure project root is importable in CI environments that run pytest from a different CWD.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

