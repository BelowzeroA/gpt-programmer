import re
import os
import logging
from dataclasses import dataclass

import pandas as pd

from be.common.schemas.verification.new_verification_result import (
    NewViolatedInvoiceLineItemSchema, PredictionsResult
)
from be.common.schemas.verification.new_verification_task import VerificationPredictionTask
from be.inference_service.pipelines.base_extractor import BaseExtractor
from be.inference_service.pipelines.inter_office.names_extractor import NamesExtractor

DEFAULT_ANSWER = {
    "deduct_reason": None,
    "deduct_comment": None,
    "score": 0.0,
}

VIOLATION_FIELDS = ["narrative"]
DEDUCT_REASON = "Vague Narrative"
DEDUCT_COMMENT = ("Revise the narrative to better convey what was done and why; "
                      "be clear and specific, demonstrating necessity of the services.")
LENGTH_THRESHOLD = 90
FALSE_PATTERNS = ["attend", "appear", "travel", "re:", "regarding", "dismissal", "summary", "stipulation",
                  "disclosure", "motion", "agreement", "settlement", "records", " re ", " for ", "strategy"]

logger = logging.getLogger(__name__)

FIRST_GROUP_RULE = "correspondence|communicate|conference|strategize|call|email|correspond|communication|telephone"
_RULES = [
    r'\b(?!for\b)(?:\w+\s+)*?(?:' + FIRST_GROUP_RULE + r')\b(?:\s+\w+){0,3}\s+with\b',
    r'\b(?!for\b)(?:\w+\s+)*?(?:' + FIRST_GROUP_RULE + r')\b(?:\s+\w+){0,1}\s+to\b',
]


class VagueNarrativeCommunicationModel(BaseExtractor):
    VIOLATION_FIELDS = VIOLATION_FIELDS
    DEDUCT_REASON = DEDUCT_REASON

    def __init__(self):
        self.deduct_reason = DEDUCT_REASON
        self.names_extractor = NamesExtractor()
        logger.info(f"Model {self.__class__.__name__} loaded")

    @staticmethod
    def narrative_matches(narrative: str):
        """
        Check if row matches any of the rules
        :param narrative: the narrative
        :return:
        """
        narrative = narrative.lower()
        for rule in _RULES:
            if re.search(rule, narrative, re.IGNORECASE):
                return True
            if rule in narrative:
                return True
        return False

    async def predict(self, task: VerificationPredictionTask) -> PredictionsResult:
        """
        Predicts violations based on rules
        :param task:
        :return:
        """
        time_entries = BaseExtractor.filter_expenses(task.items)
        prebill_rows = self.filter_prebill_rows(time_entries)
        logger.info(
            f"Model name: {self.__class__.__name__} "
            f"Source guidelines: {task.guidelines} "
            f"Guideline: Not Used"
            f"TaskId {task.meta.task_id} "
            f"DocumentID: {task.meta.doc_id}"
        )

        if not prebill_rows:
            logger.info("Violations predictions: 0. No rows to process")
            return PredictionsResult(
                model_name=self.__class__.__name__,
                items=[],
                errors=None,
            )

        predictions = []
        for i, row in enumerate(prebill_rows):
            if not row.is_potential_violation:
                continue

            violation = self.predict_narrative(row.narrative)
            if violation:
                prediction = NewViolatedInvoiceLineItemSchema(
                    score=0.999,
                    deduct_reason=self.deduct_reason,
                    deduct_comment=DEDUCT_COMMENT,
                    line_item_ids=[row.line_item_id],
                    violated_fields=self.VIOLATION_FIELDS
                )
                predictions.append(prediction)

        violation_counter = sum([1 for i in predictions if i.deduct_reason is not None])
        logger.info(f"Violation predictions: {violation_counter}")
        return PredictionsResult(
            model_name=self.__class__.__name__,
            items=predictions,
            errors=None,
        )

    def predict_narrative(self, narrative: str) -> bool:
        """
        For debugging purposes
        """
        if len(narrative) > LENGTH_THRESHOLD:
            return False
        is_communication = self.narrative_matches(narrative.lower())
        if not is_communication:
            return False
        return True

def main():
    pass

if __name__ == "__main__":
    main()