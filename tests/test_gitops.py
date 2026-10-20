"""Commit safety against the actual Git index, including non-Python source files."""
import pytest

from gdn.gitops import GitError, Ops


@pytest.mark.parametrize("path", ["result.json", "site/app.js", ".github/workflows/test.yml", "a file.txt"])
def test_markers_in_the_index_cannot_be_hidden_by_clean_working_text(tmp_path, path):
    ops = Ops(tmp_path)
    ops.git("init", "-q")
    ops.git("config", "user.name", "Test")
    ops.git("config", "user.email", "test@example.invalid")
    p = tmp_path / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> upstream\n")
    ops.git("add", "--", path)
    p.write_text("clean working file\n")
    with pytest.raises(GitError, match="conflict markers"):
        ops.refuse_markers()


def test_unstaged_markers_do_not_block_a_clean_staged_file(tmp_path):
    ops = Ops(tmp_path)
    ops.git("init", "-q")
    p = tmp_path / "data.json"
    p.write_text("{}\n")
    ops.git("add", "data.json")
    p.write_text("<<<<<<< HEAD\n")
    ops.refuse_markers()
