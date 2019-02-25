from flask import current_app as app

def parse_like_term(term):
    """
        Parse search term into (operation, term) tuple. Recognizes operators
        in the beginning of the search term. Case insensitive is the default.

        * = case insensitive (can precede other operators)
        ^ = starts with
        = = exact

        :param term:
            Search term
    """
    if app.settings.get('FLASK').get('ADMIN_CASE_INSENSITIVE_SEARCH'):
        case_insensitive = True
        if term.startswith('*'):
            term = term[1:]
    else:
        case_insensitive = term.startswith('*')
        if case_insensitive:
            term = term[1:]
    # apply operators
    if term.startswith('^'):
        oper = 'startswith'
        term = term[1:]
    elif term.startswith('='):
        oper = 'exact'
        term = term[1:]
    else:
        oper = 'contains'
    # add case insensitive flag
    if case_insensitive:
        oper = 'i' + oper
    return oper, term
