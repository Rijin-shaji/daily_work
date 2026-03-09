def generate_response(query, candidates):

    prompt = f"""
    Query: {query}

    Candidates:
    {candidates}

    Rank the best candidates.
    """

    # temporary response
    return f"Processed query: {query}"