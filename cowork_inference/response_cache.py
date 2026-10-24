"""Stand in for response_cache.py.

Planned input was prompt/response logs. The Cowork list exposes task
titles and last-activity dates. September has one task, so a repeat
rate is not computable. Prompt text is not stored.
"""

from cowork_inference.ledger import load_snapshot


def cache_report():
    tasks = load_snapshot()["cowork"]["september_tasks"]
    titles = [task["title"] for task in tasks]
    return {
        "script": "response_cache",
        "status": "NOT_EVALUATED",
        "september_task_count": len(tasks),
        "distinct_titles": len(set(titles)),
        "repeat_rate": None,
        "prompt_text_stored": False,
        "reason": (
            "A task title is not a prompt/response pair. "
            "One September task cannot justify a cache."
        ),
    }


if __name__ == "__main__":
    print(cache_report())
