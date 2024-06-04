from comm_detector import VagueNarrativeCommunicationModel

class VagueNarrativeNoSubjectModel(VagueNarrativeCommunicationModel):
    def predict_narrative(self, narrative: str) -> bool:
        if len(narrative) > self.LENGTH_THRESHOLD:
            return False
        is_communication = self.narrative_matches(narrative.lower())
        if not is_communication:
            return False
        if any(pattern in narrative.lower() for pattern in [" re ", " re: ", " regarding "]):
            return False
        return True

def main():
    pass

if __name__ == "__main__":
    main()