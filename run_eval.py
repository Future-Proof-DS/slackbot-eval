"""Run the Slackbot eval against your bot.

Loads questions from eval/ground_truth.yaml, calls ask_bot() from connect.py
for each complete question, and checks every answer with checks.py. Prints a
per-question table, the score, and the full answer for each failure.

Usage (from your project root):
    poetry run python eval/run_eval.py
"""

import sys
import textwrap
from pathlib import Path

import yaml
from dotenv import load_dotenv

# eval/ lives inside your project. PROJECT_ROOT is your project.
EVAL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_DIR.parent
# position 1 keeps eval/ first, so a connect.py or checks.py in your project can't shadow the kit's
sys.path.insert(1, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")


def main() -> None:
    # These imports must come after load_dotenv because your bot may create its
    # clients at import time, and those read their keys from the environment.
    from checks import check, describe, is_complete
    from connect import ask_bot

    gt_path = EVAL_DIR / "ground_truth.yaml"
    with gt_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    questions = data["questions"]

    # skip slots the student hasn't finished yet
    ready = [entry for entry in questions if is_complete(entry)]
    skipped = [entry for entry in questions if not is_complete(entry)]

    print(
        f"Loaded {len(questions)} questions ({len(ready)} ready, {len(skipped)} incomplete)."
    )
    if skipped:
        print(
            f"Skipping {len(skipped)} incomplete. Fill in text, kind and the kind's fields in eval/ground_truth.yaml to include them."
        )
    for entry in skipped:
        # a question with text was started, so a typo here would otherwise vanish from the score
        if entry.get("text"):
            print(f"  Check this one: {entry['text']}")
    print()

    if not ready:
        print("No complete questions to evaluate. Fill some in and re-run.")
        return

    print(f"{'#':<4} {'Question':<60} {'Result':>6}")
    print("-" * 72)

    failures = []

    for i, entry in enumerate(ready, start=1):
        question = entry["text"]
        answer = None
        error = None

        try:
            answer = ask_bot(question)
            if not isinstance(answer, str):
                raise TypeError(
                    f"ask_bot must return text, got {type(answer).__name__}"
                )
            passed = check(entry, answer)
        except Exception as exc:  # noqa: BLE001
            # the unfilled stub raises on its first call. Later, it is the bot's own error.
            if i == 1 and isinstance(exc, NotImplementedError):
                print(f"Not connected: {exc}")
                sys.exit(1)
            passed = False
            error = f"{type(exc).__name__}: {exc}"

        if not passed:
            failures.append((i, entry, answer, error))

        text_short = question if len(question) <= 60 else question[:57] + "..."
        print(f"{i:<4} {text_short:<60} {'PASS' if passed else 'FAIL':>6}")

    total = len(ready)
    score = total - len(failures)

    print("-" * 72)
    print(f"Score: {score} of {total} passed ({score / total:.0%})")

    if failures:
        print("\nFailures:")
    for i, entry, answer, error in failures:
        print(f"\n{i}. {entry['text']}")
        print(f"   Expected: {describe(entry)}")
        if error:
            print(f"   Error: {error}")
        else:
            print("   Answer:")
            print(textwrap.indent(answer, "     "))


if __name__ == "__main__":
    main()
