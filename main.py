import argparse
import tableauserverclient as TSC
import getpass
import logging


def main():
    parser = argparse.ArgumentParser(
        description='Replace all occurences of a connection in all workbooks with new connection.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--workspace', '-ws', default=None, help='workspace to use')
    parser.add_argument('--old-connection', '-oc', required=True,
                        help='Connection hostname to replace')
    parser.add_argument('--new-connection', '-nc', help='Replacement hostname')
    parser.add_argument('--new-username', '-nu', help='Replacement username')
    parser.add_argument('--new-password', '-np', help='Replacement password')
    parser.add_argument('--new-port', '-npo', help='Replacement port')
    parser.add_argument('--new-embed-password', '-ne', help='Embed password in new connection',
                        action='store_true', dest='new_embed_password')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'],
                        default='info',
                        help='desired logging level (set to error by default)')
    parser.set_defaults(new_embed_password=None)

    args = parser.parse_args()
    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    tableau_auth = TSC.TableauAuth(args.username, password, args.workspace)
    server = TSC.Server(f'https://{args.server}')

    with server.auth.sign_in(tableau_auth):
        for workbook in TSC.Pager(server.workbooks):
            server.workbooks.populate_connections(workbook)
            logging.info(f'updating workbook: {workbook.name} ({workbook.id})')
            server.workbooks.populate_connections(workbook)

            for workbook_conn in workbook.connections:
                if args.old_connection != workbook_conn.server_address:
                    logging.info(
                        f'Skipping connection {workbook_conn.server_address} in {workbook.name}')
                    continue

                if args.new_username:
                    workbook_conn.username = args.new_username
                if args.new_password:
                    workbook_conn.password = args.new_password
                if args.new_embed_password:
                    workbook_conn.embed_password = args.new_embed_password
                if args.new_port:
                    workbook_conn.server_port = args.new_port
                if args.new_connection:
                    workbook_conn.server_address = args.new_connection

                server.workbooks.update_connection(workbook, workbook_conn)

if __name__ == '__main__':
    main()
