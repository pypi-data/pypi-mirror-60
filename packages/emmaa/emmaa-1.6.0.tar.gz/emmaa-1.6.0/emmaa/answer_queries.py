import pickle
import logging
from datetime import datetime

from emmaa.model_tests import load_model_manager_from_s3
from emmaa.db import get_db
from emmaa.util import get_s3_client, make_date_str, EMMAA_BUCKET_NAME


logger = logging.getLogger(__name__)


model_manager_cache = {}

FORMATTED_TYPE_NAMES = {'pysb': 'PySB',
                         'pybel': 'PyBEL',
                         'signed_graph': 'Signed Graph',
                         'unsigned_graph': 'Unsigned Graph'}


class QueryManager(object):
    """Manager to run queries and interact with the database.

    Parameters
    ----------
    db : emmaa.db.EmmaaDatabaseManager
        An instance of a database manager to use.
    model_managers : list[emmaa.model_tests.ModelManager]
        Optional list of ModelManagers to use for running queries. If not
        given, the methods will load ModelManager from S3 when needed.
    """
    def __init__(self, db=None, model_managers=None):
        self.db = db
        if db is None:
            self.db = get_db('primary')
        self.model_managers = model_managers if model_managers else []

    def answer_immediate_query(
            self, user_email, user_id, query, model_names, subscribe,
            use_kappa=False, bucket=EMMAA_BUCKET_NAME):
        """This method first tries to find saved result to the query in the
        database and if not found, runs ModelManager method to answer query."""
        query_type = query.get_type()
        # Retrieve query-model hashes
        query_hashes = [
            query.get_hash_with_model(model) for model in model_names]
        # Store query in the database for future reference.
        self.db.put_queries(user_email, user_id, query, model_names, subscribe)
        # Check if the query has already been answered for any of given models
        # and retrieve the results from database.
        saved_results = self.db.get_results_from_query(query, model_names)
        if not saved_results:
            saved_results = []
        checked_models = {res[0] for res in saved_results}
        # If the query was answered for all models before, return the hashes.
        if checked_models == set(model_names):
            return {query_type: query_hashes}
        # Run queries mechanism for models for which result was not found.
        new_results = []
        new_date = datetime.now()
        for model_name in model_names:
            if model_name not in checked_models:
                results_to_store = []
                mm = self.get_model_manager(model_name)
                response_list = mm.answer_query(
                    query, use_kappa=use_kappa, bucket=bucket)
                for (mc_type, response) in response_list:
                    results_to_store.append((query, mc_type, response))
                self.db.put_results(model_name, results_to_store)
        return {query_type: query_hashes}

    def answer_registered_queries(
            self, model_name, find_delta=True, notify=False, use_kappa=False,
            bucket=EMMAA_BUCKET_NAME):
        """Retrieve queries registered on database for a given model,
        answer them, calculate delta between results, notify users in case of
        any changes, and put results to a database.
        """
        model_manager = self.get_model_manager(model_name)
        queries = self.db.get_queries(model_name)
        logger.info(f'Found {len(queries)} queries for {model_name} model.')
        # Only do the following steps if there are queries for this model
        if queries:
            results = model_manager.answer_queries(
                queries, use_kappa=use_kappa, bucket=bucket)
            new_results = [(model_name, result[0], result[1], result[2], '')
                           for result in results]
            # Optionally find delta between results
            # NOTE: For now the report is presented in the logs. In future we
            # can choose some other ways to keep track of result changes.
            if find_delta:
                reports = self.make_reports_from_results(new_results, False,
                                                         'str')
                for report in reports:
                    logger.info(report)
            self.db.put_results(model_name, results)

    def get_registered_queries(self, user_email, query_type='path_property'):
        """Get formatted results to queries registered by user."""
        results = self.db.get_results(user_email, query_type=query_type)
        return format_results(results, query_type)

    def retrieve_results_from_hashes(self, query_hashes,
                                     query_type='path_property'):
        """Retrieve results from a db given a list of query-model hashes."""
        results = self.db.get_results_from_hashes(query_hashes)
        return format_results(results, query_type)

    def make_reports_from_results(
            self, new_results, stored=True, report_format='str'):
        """Make a report given latest results and queries the results are for.

        Parameters
        ----------
        new_results : list[tuple]
            Latest results as a list of tuples where each tuple has the format
            (model_name, query, mc_type, result_json, date).
        stored : bool
            Whether the new_results are already stored in the database.
        report_format : str
            A format to write reports in. Accepted values: 'str' and 'html'.
        Returns
        -------
        reports : list[str]
            A list of reports on changes for each of the queries.
        """
        processed_query_mc = []
        reports = []
        # If latest results are in db, retrieve the second latest
        if stored:
            order = 2
        # If latest results are not in db, retrieve the latest stored
        else:
            order = 1
        for model_name, query, mc_type, new_result_json, _ in new_results:
            if (model_name, query, mc_type) in processed_query_mc:
                continue
            try:
                old_results = self.db.get_results_from_query(
                    query, [model_name], order)
                if old_results:
                    for old_result in old_results:
                        if mc_type == old_result[2]:
                            old_result_json = old_result[3]
                            if report_format == 'str':
                                report = self.make_str_report_one_query(
                                    model_name, query, mc_type,
                                    new_result_json, old_result_json)
                            elif report_format == 'html':
                                report = self._make_html_one_query_inner(
                                    model_name, query, mc_type,
                                    new_result_json, old_result_json)
                            reports.append(report)
                else:
                    logger.info('No previous result was found.')
                    if report_format == 'str':
                        report = self.make_str_report_one_query(
                            model_name, query, mc_type, new_result_json, None)
                    elif report_format == 'html':
                        report = self._make_html_one_query_inner(
                            model_name, query, mc_type, new_result_json, None)
                    reports.append(report)
            except IndexError:
                logger.info('No result for desired date back was found.')
                if report_format == 'str':
                    report = self.make_str_report_one_query(
                        model_name, query, mc_type, new_result_json, None)
                elif report_format == 'html':
                    report = self._make_html_one_query_inner(
                        model_name, query, mc_type, new_result_json, None)
                reports.append(report)
            processed_query_mc.append((model_name, query, mc_type))
        return reports

    def get_user_query_delta(
            self, user_email, filename='query_delta', report_format='str'):
        """Produce a report for all query results per user in a given format"""
        results = self.db.get_results(user_email, latest_order=1)
        if report_format == 'str':
            filename = filename + '.txt'
            self.make_str_report_per_user(results, filename=filename)
        elif report_format == 'html':
            filename = filename + '.html'
            self.make_html_report_per_user(results, filename=filename)

    def get_report_per_query(self, model_name, query):
        try:
            new_results = self.db.get_results_from_query(
                            query, [model_name], latest_order=1)
        except IndexError:
            logger.info('No latest result was found.')
            return None
        return self.make_reports_from_results(new_results, True, 'str')

    def make_str_report_per_user(self, results, filename='query_delta.txt'):
        """Produce a report for all query results per user in a text file."""
        reports = self.make_reports_from_results(results, True, 'str')
        with open(filename, 'w') as f:
            for report in reports:
                f.write(report)

    def make_html_report_per_user(self, results, filename='query_delta.html'):
        """Produce a report for all query results per user in an html file."""
        msg = '<html><body>'
        reports = self.make_reports_from_results(results, True, 'html')
        for report in reports:
            msg += report
        msg += '</body></html>'
        with open(filename, 'w') as f:
            f.write(msg)

    def make_str_report_one_query(self, model_name, query, mc_type,
                                  new_result_json, old_result_json=None):
        """Return a string message containing information about a query and any
        change in the results."""
        if is_query_result_diff(new_result_json, old_result_json):
            if not old_result_json:
                msg = f'\nThis is the first result to query {query} ' \
                      f'in {model_name} with {mc_type} model checker.' \
                      f'\nThe result is:'
                msg += _process_result_to_str(new_result_json)
            else:
                msg = f'\nA new result to query {query} in {model_name} was ' \
                      f'found with {mc_type} model checker. '
                msg += '\nPrevious result was:'
                msg += _process_result_to_str(old_result_json)
                msg += '\nNew result is:'
                msg += _process_result_to_str(new_result_json)
        else:
            msg = f'\nA result to query {query} in ' \
                  f'{model_name} from {mc_type} model checker ' \
                  f'did not change. The result is:'
            msg += _process_result_to_str(new_result_json)
        return msg

    def make_html_one_query_report(self, model_name, query, mc_type,
                                   new_result_json, old_result_json=None):
        """Return an html page containing information about a query and any
        change in the results."""
        msg = '<html><body>'
        msg += self._make_html_one_query_inner(
            model_name, query, mc_type, new_result_json, old_result_json)
        msg += '</body></html>'
        return msg

    def _make_html_one_query_inner(self, model_name, query, mc_type,
                                   new_result_json, old_result_json=None):
        # Create an html part for one query to be used in producing html report
            if is_query_result_diff(new_result_json, old_result_json):
                if not old_result_json:
                    msg = f'<p>This is the first result to query {query} in ' \
                          f'{model_name} with {mc_type} model checker. ' \
                          f'The result is:<br>'
                    msg += _process_result_to_str(new_result_json)
                    msg += '</p>'
                else:
                    msg = f'<p>A new result to query {query} in ' \
                          f'{model_name} was found with {mc_type} ' \
                          f'model checker.<br>'
                    msg += '<br>Previous result was:<br>'
                    msg += _process_result_to_str(old_result_json)
                    msg += '<br>New result is:<br>'
                    msg += _process_result_to_str(new_result_json)
                    msg += '</p>'
            else:
                msg = f'<p>A result to query {query} in ' \
                      f'{model_name} from {mc_type} model checker did not ' \
                      f'change. The result is:<br>'
                msg += _process_result_to_str(new_result_json)
                msg += '</p>'
            return msg

    def notify_user(
            self, user_email, model_name, query, mc_type, new_result_json,
            old_result_json=None):
        """Create a query result delta report and send it to user."""
        str_msg = self.make_str_report_one_query(
            model_name, query, mc_type, new_result_json, old_result_json)
        html_msg = self.make_html_one_query_report(
            model_name, query, mc_type, new_result_json, old_result_json)
        # TODO send an email to user
        pass

    def get_model_manager(self, model_name):
        # Try get model manager from class attributes or load from s3.
        for mm in self.model_managers:
            if mm.model.name == model_name:
                return mm
        return load_model_manager_from_cache(model_name)

    def _recreate_db(self):
        self.db.drop_tables(force=True)
        self.db.create_tables()


def is_query_result_diff(new_result_json, old_result_json=None):
    """Return True if there is a delta between results."""
    # NOTE: this function is query-type specific so it may need to be
    # refactored as a method of the Query class:

    # Return True if this is the first result
    if not old_result_json:
        return True
    # Compare hashes of query results
    old_result_hashes = [k for k in old_result_json.keys()]
    new_result_hashes = [k for k in new_result_json.keys()]
    return not set(new_result_hashes) == set(old_result_hashes)


def format_results(results, query_type='path_property'):
    """Format db output to a standard json structure."""
    model_types = ['pysb', 'pybel', 'signed_graph', 'unsigned_graph']
    formatted_results = {}
    for result in results:
        model = result[0]
        query = result[1]
        query_hash = query.get_hash_with_model(model)
        if query_hash not in formatted_results:
            formatted_results[query_hash] = {
                'query': query.to_english(),
                'model': model,
                'date': make_date_str(result[4])}
        mc_type = result[2]
        response_json = result[3]
        response = []
        for v in response_json.values():
            if isinstance(v, str):
                response = v
            elif isinstance(v, dict):
                response.append(v)
        if query_type == 'path_property':
            if mc_type == '' and \
                    response == 'Query is not applicable for this model':
                for mt in model_types:
                    formatted_results[query_hash][mt] = ['n_a', response]
            elif isinstance(response, str) and \
                    response == 'Statement type not handled':
                formatted_results[query_hash][mc_type] = ['n_a', response]
            elif isinstance(response, str) and \
                    not response == 'Path found but exceeds search depth':
                formatted_results[query_hash][mc_type] = ['Fail', response]
            else:
                formatted_results[query_hash][mc_type] = ['Pass', response]
        elif query_type == 'dynamic_property':
            if response == 'Query is not applicable for this model':
                formatted_results[query_hash]['result'] = ['n_a', response]
            else:
                res = int(response[0]['sat_rate'] * 100)
                expl = (f'Satisfaction rate is {res}% after '
                        f'{response[0]["num_sim"]} simulations.')
                if res > 50:
                    formatted_results[query_hash]['result'] = ['Pass', expl]
                else:
                    formatted_results[query_hash]['result'] = ['Fail', expl]
                formatted_results[query_hash]['image'] = response[0]['fig_path']
    if query_type == 'path_property':
        # Loop through the results again to make sure all model types are there
        for qh in formatted_results:
            for mt in model_types:
                if mt not in formatted_results[qh]:
                    formatted_results[qh][mt] = [
                        'n_a', 'Model type not supported']
    return formatted_results


def load_model_manager_from_cache(model_name, bucket=EMMAA_BUCKET_NAME):
    model_manager = model_manager_cache.get(model_name)
    if model_manager:
        logger.info(f'Loaded model manager for {model_name} from cache.')
        return model_manager
    model_manager = load_model_manager_from_s3(
        model_name=model_name, bucket=bucket)
    model_manager_cache[model_name] = model_manager
    return model_manager


def _process_result_to_str(result_json):
    msg = '\n'
    for v in result_json.values():
        if isinstance(v, str):
            msg += v
        elif isinstance(v, dict):
            if 'path' in v.keys():
                msg += v['path']
                msg += '\n'
            else:
                msg += f'Satisfaction rate: {v["sat_rate"]}, '
                msg += f'Number of simulations: {v["num_sim"]}, '
                msg += f'Suggested pattern: {v["kpat"]}.'
    return msg


def answer_queries_from_s3(model_name, db=None, bucket=EMMAA_BUCKET_NAME):
    """Answer registered queries with model manager on s3.

    Parameters
    ----------
    model_name : str
        Name of EmmaaModel to answer queries for.
    db : Optional[emmaa.db.manager.EmmaaDatabaseManager]
        If given over-rides the default primary database.
    """
    mm = load_model_manager_from_s3(model_name=model_name, bucket=bucket)
    qm = QueryManager(db=db, model_managers=[mm])
    qm.answer_registered_queries(model_name, find_delta=True)
