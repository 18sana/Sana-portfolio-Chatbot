from app.evals.harness import evaluate_answer, load_golden_set


def test_golden_set_loads() -> None:
    cases = load_golden_set()
    assert len(cases) >= 3


def test_evaluate_answer_flags_banned() -> None:
    case = load_golden_set()[0]
    failures = evaluate_answer(case, "as an AI language model I think they did RAG")
    assert any(f.startswith("banned:") for f in failures)
