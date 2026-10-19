"""No test may reach the network: any socket connection to a host other than 127.0.0.1 raises."""
import socket
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests/fixtures"

_connect = socket.socket.connect
_connect_ex = socket.socket.connect_ex


def _host(address):
    return address[0] if isinstance(address, tuple) else None


def _check(sock, address):
    if sock.family in (socket.AF_INET, socket.AF_INET6) and _host(address) not in ("127.0.0.1",):
        raise RuntimeError(f"network blocked in tests: {address!r}")


def _guarded_connect(self, address):
    _check(self, address)
    return _connect(self, address)


def _guarded_connect_ex(self, address):
    _check(self, address)
    return _connect_ex(self, address)


socket.socket.connect = _guarded_connect
socket.socket.connect_ex = _guarded_connect_ex


@pytest.fixture
def faa_texts():
    from gdn import faa
    return {k: (FIXTURES / "faa" / f"{k}.txt").read_bytes().decode("utf-8", errors="replace") for k in faa.FILES}
