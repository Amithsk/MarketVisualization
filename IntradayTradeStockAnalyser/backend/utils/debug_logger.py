# backend/utils/debug_logger.py

from datetime import datetime
from pprint import pformat
import traceback


DEBUG_MODE = True


def log_step(
    title: str,
):

    if not DEBUG_MODE:
        return

    print("\n" + "=" * 80)

    print(
        f"[PHASE3 DEBUG] "
        f"{title}"
    )

    print("=" * 80)


def log_info(
    label: str,
    value,
):

    if not DEBUG_MODE:
        return

    print(
        f"[INFO] "
        f"{label}: "
        f"{value}"
    )


def log_object(
    label: str,
    obj,
):

    if not DEBUG_MODE:
        return

    print(
        f"\n[OBJECT] "
        f"{label}"
    )

    print(
        pformat(
            obj,
            indent=2,
            width=120,
        )
    )


def log_count(
    label: str,
    items,
):

    if not DEBUG_MODE:
        return

    print(
        f"[COUNT] "
        f"{label}: "
        f"{len(items)}"
    )


def log_error(
    error,
):

    print("\n" + "!" * 80)

    print(
        "[PHASE3 ERROR]"
    )

    print(
        f"Type: "
        f"{type(error).__name__}"
    )

    print(
        f"Message: "
        f"{error}"
    )

    print(
        "\nFULL TRACEBACK:\n"
    )

    traceback.print_exc()

    print("!" * 80)