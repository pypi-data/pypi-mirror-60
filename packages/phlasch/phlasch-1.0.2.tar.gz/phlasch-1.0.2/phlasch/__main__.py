import argparse
from phlasch.runners import run
from phlasch.migrators import history, revision, upgrade, downgrade


def main():
    # create command parser
    parser = argparse.ArgumentParser(
        'phlasch',
        description='A url shortener.',
    )

    # make command subparsers
    subparsers = parser.add_subparsers(
        title='Action',
        description='The action to take.',
        dest='action',
        required=True,
    )

    # run subparser
    run_parser = subparsers.add_parser(
        'run',
        description='Run app.',
        help='Run app.',
    )
    run_parser.add_argument(
        'app', type=str,
        help='The app to run.',
    )

    # history subparser
    history_parser = subparsers.add_parser(
        'history',
        description='Log revisions.',
        help='Log revisions.',
    )
    history_parser.add_argument(
        'app', type=str,
        help='The app to log the revisions for.',
    )

    # revision subparser
    revision_parser = subparsers.add_parser(
        'revision',
        description='Make revision.',
        help='Make revision.',
    )
    revision_parser.add_argument(
        'app', type=str,
        help='The app to make the revision for.',
    )
    revision_parser.add_argument(
        'message', type=str,
        help='The revision message.',
    )

    # upgrade subparser
    upgrade_parser = subparsers.add_parser(
        'upgrade',
        description='Upgrade to revision.',
        help='Upgrade to revision.',
    )
    upgrade_parser.add_argument(
        'app', type=str,
        help='The app to upgrade.',
    )
    upgrade_parser.add_argument(
        'rev', type=str,
        help='The rev to upgrade to.',
    )

    # downgrade subparser
    downgrade_parser = subparsers.add_parser(
        'downgrade',
        description='Downgrade to revision.',
        help='Downgrade to revision.',
    )
    downgrade_parser.add_argument(
        'app', type=str,
        help='The app to downgrade.',
    )
    downgrade_parser.add_argument(
        'rev', type=str,
        help='The rev to downgrade to.',
    )

    # parse args
    args = parser.parse_args()

    if args.action == 'run':
        run(args.app)
    elif args.action == 'history':
        history(args.app)
    elif args.action == 'revision':
        revision(args.app, args.message)
    elif args.action == 'upgrade':
        upgrade(args.app, args.rev)
    elif args.action == 'downgrade':
        downgrade(args.app, args.rev)


if __name__ == '__main__':
    main()
