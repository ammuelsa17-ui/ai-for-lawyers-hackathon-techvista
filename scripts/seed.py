import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal, init_db
from app.cms.mock_adapter import MockCMSAdapter
from app.db.models import MatterModel, DocumentModel


def seed_database():
    print("Initializing database schema...")
    init_db()

    db = SessionLocal()
    try:
        # Check if already seeded
        existing_matter = db.query(MatterModel).first()
        if existing_matter:
            print(f"Database already seeded with matter: {existing_matter.title} ({existing_matter.id})")
            return

        adapter = MockCMSAdapter(db)
        print("Creating synthetic matter via CMS Adapter (approved_by='attorney_jane')...")
        matter_result = adapter.create_matter(
            title="Acme Corp v. Global Logistics",
            client_name="Acme Corp",
            practice_area="Commercial Litigation",
            approved_by="attorney_jane",
        )
        matter_id = matter_result["matter_id"]
        print(f"Created matter: {matter_id}")

        print("Seeding synthetic documents into documents table...")
        now = datetime.now(timezone.utc)
        doc1 = DocumentModel(
            id=str(uuid.uuid4()),
            matter_id=matter_id,
            file_name="summons_and_complaint.txt",
            file_path="fixtures/summons_and_complaint.txt",
            category="Pleading",
            page_count=5,
            created_at=now,
        )
        doc2 = DocumentModel(
            id=str(uuid.uuid4()),
            matter_id=matter_id,
            file_name="initial_discovery_requests.txt",
            file_path="fixtures/initial_discovery_requests.txt",
            category="Discovery",
            page_count=12,
            created_at=now,
        )
        db.add_all([doc1, doc2])
        db.commit()

        print(f"Seeded 2 documents for matter {matter_id}.")
        print("Database seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
