"""files.py: a write that died halfway is repaired, and no temp file is left behind."""
import gzip

from gdn.files import gz_bytes, write_gz, write_text


def test_a_truncated_gz_is_rewritten(tmp_path):
    p = tmp_path / "MASTER.txt.gz"
    p.write_bytes(gz_bytes(b"x" * 1000)[:20])
    write_gz(p, b"y" * 1000)
    assert gzip.decompress(p.read_bytes()) == b"y" * 1000


def test_a_corrupt_gz_is_rewritten(tmp_path):
    p = tmp_path / "MASTER.txt.gz"
    b = bytearray(gz_bytes(b"x" * 1000))
    b[12:20] = b"\xff" * 8
    p.write_bytes(bytes(b))
    write_gz(p, b"y" * 1000)
    assert gzip.decompress(p.read_bytes()) == b"y" * 1000


def test_writes_leave_no_temp_file(tmp_path):
    write_text(tmp_path / "a.json", "{}\n")
    write_gz(tmp_path / "b.txt.gz", b"z")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.json", "b.txt.gz"]
