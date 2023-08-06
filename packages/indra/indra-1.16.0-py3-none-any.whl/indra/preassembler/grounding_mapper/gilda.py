"""This module implements a client to the Gilda grounding web service,
and contains functions to help apply it during the course of INDRA assembly."""
import logging
import requests
from urllib.parse import urljoin
from indra.preassembler.grounding_mapper.standardize \
    import standardize_agent_name
from indra.config import get_config, has_config
from .adeft import _get_text_for_grounding

logger = logging.getLogger(__name__)

grounding_service_url = get_config('GILDA_URL') if has_config('GILDA_URL') \
    else 'http://grounding.indra.bio/'


def get_gilda_models(mode='web'):
    """Return a list of strings for which Gilda has a disambiguation model.

    Parameters
    ----------
    mode : Optional[str]
        If 'web', the web service given in the GILDA_URL config setting or
        environmental variable is used. Otherwise, the gilda package is
        attempted to be imported and used. Default: web

    Returns
    -------
    list[str]
        A list of entity strings.
    """
    if mode == 'web':
        res = requests.post(urljoin(grounding_service_url, 'models'))
        models = res.json()
        return models
    else:
        from gilda import get_models
        return get_models()


def ground_agent(agent, txt, context=None, mode='web'):
    """Set the grounding of a given agent, by re-grounding with Gilda.

    This function changes the agent in place without returning a value.

    Parameters
    ----------
    agent : indra.statements.Agent
        The Agent whose db_refs shuld be changed.
    txt : str
        The text by which the Agent should be grounded.
    context : Optional[str]
        Any additional text context to help disambiguate the sense
        associated with txt.
    mode : Optional[str]
        If 'web', the web service given in the GILDA_URL config setting or
        environmental variable is used. Otherwise, the gilda package is
        attempted to be imported and used. Default: web
    """
    if mode == 'web':
        resp = requests.post(urljoin(grounding_service_url, 'ground'),
                             json={'text': txt, 'context': context})
        results = resp.json()
        if results:
            db_refs = {'TEXT': txt,
                       results[0]['term']['db']: results[0]['term']['id']}
            agent.db_refs = db_refs
            standardize_agent_name(agent, standardize_refs=True)
        return results
    else:
        from gilda import ground
        results = ground(txt, context)
        if results:
            db_refs = {'TEXT': txt,
                       results[0].term.db: results[0].term.id}
            agent.db_refs = db_refs
            standardize_agent_name(agent, standardize_refs=True)


def ground_statement(stmt, mode='web'):
    """Set grounding for Agents in a given Statement using Gilda.

    This function modifies the original Statement/Agents in place.

    Parameters
    ----------
    stmt : indra.statements.Statement
        A Statement to ground
    mode : Optional[str]
        If 'web', the web service given in the GILDA_URL config setting or
        environmental variable is used. Otherwise, the gilda package is
        attempted to be imported and used. Default: web
    """
    if stmt.evidence and stmt.evidence[0].text:
        context = stmt.evidence[0].text
    else:
        context = None
    for agent in stmt.agent_list():
        if agent is not None and 'TEXT' in agent.db_refs:
            txt = agent.db_refs['TEXT']
            ground_agent(agent, txt, context, mode=mode)


def ground_statements(stmts, mode='web'):
    """Set grounding for Agents in a list of Statements using Gilda.

    This function modifies the original Statements/Agents in place.

    Parameters
    ----------
    stmts : list[indra.statements.Statement]
        A list of Statements to ground
    mode : Optional[str]
        If 'web', the web service given in the GILDA_URL config setting or
        environmental variable is used. Otherwise, the gilda package is
        attempted to be imported and used. Default: web
    """
    for stmt in stmts:
        ground_statement(stmt, mode)


def run_gilda_disambiguation(stmt, agent, idx, mode='web'):
    """Run Gilda disambiguation on an Agent in a given Statement.

    This function looks at the evidence of the given Statement and attempts
    to look up the full paper or the abstract for the evidence. If both of
    those fail, the evidence sentence itself is used for disambiguation.
    The disambiguation model corresponding to the Agent text is then called,
    and the highest scoring returned grounding is set as the Agent's new
    grounding.

    The Statement's annotations as well as the Agent are modified in place
    and no value is returned.

    Parameters
    ----------
    stmt : indra.statements.Statement
        An INDRA Statement in which the Agent to be disambiguated appears.
    agent : indra.statements.Agent
        The Agent (potentially grounding mapped) which we want to
        disambiguate in the context of the evidence of the given Statement.
    idx : int
        The index of the new Agent's position in the Statement's agent list
        (needed to set annotations correctly).
    mode : Optional[str]
        If 'web', the web service given in the GILDA_URL config setting or
        environmental variable is used. Otherwise, the gilda package is
        attempted to be imported and used. Default: web

    Returns
    -------
    bool
        True if disambiguation was successfully applied, and False otherwise.
        Reasons for a False response can be the lack of evidence as well as
        failure to obtain text for grounding disambiguation.
    """
    success = False
    # If the Statement doesn't have evidence for some reason, then there is
    # no text to disambiguate by
    # NOTE: we might want to try disambiguating by other agents in the
    # Statement
    if not stmt.evidence:
        return False
    # Initialize annotations if needed so predicted
    # probabilities can be added to Agent annotations
    annots = stmt.evidence[0].annotations
    agent_txt = agent.db_refs['TEXT']
    if 'agents' in annots:
        if 'gilda' not in annots['agents']:
            annots['agents']['gilda'] = \
                [None for _ in stmt.agent_list()]
    else:
        annots['agents'] = {'gilda': [None for _ in stmt.agent_list()]}
    grounding_text = _get_text_for_grounding(stmt, agent_txt)
    if grounding_text:
        gilda_result = ground_agent(agent, agent_txt, grounding_text, mode)
        if gilda_result:
            logger.info('Disambiguated %s to: %s' %
                        (agent_txt, agent.name))
            annots['agents']['gilda'][idx] = gilda_result
            success = True
    return success
