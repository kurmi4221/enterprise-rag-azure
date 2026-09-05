import json
from pathlib import Path

from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

from backend.app.services.rag_service import ask_rag

from evaluation.azure_deepeval_model import (
    AzureDeepEvalModel,
)


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "rag_test_cases.json"
)


# ============================================================
# Thresholds
# ============================================================

ANSWER_RELEVANCY_THRESHOLD = 0.70
FAITHFULNESS_THRESHOLD = 0.70
CONTEXTUAL_RELEVANCY_THRESHOLD = 0.70


# ============================================================
# Dataset
# ============================================================

def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ============================================================
# Build DeepEval test cases
# ============================================================

def build_test_cases():

    dataset = load_dataset()

    test_cases = []

    for item in dataset:

        question = item["question"]

        print()
        print("=" * 70)
        print(f"Question: {question}")
        print("=" * 70)

        result = ask_rag(question)

        answer = result.get(
            "answer",
            "",
        )

        sources = result.get(
            "sources",
            [],
        )

        retrieval_context = []

        for source in sources:

            content = source.get(
                "content"
            )

            if content:
                retrieval_context.append(
                    content
                )
                continue

            snippet = source.get(
                "snippet"
            )

            if snippet:
                retrieval_context.append(
                    snippet
                )

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        if not retrieval_context:

            for source in sources:

                retrieval_context.append(
                    (
                        f"Document: "
                        f"{source.get('document_name')}\n"
                        f"Page: "
                        f"{source.get('page_number')}\n"
                        f"Chunk: "
                        f"{source.get('chunk_number')}"
                    )
                )

        expected_answer = item.get(
            "expected_answer"
        )

        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            expected_output=expected_answer,
            retrieval_context=retrieval_context,
        )

        test_cases.append(
            test_case
        )

        print(
            f"Answer: {answer}"
        )

        print(
            f"Sources: {len(sources)}"
        )

    return test_cases


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 70)
    print("Enterprise RAG - DeepEval")
    print("=" * 70)

    print()
    print(
        "Initializing Azure DeepEval model..."
    )

    evaluation_model = (
        AzureDeepEvalModel()
    )

    print(
        "Azure DeepEval model initialized."
    )

    # --------------------------------------------------------
    # Build test cases
    # --------------------------------------------------------

    test_cases = build_test_cases()

    print()
    print(
        f"Test cases: {len(test_cases)}"
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    answer_relevancy = (
        AnswerRelevancyMetric(
            threshold=ANSWER_RELEVANCY_THRESHOLD,
            model=evaluation_model,
            include_reason=True,
        )
    )

    faithfulness = (
        FaithfulnessMetric(
            threshold=FAITHFULNESS_THRESHOLD,
            model=evaluation_model,
            include_reason=True,
        )
    )

    contextual_relevancy = (
        ContextualRelevancyMetric(
            threshold=CONTEXTUAL_RELEVANCY_THRESHOLD,
            model=evaluation_model,
            include_reason=True,
        )
    )

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("Running evaluation...")
    print("=" * 70)

    results = evaluate(
        test_cases=test_cases,
        metrics=[
            answer_relevancy,
            faithfulness,
            contextual_relevancy,
        ],
    )

    print()
    print("=" * 70)
    print("DeepEval evaluation completed")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()