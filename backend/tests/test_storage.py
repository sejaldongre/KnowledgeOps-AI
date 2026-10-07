from pathlib import Path

from app.services.storage import LocalStorageService


def test_storage_save_and_get(tmp_path):
    """Verify that files can be saved and retrieved."""

    storage = LocalStorageService(
        base_path=str(tmp_path)
    )

    content = b"Employee Handbook content"

    storage_path = storage.save(
        filename="handbook.pdf",
        content=content,
    )

    assert Path(storage_path).exists()

    retrieved = storage.get(storage_path)

    assert retrieved == content


def test_storage_generates_unique_filename(tmp_path):
    """Verify that stored filenames are unique."""

    storage = LocalStorageService(
        base_path=str(tmp_path)
    )

    first_path = storage.save(
        filename="document.pdf",
        content=b"first",
    )

    second_path = storage.save(
        filename="document.pdf",
        content=b"second",
    )

    assert first_path != second_path


def test_storage_delete(tmp_path):
    """Verify that stored files can be deleted."""

    storage = LocalStorageService(
        base_path=str(tmp_path)
    )

    storage_path = storage.save(
        filename="document.pdf",
        content=b"test",
    )

    assert Path(storage_path).exists()

    storage.delete(storage_path)

    assert not Path(storage_path).exists()
