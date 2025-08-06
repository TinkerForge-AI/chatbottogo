from typing import List

def basic_hallucination_detection(response: str, context: List[str]) -> List[str]:
    """
    Checks if response contains facts not present in the context.
    Returns a list of suspected hallucinated sentences.
    Flags sentences where no significant phrase (3+ words) matches any context sentence.
    """
    import re
    sentences = re.split(r'(?<=[.!?]) +', response)
    hallucinated = []
    context_text = ' '.join(context).lower()
    for sent in sentences:
        sent_clean = sent.strip()
        if not sent_clean:
            continue
        # Look for 3+ word phrases in the sentence that appear in the context
        found = False
        words = sent_clean.split()
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3]).lower()
            if phrase in context_text:
                found = True
                break
        if not found:
            hallucinated.append(sent)
    return hallucinated
