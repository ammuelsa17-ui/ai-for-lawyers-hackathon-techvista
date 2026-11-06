import sqlite3
import pytest


def test_tasks_status_check_constraint(temp_db_path):
    """Assert SQLite CHECK constraint rejects statuses outside ('proposed', 'approved', 'done')."""
    conn = sqlite3.connect(temp_db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()

    # Create a valid matter first
    cursor.execute(
        "INSERT INTO matters (id, title, client_name, practice_area) VALUES (?, ?, ?, ?)",
        ("m1", "Matter 1", "Client A", "Litigation"),
    )
    conn.commit()

    # Valid status inserts
    for valid_status in ("proposed", "approved", "done"):
        cursor.execute(
            """INSERT INTO tasks (id, matter_id, title, due_date, status, source_doc_id, source_chunk_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (f"t_{valid_status}", "m1", "Task Title", "2026-12-01", valid_status, "doc1", "chunk1"),
        )
    conn.commit()

    # Invalid status insert must fail with IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """INSERT INTO tasks (id, matter_id, title, due_date, status, source_doc_id, source_chunk_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("t_bad", "m1", "Task Title", "2026-12-01", "in_progress", "doc1", "chunk1"),
        )
        conn.commit()

    conn.close()


def test_matters_status_check_constraint(temp_db_path):
    """Assert SQLite CHECK constraint rejects matter statuses outside ('open', 'pending', 'closed')."""
    conn = sqlite3.connect(temp_db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO matters (id, title, client_name, practice_area, status) VALUES (?, ?, ?, ?, ?)",
            ("m_invalid", "Matter Invalid", "Client B", "Corporate", "archived"),
        )
        conn.commit()

    conn.close()


def test_foreign_key_enforcement(temp_db_path):
    """Assert PRAGMA foreign_keys = ON prevents inserting a task with a non-existent matter_id."""
    conn = sqlite3.connect(temp_db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """INSERT INTO tasks (id, matter_id, title, due_date, status, source_doc_id, source_chunk_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("t_orphan", "non_existent_matter_id", "Title", "2026-12-01", "proposed", "doc1", "chunk1"),
        )
        conn.commit()

    conn.close()


def test_audit_log_immutability_triggers(temp_db_path):
    """Assert database triggers prevent UPDATE and DELETE operations on audit_log."""
    conn = sqlite3.connect(temp_db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()

    # Insert an audit log entry
    cursor.execute(
        """INSERT INTO audit_log (id, matter_id, actor, action, target_type, target_id, payload)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("a1", "m1", "attorney_jane", "create_matter", "matter", "m1", '{"test": true}'),
    )
    conn.commit()

    # Attempt UPDATE -> must raise IntegrityError with trigger message
    with pytest.raises(sqlite3.IntegrityError, match="audit_log is append-only"):
        cursor.execute("UPDATE audit_log SET actor = ? WHERE id = ?", ("malicious_actor", "a1"))
        conn.commit()

    # Attempt DELETE -> must raise IntegrityError with trigger message
    with pytest.raises(sqlite3.IntegrityError, match="audit_log is append-only"):
        cursor.execute("DELETE FROM audit_log WHERE id = ?", ("a1",))
        conn.commit()

    conn.close()
