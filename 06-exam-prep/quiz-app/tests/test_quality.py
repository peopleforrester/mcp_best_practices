# ABOUTME: Bank-level item-writing quality gates from docs/research/spikes/exam-item-writing.md.
# ABOUTME: Guards the test-wiseness flaws the first draft had: key-as-longest, position bias, recall-only.
from collections import Counter

from mcp_quiz.bank import load_bank


def test_every_question_has_four_unique_options():
    for q in load_bank():
        assert len(q.options) == 4, q.id
        assert len(set(q.options)) == 4, q.id


def test_answer_positions_are_balanced():
    bank = load_bank()
    counts = Counter(q.answer_index for q in bank)
    # All four positions are used, and no single position holds more than 40% of the keys.
    assert set(counts) == {0, 1, 2, 3}
    assert max(counts.values()) <= 0.40 * len(bank)


def test_bank_leans_application_over_recall():
    bank = load_bank()
    application = sum(1 for q in bank if q.cognitive == "application")
    assert application >= 0.5 * len(bank)


def test_correct_answer_is_not_systematically_the_longest():
    # The most common unintended cue: the key being the longest option. It may happen occasionally
    # (some correct answers are naturally longer), but not as a systematic pattern across the bank.
    bank = load_bank()
    key_is_uniquely_longest = 0
    for q in bank:
        longest = max(len(o) for o in q.options)
        if len(q.answer) == longest and sum(len(o) == longest for o in q.options) == 1:
            key_is_uniquely_longest += 1
    assert key_is_uniquely_longest <= 0.40 * len(bank)


def test_every_domain_is_represented():
    domains = {q.domain for q in load_bank()}
    assert {"fundamentals", "architecture", "tooling", "security", "ecosystem"} <= domains


def test_security_is_the_heaviest_domain():
    # Matches the exam blueprint: security carries the most weight.
    counts = Counter(q.domain for q in load_bank())
    assert counts["security"] == max(counts.values())
