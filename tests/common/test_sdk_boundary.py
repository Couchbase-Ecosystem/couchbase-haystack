import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "couchbase_haystack"
# Couchbase SDK packages that are implementation details and move between SDK releases
# (couchbase.logic was removed in 4.7.0). Import from the public modules instead,
# e.g. couchbase.search, couchbase.options, couchbase.cluster.
PRIVATE_SDK_PACKAGES = ("couchbase.logic", "couchbase.common", "couchbase.pycbc_core", "couchbase._")


def _imported_modules(path: Path):
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            yield node.lineno, node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name


@pytest.mark.unit
def test_src_only_imports_public_couchbase_sdk_modules():
    offenders = [
        f"{path.relative_to(SRC.parent)}:{lineno} imports {module}"
        for path in sorted(SRC.rglob("*.py"))
        for lineno, module in _imported_modules(path)
        if module.startswith(PRIVATE_SDK_PACKAGES)
    ]
    assert not offenders, "Private Couchbase SDK imports found:\n" + "\n".join(offenders)
