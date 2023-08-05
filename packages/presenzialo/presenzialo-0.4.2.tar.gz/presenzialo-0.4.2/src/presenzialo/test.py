import datetime
import argparse

from .presenzialo_web import PRweb
from .presenzialo_day import PRday, add_parser_date
from .presenzialo_args import add_parser_debug
from .presenzialo_address import PRaddress, add_parser_address
from .presenzialo_auth import PRauth, add_parser_auth

from .presenzialo_auth import PRauth, config_auth
from .presenzialo_web import PRweb
from .presenzialo_day import PRday


def main():

    parser = argparse.ArgumentParser(
        prog="presenzialo",
        description="presenzialo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    add_parser_debug(parser)
    add_parser_date(parser)
    add_parser_address(parser)
    add_parser_auth(parser)

    args = parser.parse_args()
    print(args)

    # pr_web = PRweb(PRauth())

    pr_auth = PRauth(**vars(args))
    pr_web = PRweb(pr_auth)

    pr_day = PRday(pr_web.timecard())
    # pr_day = PRday(pr_web.timecard(args.day_from, args.day_to))

    print(pr_day.days)


if __name__ == "__main__":
    main()
