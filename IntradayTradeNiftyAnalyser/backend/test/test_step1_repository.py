import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.session import SessionLocal
from backend.app.repositories.analytics.learning_repository import (
    LearningRepository,
)


def main():

    db = SessionLocal()

    try:

        repo = LearningRepository(db)

        trade_date = "2026-06-11"

        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)

        summary = repo.get_summary(trade_date)

        print(summary)

        print()

        print("=" * 80)
        print("SUGGESTIONS")
        print("=" * 80)

        suggestions = repo.get_suggestions(trade_date)

        print(f"Total Suggestions: {len(suggestions)}")
        print()

        for suggestion in suggestions:
            print(suggestion)

        print()

        print("=" * 80)
        print("JOB STATUS")
        print("=" * 80)

        job_status = repo.get_job_status(trade_date)

        print(job_status)

    except Exception as ex:

        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)

        print(ex)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()