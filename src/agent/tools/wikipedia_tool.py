import wikipedia


def fetch_wikipedia_summary(topic: str) -> str:
    """
    Fetch the summary of a given topic from Wikipedia.

    Parameters
    ----------
    topic : str
        The topic to search for on Wikipedia.

    Returns
    -------
    str
        The summary of the topic.

    Raises
    ------
    wikipedia.PageError
        If the page for the given topic does not exist.
    wikipedia.DisambiguationError
        If the topic leads to a disambiguation page.
    """
    try:
        page = wikipedia.page(topic)
        return page.summary
    except wikipedia.PageError as e:
        raise e
    except wikipedia.DisambiguationError as e:
        raise e