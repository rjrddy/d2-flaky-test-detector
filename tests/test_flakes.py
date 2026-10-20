from flakes import detect, generate


def test_injected_precision_recall_and_permanent_failures():
    history, truth = generate()
    assert detect(history) == truth
    assert "test_25" not in detect(history)


def test_different_commits_are_not_flaky_evidence():
    assert not detect(
        [
            {"test": "a", "sha": "one", "attempt": 0, "outcome": "fail"},
            {"test": "a", "sha": "two", "attempt": 1, "outcome": "pass"},
        ],
        min_flips=1,
    )


def test_insufficient_evidence_is_not_quarantined():
    assert not detect(
        [
            {"test": "a", "sha": "one", "attempt": 0, "outcome": "fail"},
            {"test": "a", "sha": "one", "attempt": 1, "outcome": "pass"},
        ]
    )


def test_deterministic_synthetic_history():
    assert generate() == generate()
