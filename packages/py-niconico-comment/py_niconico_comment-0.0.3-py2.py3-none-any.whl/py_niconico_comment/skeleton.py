# -*- coding: utf-8 -*-
import argparse
import json
import logging
import sys

from py_niconico_comment import NiconicoComments, __version__, write_file

__author__ = 'poipoii'
__copyright__ = 'poipoii'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        prog='niconico_comment', usage='%(prog)s [options] URL',
        description='niconico comment utils')
    parser.add_argument(
        '--version',
        action='version',
        version='py-niconico-comment {ver}'.format(ver=__version__))
    parser.add_argument(
        '--user',
        action='store',
        dest='username')
    parser.add_argument(
        '--password',
        action='store',
        dest='password')
    parser.add_argument(
        '--list',
        action='store_true',
        default=False,
        help='List all user-id with 2 first comment')
    parser.add_argument(
        '--user-id',
        action='append',
        help='Set user-id to fitter when write file')
    parser.add_argument(
        '--no-out',
        action='store_true',
        default=False,
        help='Return context, not write to file')
    parser.add_argument(
        '--write-srt',
        action='store_true',
        default=False,
        help='Write comments to a srt file')
    parser.add_argument(
        '--write-json',
        action='store_true',
        default=False,
        help='Write comments to a json file')
    parser.add_argument(
        '--time',
        action='store',
        default=0.0,
        help='Shift time when write srt file',
        type=float)
    parser.add_argument(
        '-v',
        '--verbose',
        dest='loglevel',
        help='set loglevel to INFO',
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest='loglevel',
        help='set loglevel to DEBUG',
        action='store_const',
        const=logging.DEBUG)
    parser.add_argument(
        'url',
        metavar='URL',
        type=str,
        nargs='+',
        help='URL')
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = '[%(asctime)s] %(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt='%Y-%m-%d %H:%M:%S')


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    loglevel = args.loglevel or logging.CRITICAL
    setup_logging(loglevel)

    username = args.username
    password = args.password
    user_id = args.user_id
    no_out = args.no_out
    list_user = args.list
    urls = args.url

    if not username or not password:   # if filename is not given
        _logger.info('Username or password not given!')
        return
    if not len(urls):   # if URL is not given
        _logger.info('missing URL!')
        return
    url = urls[0]

    if list_user or args.write_srt or args.write_json:
        _logger.info('Login...')
        niconico = NiconicoComments(username, password, loglevel)

        if not niconico.is_login:
            _logger.info('Login faild!')
            return
        _logger.info('Login Success!')
    else:
        _logger.info('Nothing to do!')

    if list_user:
        users = niconico.get_list_user(url)
        list_user_with_comment = ''
        for index, u in enumerate(users.keys()):
            if len(users[u]) > 1:
                list_user_with_comment += '\n%0.f: %s\n\t-%s\n\t-%s' % (index, u, users[u][0], users[u][1])
        if list_user_with_comment:
            print(list_user_with_comment)
        else:
            _logger.info('No user data!')
        return

    if args.write_json or args.write_srt:
        comments = niconico.get_comments(url, user_id)
        if args.write_json:
            context = json.dumps(comments)
            if no_out:
                _logger.info(context)
            else:
                _logger.info('write_json')
                write_file('%s.json' % url[url.rfind('/') + 1:], context)

        elif args.write_srt:
            context = niconico.to_srt(comments, args.time)
            if no_out:
                _logger.info(context)
            else:
                _logger.info('write_srt')
                write_file('%s.srt' % url[url.rfind('/') + 1:], context)


def run():
    """Entry point for console_scripts
    """
    args = sys.argv[1:]
    main(args if len(args) else ['--help'])


if __name__ == '__main__':
    run()
