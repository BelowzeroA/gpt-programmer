from comm_detector import VagueNarrativeCommunicationModel

class VagueNarrativeNoNamesModel(VagueNarrativeCommunicationModel):
    def predict_narrative(self, narrative: str) -> bool:
        """
        For debugging purposes
        """
        if len(narrative) > self.LENGTH_THRESHOLD:
            return False
        is_communication = self.narrative_matches(narrative.lower())
        if not is_communication:
            return False
        names = self.names_extractor.extract(narrative)
        return len(names) == 0

def main():
    pass

if __name__ == "__main__":
    main()