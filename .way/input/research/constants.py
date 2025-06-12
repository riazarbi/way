HYPOTHESIS_SCORING_START_DATE = "2025-01-26"
SOURCE_DATASET_ID = "transform_jira"
DESTINATION_DATASET_ID = "jira_llm_outputs"
OUTPUT_TABLE_ID = "hypothesis_scoring_results"
EVALUATION_TEST_TABLE_ID = "hypothesis_evaluation_test_results"
INTERMEDIATE_TABLE_ID = "int_hypothesis_scoring_results"
ITERATIONS = 10
BIGQUERY_DATASET_LOCATION = "EU"
HYPOTHESIS_BATCH_SIZE = 20

GEMINI_CONFIG = {
    "temperature": 0,
    "top_k": 1,
    "top_p": 1,
    "candidate_count": 1,
    "max_output_tokens": 250,
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "OBJECT",
        "properties": {
                "score": {"type": "STRING"},
                "justification": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "strengths": {"type": "STRING"},
                            "weaknesses": {"type": "STRING"},
                            "improvements": {"type": "STRING"}
                        }
                    }
                },
            }
    }
}

COSINE_SIMILARITY_LEVELS = {
    "Identical meaning": {
        "threshold": "1.00",
        "description": "Texts are paraphrases or nearly identical.",
    },
    "Very strong similarity": {
        "threshold": "0.85",
        "description": "Same idea, different wording.",
    },
    "Strong similarity": {
        "threshold": "0.70",
        "description": "Similar meaning with different emphasis.",
    },
    "Moderate similarity": {
        "threshold": "0.50",
        "description": "Related topics but not directly paraphrased.",
    },
    "Weak similarity": {
        "threshold": "0.30",
        "description": "Some conceptual overlap, different message.",
    },
    "Little to no similarity": {
        "threshold": "0.00",
        "description": "Unrelated in meaning.",
    }
}
