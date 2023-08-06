import argparse
from getpass import getpass

from reproduce_wem_taxonomy.share import PgConnector


def use_case_mentions_by_publication(pg: PgConnector):
    with pg.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * '
                           'FROM publications_with_origins '
                           '(origin_id, origin_url, origin_retrieval_date, '
                           'origin_cites, origin_kind) '
                           'VALUES (DEFAULT, %(url)s, %(retrieval_date)s, '
                           '%(cites)s, %(kind)s) '
                           'RETURNING origin_id;',
                           {'url': query_url,
                            'retrieval_date': date.today(),
                            'cites': cites,
                            'kind': origin_kind})
            origin_id = cursor.fetchone()[0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
                                     'Export various useful JSON views '
                                     'from a database of '
                                     'annotated WEM publications.')
    parser.add_argument('--host', type=str,
                        help='host of the Postgres database',
                        default='localhost')
    parser.add_argument('--db', type=str,
                        help='name of the Postgres database',
                        required=True)
    parser.add_argument('--user', type=str,
                        help='name of a user having read access to the '
                             'Postgres database (default: taxonomist)',
                        default='taxonomist')

    args = parser.parse_args()
    pw = getpass('Enter password for Postgres user {}:'.format(args.user))

    pg = PgConnector(host=args.host, db_name=args.db, user=args.user,
                     password=pw)

