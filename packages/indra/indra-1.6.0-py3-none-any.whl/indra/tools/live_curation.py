"""This REST service allows real-time curation and belief updates for
a corpus of INDRA Statements."""
import json
import yaml
import boto3
import pickle
import logging
import argparse
from os import path
from pathlib import Path
from flask import Flask, request, jsonify, abort, Response
# Note: preserve EidosReader import as first one from indra
from indra.sources.eidos.reader import EidosReader
from indra.belief import BeliefEngine
from indra.tools import assemble_corpus as ac
from indra.belief.wm_scorer import get_eidos_bayesian_scorer
from indra.statements import stmts_from_json_file, stmts_to_json, \
    stmts_from_json, Statement
from indra.preassembler.hierarchy_manager import YamlHierarchyManager
from indra.preassembler.make_wm_ontologies import wm_ont_url, \
    load_yaml_from_url, rdf_graph_from_yaml


logger = logging.getLogger('live_curation')
app = Flask(__name__)
corpora = {}


default_bucket = 'world-modelers'
default_key_base = 'indra_models'
default_profile = 'wm'
file_defaults = {'raw': 'raw_statements',
                 'sts': 'statements',
                 'cur': 'curations',
                 'meta': 'metadata'}

HERE = Path(path.abspath(__file__)).parent
CACHE = HERE.joinpath('_local_cache')
CACHE.mkdir(exist_ok=True)


def _json_loader(fpath):
    logger.info('Loading json file %s' % fpath)
    with open(fpath, 'r') as f:
        return json.load(f)


def _json_dumper(jsonobj, fpath):
    try:
        logger.info('Saving json object to file %s' % fpath)
        with open(fpath, 'w') as f:
            json.dump(obj=jsonobj, fp=f, indent=1)
        return True
    except Exception as e:
        logger.error('Could not save json')
        logger.exception(e)
        return False


class Corpus(object):
    """Represent a corpus of statements with curation.

    Parameters
    ----------
    statements : list[indra.statement.Statement]
        A list of INDRA Statements to embed in the corpus.
    raw_statements : list[indra.statement.Statement]
        A List of raw statements forming the basis of the statements in
        'statements'.
    aws_name : str
        The name of the profile in the AWS credential file to use. 'default' is
        used by default.

    Attributes
    ----------
    statements : dict
        A dict of INDRA Statements keyed by UUID.
    raw_statements : list
        A list of the raw statements
    curations : dict
        A dict keeping track of the curations submitted so far for Statement
        UUIDs in the corpus.
    meta_data : dict
        A dict with meta data associated with the corpus
    """
    def __init__(self, statements=None, raw_statements=None, meta_data=None,
                 aws_name=default_profile):
        self.statements = {st.uuid: st for st in statements} if statements \
            else {}
        self.raw_statements = raw_statements if raw_statements else []
        self.curations = {}
        self.meta_data = meta_data if meta_data else {}
        self.aws_name = aws_name
        self._s3 = None

    def _get_s3_client(self):
        if self._s3 is None:
            self._s3 = boto3.session.Session(
                profile_name=self.aws_name).client('s3')
        return self._s3

    def __str__(self):
        return 'Corpus(%s -> %s)' % (str(self.statements), str(self.curations))

    def __repr__(self):
        return str(self)

    @classmethod
    def load_from_s3(cls, s3key, aws_name=default_profile,
                     bucket=default_bucket, force_s3_reload=False,
                     raise_exc=False):
        corpus = cls([], aws_name=aws_name)
        corpus.s3_get(s3key, bucket, cache=(not force_s3_reload),
                      raise_exc=raise_exc)
        return corpus

    def s3_put(self, s3key, bucket=default_bucket, cache=True):
        """Push a corpus object to S3 in the form of three json files

        The json files representing the object have S3 keys of the format
        <key_base_name>/<name>/<file>.json

        Parameters
        ----------
        s3key : str
            The key to fetch the json files from. The key is assumed to be
            of the following form: "indra_models/<dirname>/<file>.json" and
            only <dirname> *must* be provided. Any combination of
            including/excluding 'indra_models' and/or <file>.json is
            accepted assuming the file ending '.json' is specified when
            <file>.json is specified.
        bucket : str
            The S3 bucket to upload the Corpus to. Default: 'world-modelers'.
        cache : bool
            If True, also create a local cache of the corpus. Default: True.

        Returns
        -------
        keys : tuple(str)
            A tuple of three strings giving the S3 key to the pushed objects
        """
        s3key = _clean_key(s3key) + '/'
        raw = s3key + file_defaults['raw'] + '.json'
        sts = s3key + file_defaults['sts'] + '.json'
        cur = s3key + file_defaults['cur'] + '.json'
        meta = s3key + file_defaults['meta'] + '.json'
        try:
            s3 = self._get_s3_client()
            # Structure and upload raw statements
            self._s3_put_file(s3, raw, stmts_to_json(self.raw_statements),
                              bucket)

            # Structure and upload assembled statements
            self._s3_put_file(s3, sts, _stmts_dict_to_json(self.statements),
                              bucket)

            # Structure and upload curations
            self._s3_put_file(s3, cur, self.curations, bucket)

            # Upload meta data
            self._s3_put_file(s3, meta, self.meta_data, bucket)

            if cache:
                self._save_to_cache(raw, sts, cur)
            return list((raw, sts, cur))
        except Exception as e:
            logger.exception('Failed to put on s3: %s' % e)
            return None

    @staticmethod
    def _s3_put_file(s3, key, json_obj, bucket=default_bucket):
        """Does the json.dumps operation for the the upload, i.e. json_obj
        must be an object that can be turned into a bytestring using
        json.dumps"""
        logger.info('Uploading %s to S3' % key)
        s3.put_object(Body=json.dumps(json_obj, indent=1),
                      Bucket=bucket, Key=key)

    def _save_to_cache(self, raw=None, sts=None, cur=None, meta=None):
        """Helper method that saves the current state of the provided
        file keys"""
        # Assuming file keys are full s3 keys:
        # <base_name>/<dirname>/<file>.json

        # Raw:
        if raw:
            rawf = CACHE.joinpath(raw.replace(default_key_base + '/', ''))
            if not rawf.is_file():
                rawf.parent.mkdir(exist_ok=True, parents=True)
                rawf.touch(exist_ok=True)
            _json_dumper(jsonobj=stmts_to_json(self.raw_statements),
                         fpath=rawf.as_posix())

        # Assembled
        if sts:
            stsf = CACHE.joinpath(sts.replace(default_key_base + '/', ''))
            if not stsf.is_file():
                stsf.parent.mkdir(exist_ok=True, parents=True)
                stsf.touch(exist_ok=True)
            _json_dumper(jsonobj=_stmts_dict_to_json(self.statements),
                         fpath=stsf.as_posix())

        # Curation
        if cur:
            curf = CACHE.joinpath(cur.replace(default_key_base + '/', ''))
            if not curf.is_file():
                curf.parent.mkdir(exist_ok=True, parents=True)
                curf.touch(exist_ok=True)
            _json_dumper(jsonobj=self.curations, fpath=curf.as_posix())

        # Meta data
        if meta:
            metaf = CACHE.joinpath(meta.replace(default_key_base + '/', ''))
            if not metaf.is_file():
                metaf.parent.mkdir(exist_ok=True, parents=True)
                metaf.touch(exist_ok=True)
            _json_dumper(jsonobj=self.meta_data, fpath=metaf.as_posix())

    def s3_get(self, s3key, bucket=default_bucket, cache=True,
               raise_exc=False):
        """Fetch a corpus object from S3 in the form of three json files

        The json files representing the object have S3 keys of the format
        <s3key>/statements.json and <s3key>/raw_statements.json.

        Parameters
        ----------
        s3key : str
            The key to fetch the json files from. The key is assumed to be
            of the following form: "indra_models/<dirname>/<file>.json" and
            only <dirname> *must* be provided. Any combination of
            including/excluding 'indra_models' and/or <file>.json is
            accepted assuming the file ending '.json' is specified when
            <file>.json is specified.
        bucket : str
            The S3 bucket to fetch the Corpus from. Default: 'world-modelers'.
        cache : bool
            If True, look for corpus in local cache instead of loading it
            from s3. Default: True.
        raise_exc : bool
            If True, raise InvalidCorpusError when corpus failed to load

        """
        s3key = _clean_key(s3key) + '/'
        raw = s3key + file_defaults['raw'] + '.json'
        sts = s3key + file_defaults['sts'] + '.json'
        cur = s3key + file_defaults['cur'] + '.json'
        meta = s3key + file_defaults['meta'] + '.json'
        try:
            logger.info('Loading corpus: %s' % s3key)
            s3 = self._get_s3_client()

            # Get and process raw statements
            raw_stmt_jsons = []
            if cache:
                raw_stmt_jsons = self._load_from_cache(raw)
            if not raw_stmt_jsons:
                raw_stmt_jsons_str = s3.get_object(
                    Bucket=bucket, Key=raw)['Body'].read()
                raw_stmt_jsons = json.loads(raw_stmt_jsons_str)
            self.raw_statements = stmts_from_json(raw_stmt_jsons)

            # Get and process assembled statements from list to dict
            json_stmts = []
            if cache:
                json_stmts = self._load_from_cache(sts)
            if not json_stmts:
                json_stmts = json.loads(s3.get_object(
                    Bucket=bucket, Key=sts)['Body'].read())

            self.statements = _json_to_stmts_dict(json_stmts)

            # Get and process curations if any
            curation_json = {}
            if cache:
                curation_json = self._load_from_cache(cur)
            if not curation_json:
                curation_json = json.loads(s3.get_object(
                    Bucket=bucket, Key=cur)['Body'].read())
            self.curations = curation_json

            meta_json = {}
            try:
                if cache:
                    meta_json = self._load_from_cache(meta)
                if not meta_json:
                    meta_json = json.loads(s3.get_object(
                        Bucket=bucket, Key=meta)['Body'].read())
            except Exception as e:
                logger.warning('No meta data found')
            self.meta_data = meta_json

        except Exception as e:
            if raise_exc:
                raise InvalidCorpusError('Failed to get from s3: %s' % e)
            else:
                logger.warning('Failed to get from s3: %s' % e)

    def upload_curations(self, corpus_id, look_in_cache=False,
                         save_to_cache=False, bucket=default_bucket):
        """Upload the current state of curations for the corpus

        Parameters
        ----------
        corpus_id : str
            The corpus ID of the curations to upload
        look_in_cache : bool
            If True, when no curations are avaialbe check if there are
            curations cached locally. Default: False
        save_to_cache : bool
            If True, also save current curation state to cache. If
            look_in_cache is True, this option will have no effect. Default:
            False.
        bucket : str
            The bucket to upload to. Default: 'world-modelers'.
        """
        # Get curation file key
        file_key = _clean_key(corpus_id) + '/' + \
                   file_defaults['cur'] + '.json'

        # First see if we have any curations, then check in cache if
        # look_in_cache == True
        if self.curations:
            curations = self.curations
        elif look_in_cache:
            curations = self._load_from_cache(file_key)
        else:
            curations = None

        # Only upload if we actually have any curations to upload
        if curations:
            self._s3_put_file(s3=self._get_s3_client(),
                              key=file_key,
                              json_obj=curations,
                              bucket=bucket)

        if self.curations and save_to_cache and not look_in_cache:
            self._save_to_cache(cur=file_key)

    @staticmethod
    def _load_from_cache(file_key):
        # Assuming file_key is cleaned, contains the file name and contains
        # the initial file base name:
        # <base_name>/<dirname>/<file>.json

        # Remove <base_name> and get local path to file
        local_file = CACHE.joinpath(
            '/'.join([s for s in file_key.split('/')[1:]]))

        # Load json object
        if local_file.is_file():
            return _json_loader(local_file.as_posix())
        return None


class InvalidCorpusError(Exception):
    pass


def default_assembly(stmts):
    from indra.belief.wm_scorer import get_eidos_scorer
    from indra.preassembler.hierarchy_manager import get_wm_hierarchies
    hm = get_wm_hierarchies()
    scorer = get_eidos_scorer()
    stmts = ac.run_preassembly(stmts, belief_scorer=scorer,
                               return_toplevel=True,
                               flatten_evidence=True,
                               normalize_equivalences=True,
                               normalize_opposites=True,
                               normalize_ns='WM',
                               flatten_evidence_collect_from='supported_by',
                               poolsize=4,
                               hierarchies=hm)
    stmts = ac.merge_groundings(stmts)
    stmts = ac.merge_deltas(stmts)
    stmts = ac.standardize_names_groundings(stmts)
    return stmts


def _make_wm_ontology():
    return YamlHierarchyManager(load_yaml_from_url(wm_ont_url),
                                rdf_graph_from_yaml, True)


def _clean_key(s3key):
    # Check if default_key_base ('indra_models') is present in key
    s3key = s3key if default_key_base in s3key else \
        default_key_base + '/' + s3key

    # Replace double slashes
    s3key = s3key.replace('//', '/')

    # Ommit file part of key, assume it ends with json if it is present
    s3key = '/'.join([s for s in s3key.split('/')[:-1]]) if \
        s3key.endswith('.json') else s3key

    # Ensure last char in string is not '/'
    s3key = s3key[:-1] if s3key.endswith('/') else s3key

    return s3key


def _stmts_dict_to_json(stmt_dict):
    """Make a json representation from dict of statements

    This function is the inverse of _json_to_stmts_dict()

    Parameters
    ----------
    stmt_dict : dict
        Dict with statements keyed by their uuid's: {uuid: stmt}

    Returns
    -------
    list(json)
        A list of json statements
    """
    return [s.to_json() for _, s in stmt_dict.items()]


def _json_to_stmts_dict(stmt_jsons):
    """Return dict of statements keyed by uuid's from json statements

    This function is the inverse of _stmts_dict_to_json()

    Parameters
    ----------
    stmt_jsons : list(json)
        A list of json statements

    Returns
    -------
    dict
        Dict with statements keyed by their uuid's: {uuid: stmt}
    """
    loaded_stmts = [Statement._from_json(s) for s in stmt_jsons]
    return {s.uuid: s for s in loaded_stmts}


class LiveCurator(object):
    """Class coordinating the real-time curation of a corpus of Statements.

    Parameters
    ----------
    scorer : indra.belief.BeliefScorer
        A scorer object to use for the curation
    corpora : dict[str, Corpus]
        A dictionary mapping corpus IDs to Corpus objects.
    """

    def __init__(self, scorer=None, corpora=None):
        self.corpora = corpora if corpora else {}
        self.scorer = scorer if scorer else get_eidos_bayesian_scorer()
        self.ont_manager = _make_wm_ontology()
        self.eidos_reader = EidosReader()

    # TODO: generalize this to other kinds of scorers
    def reset_scorer(self):
        """Reset the scorer used for curation."""
        logger.info('Resetting the scorer')
        self.scorer = get_eidos_bayesian_scorer()
        for corpus_id, corpus in self.corpora.items():
            corpus.curations = {}

    def get_corpus(self, corpus_id, check_s3=False, use_cache=True):
        """Return a corpus given an ID.

        If the corpus ID cannot be found, an InvalidCorpusError is raised.

        Parameters
        ----------
        corpus_id : str
            The ID of the corpus to return.
        check_s3 : bool
            If True, look on S3 for the corpus if it's not currently loaded.
            Default: False.
        use_cache : bool
            If True, look in local cache before trying to find corpus on s3.
            If True while check_s3 if False, this option will be ignored.
            Default: False.

        Returns
        -------
        Corpus
            The corpus with the given ID.
        """
        logger.info('Getting corpus "%s"' % corpus_id)
        corpus = self.corpora.get(corpus_id)
        if check_s3 and corpus is None:
            logger.info('Corpus not loaded, looking on S3')
            corpus = Corpus.load_from_s3(s3key=corpus_id,
                                         force_s3_reload=not use_cache,
                                         raise_exc=True)
            logger.info('Adding corpus to loaded corpora')
            self.corpora[corpus_id] = corpus

            # Run update beliefs. The belief update needs to be inside this
            # if statement to avoid infinite recursion
            beliefs = self.update_beliefs(corpus_id)
        elif corpus is None:
            raise InvalidCorpusError

        return corpus

    def submit_curation(self, corpus_id, curations):
        """Submit correct/incorrect curations fo a given corpus.

        Parameters
        ----------
        corpus_id : str
            The ID of the corpus to which the curations apply.
        curations : dict
            A dict of curations with keys corresponding to Statement UUIDs and
            values corresponding to correct/incorrect feedback.
        """
        logger.info('Submitting curations for corpus "%s"' % corpus_id)
        corpus = self.get_corpus(corpus_id, check_s3=True, use_cache=True)
        # Start tabulating the curation counts
        prior_counts = {}
        subtype_counts = {}
        # Take each curation from the input
        for uuid, correct in curations.items():
            # Save the curation in the corpus
            # TODO: handle already existing curation
            stmt = corpus.statements.get(uuid)
            if stmt is None:
                logger.warning('%s is not in the corpus.' % uuid)
                continue
            corpus.curations[uuid] = correct
            # Now take all the evidences of the statement and assume that
            # they follow the correctness of the curation and contribute to
            # counts for their sources
            for ev in stmt.evidence:
                # Make the index in the curation count list
                idx = 0 if correct else 1
                extraction_rule = ev.annotations.get('found_by')
                # If there is no extraction rule then we just score the source
                if not extraction_rule:
                    try:
                        prior_counts[ev.source_api][idx] += 1
                    except KeyError:
                        prior_counts[ev.source_api] = [0, 0]
                        prior_counts[ev.source_api][idx] += 1
                # Otherwise we score the specific extraction rule
                else:
                    try:
                        subtype_counts[ev.source_api][extraction_rule][idx] \
                            += 1
                    except KeyError:
                        if ev.source_api not in subtype_counts:
                            subtype_counts[ev.source_api] = {}
                        subtype_counts[ev.source_api][extraction_rule] = [0, 0]
                        subtype_counts[ev.source_api][extraction_rule][idx] \
                            += 1
        # Finally, we update the scorer with the new curation counts
        self.scorer.update_counts(prior_counts, subtype_counts)

    def save_curation(self, corpus_id, save_to_cache=True):
        """Save the current state of curations for a corpus given its ID

        If the corpus ID cannot be found, an InvalidCorpusError is raised.

        Parameters
        ----------
        corpus_id : str
            the ID of the corpus to save the
        save_to_cache : bool
            If True, also save the current curation to the local cache.
            Default: True.
        """
        # Do NOT use cache or S3 when getting the corpus, otherwise it will
        # overwrite the current corpus
        logger.info('Saving curations for corpus "%s"' % corpus_id)
        corpus = self.get_corpus(corpus_id, check_s3=False, use_cache=False)
        corpus.upload_curations(corpus_id, save_to_cache=save_to_cache)

    def update_metadata(self, corpus_id, meta_data, save_to_cache=True):
        """Update the meta data for a given corpus

        Parameters
        ----------
        corpus_id : str
            The ID of the corpus to update the meta data for
        meta_data : dict
            A json compatible dict containing the meta data
        save_to_cache : bool
            If True, also update the local cache of the meta data dict.
            Default: True.
        """
        logger.info('Updating meta data for corpus "%s"' % corpus_id)
        corpus = self.get_corpus(corpus_id, check_s3=True, use_cache=True)

        # Loop and add/overwrite meta data key value pairs
        for k, v in meta_data.items():
            corpus.meta_data[k] = v

        if save_to_cache:
            meta_file_key = _clean_key(corpus_id) + '/' + \
                       file_defaults['meta'] + '.json'
            corpus._save_to_cache(meta=meta_file_key)

    def update_beliefs(self, corpus_id):
        """Return updated belief scores for a given corpus.

        Parameters
        ----------
        corpus_id : str
            The ID of the corpus for which beliefs are to be updated.

        Returns
        -------
        dict
            A dictionary of belief scores with keys corresponding to Statement
            UUIDs and values to new belief scores.
        """
        logger.info('Updating beliefs for corpus "%s"' % corpus_id)
        # TODO check which options are appropriate for get_corpus
        corpus = self.get_corpus(corpus_id)
        be = BeliefEngine(self.scorer)
        stmts = list(corpus.statements.values())
        be.set_prior_probs(stmts)
        # Here we set beliefs based on actual curation
        for uuid, correct in corpus.curations.items():
            stmt = corpus.statements.get(uuid)
            if stmt is None:
                logger.warning('%s is not in the corpus.' % uuid)
                continue
            stmt.belief = correct
        belief_dict = {st.uuid: st.belief for st in stmts}
        return belief_dict

    def update_groundings(self, corpus_id):
        # TODO check which options are appropriate for get_corpus
        logger.info('Updating groundings for corpus "%s"' % corpus_id)
        corpus = self.get_corpus(corpus_id)

        # Send the latest ontology and list of concept texts to Eidos
        yaml_str = yaml.dump(self.ont_manager.yaml_root)
        concepts = []
        for stmt in corpus.raw_statements:
            for concept in stmt.agent_list():
                concept_txt = concept.db_refs.get('TEXT')
                concepts.append(concept_txt)
        groundings = self.eidos_reader.reground_texts(concepts, yaml_str)
        # Update the corpus with new groundings
        idx = 0
        for stmt in corpus.raw_statements:
            for concept in stmt.agent_list():
                concept.db_refs['UN'] = groundings[idx]
                idx += 1
        assembled_statements = default_assembly(corpus.raw_statements)
        corpus.statements = {s.uuid: s for s in assembled_statements}
        return assembled_statements


# From here on, a Flask app built around a LiveCurator is implemented

curator = LiveCurator(corpora=corpora)


@app.route('/reset_curation', methods=['POST'])
def reset_curation():
    """Reset the curations submitted until now."""
    if request.json is None:
        abort(Response('Missing application/json header.', 415))
    curator.reset_scorer()
    return jsonify({})


@app.route('/submit_curation', methods=['POST'])
def submit_curation():
    """Submit curations for a given corpus.

    The submitted curations are handled to update the probability model but
    there is no return value here. The update_belief function can be called
    separately to calculate update belief scores.

    Parameters
    ----------
    corpus_id : str
        The ID of the corpus for which the curation is submitted.
    curations : dict
        A set of curations where each key is a Statement UUID in the given
        corpus and each key is 0 or 1 with 0 corresponding to incorrect and
        1 corresponding to correct.
    """
    if request.json is None:
        abort(Response('Missing application/json header.', 415))
    # Get input parameters
    corpus_id = request.json.get('corpus_id')
    curations = request.json.get('curations', {})
    try:
        curator.submit_curation(corpus_id, curations)
    except InvalidCorpusError:
        abort(Response('The corpus_id "%s" is unknown.' % corpus_id, 400))
        return
    return jsonify({})


@app.route('/update_beliefs', methods=['POST'])
def update_beliefs():
    """Return updated beliefs based on current probability model."""
    if request.json is None:
        abort(Response('Missing application/json header.', 415))
    # Get input parameters
    corpus_id = request.json.get('corpus_id')
    try:
        belief_dict = curator.update_beliefs(corpus_id)
    except InvalidCorpusError:
        abort(Response('The corpus_id "%s" is unknown.' % corpus_id, 400))
        return
    return jsonify(belief_dict)


@app.route('/add_ontology_entry', methods=['POST'])
def add_ontology_entry():
    if request.json is None:
        abort(Response('Missing application/json header.', 415))

    # Get input parameters
    entry = request.json.get('entry')
    examples = request.json.get('examples', [])
    # Add the entry and examples to the in-memory representation
    # of the onotology
    curator.ont_manager.add_entry(entry, examples)
    return jsonify({})


@app.route('/reset_ontology', methods=['POST'])
def reset_ontology():
    if request.json is None:
        abort(Response('Missing application/json header.', 415))

    # Reload the original ontology
    curator.ont_manager = _make_wm_ontology()

    return jsonify({})


@app.route('/update_groundings', methods=['POST'])
def update_groundings():
    if request.json is None:
        abort(Response('Missing application/json header.', 415))

    # Get input parameters
    corpus_id = request.json.get('corpus_id')
    # Run the actual regrounding
    stmts = curator.update_groundings(corpus_id)
    stmts_json = stmts_to_json(stmts)
    return jsonify(stmts_json)


@app.route('/update_metadata', methods=['POST'])
def update_metadata():
    if request.json is None:
        abort(Response('Missing application/json header.', 415))

    try:
        # Get input parameters
        corpus_id = request.json.get('corpus_id')
        meta_data = request.json.get('meta_data')
        curator.update_metadata(corpus_id, meta_data, save_to_cache=True)
    except InvalidCorpusError:
        abort(Response('The corpus_id "%s" is unknown.' % corpus_id, 400))
        return
    return jsonify({})


@app.route('/save_curation', methods=['POST'])
def save_curations():
    if request.json is None:
        abort(Response('Missing application/json header.', 415))

    try:
        # Get input parameters
        corpus_id = request.json.get('corpus_id')
        curator.save_curation(corpus_id, save_to_cache=True)
    except InvalidCorpusError:
        abort(Response('The corpus_id "%s" is unknown.' % corpus_id, 400))
        return
    return jsonify({})


if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser(
        description='Choose a corpus for live curation.')
    parser.add_argument('--json')
    parser.add_argument('--raw_json')
    parser.add_argument('--pickle')
    parser.add_argument('--meta-json', help='Meta data json file')
    parser.add_argument('--corpus_id')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8001, type=int)
    parser.add_argument('--aws-cred', type=str, default='default',
                        help='The name of the credential set to use when '
                             'connecting to AWS services. If the name is not '
                             'found in your AWS config, `[default]`  is used.')
    args = parser.parse_args()

    # Load corpus from S3 if corpus ID is provided
    if args.corpus_id and not args.json and not args.pickle:
        curator.corpora[args.corpus_id] = Corpus.load_from_s3(
            s3key=args.corpus_id,
            aws_name=args.aws_cred
        )
        logger.info('Loaded corpus %s from S3 with %d statements and %d '
                    'curation entries' %
                    (args.corpus_id,
                     len(curator.corpora[args.corpus_id].statements),
                     len(curator.corpora[args.corpus_id].curations)))

    elif args.json or args.pickle:
        if not args.corpus_id:
            raise ValueError('Must provide a corpus id when loading files '
                             'locally')
        if args.json:
            stmts = stmts_from_json_file(args.json)
        elif args.pickle:
            with open(args.pickle, 'rb') as fh:
                stmts = pickle.load(fh)
        else:
            stmts = None

        if args.raw_json:
            raw_stmts = stmts_from_json_file(args.raw_json)
        else:
            raw_stmts = None

        if args.meta_json and path.isfile(args.meta_json):
            meta_json_obj = _json_loader(args.meta_json)
        else:
            meta_json_obj = None

        if stmts:
            logger.info('Loaded corpus from provided file with %d '
                        'statements.' % len(stmts))
            # If loaded from file, the key will be '1'
            curator.corpora[args.corpus_id] = Corpus(stmts, raw_stmts,
                                                     meta_json_obj,
                                                     args.aws_cred)

    # Run the app
    app.run(host=args.host, port=args.port, threaded=False)
