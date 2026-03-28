"""
eval.py — Basic RAG evaluation: checks faithfulness and retrieval relevance.

Run: python eval.py
"""

from chain import ask

# ── Sample test questions ──────────────────────────────────────────────────────
# Replace these with questions relevant to YOUR uploaded documents.
TEST_QUESTIONS = [
    "What are the symptoms of type 2 diabetes?",
    "What is the recommended dosage for metformin?",
    "What are the contraindications for ibuprofen?",
    "How is hypertension diagnosed?",
]


def evaluate():
    print("=" * 60)
    print("MediQuery — Basic Evaluation")
    print("=" * 60)

    results = []

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i}/{len(TEST_QUESTIONS)}] Q: {question}")
        result = ask(question)

        answer = result["answer"]
        sources = result["sources"]

        # Faithfulness check: did the model admit uncertainty?
        grounded = "couldn't find" not in answer.lower()
        has_sources = len(sources) > 0

        # Relevance check: did any retrieved chunk share keywords with the question?
        question_words = set(question.lower().split())
        relevant = any(
            len(question_words & set(doc.page_content.lower().split())) > 2
            for doc in sources
        )

        status = "✓" if (grounded and has_sources and relevant) else "⚠"
        print(f"  Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
        print(f"  Sources retrieved: {len(sources)}")
        print(f"  Relevance check: {'pass' if relevant else 'fail'}")
        print(f"  Status: {status}")

        results.append({
            "question": question,
            "grounded": grounded,
            "has_sources": has_sources,
            "relevant": relevant,
        })

    # Summary
    passed = sum(1 for r in results if r["grounded"] and r["has_sources"] and r["relevant"])
    print("\n" + "=" * 60)
    print(f"Evaluation complete: {passed}/{len(results)} questions passed all checks.")
    print("=" * 60)
    return results


if __name__ == "__main__":
    evaluate()