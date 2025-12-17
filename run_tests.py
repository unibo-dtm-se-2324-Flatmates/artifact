import sys
from pathlib import Path

import pytest


if __name__ == "__main__":
    root = Path(__file__).parent
    target = root / "test"
    sys.exit(pytest.main([str(target)]))