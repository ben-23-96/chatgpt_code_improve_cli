from argparse import ArgumentParser
from .commands.code_edit import code_edit_parser, code_edit_function
from .commands.review_to_file import review_to_file_parser, review_to_file_function
from .commands.set_api_key import set_api_key_parser, set_api_key_function


def main():
    parser = ArgumentParser(
        description='Command line to interact with ChatGPT API to refactor code, add comments and docstrings, or add error handling.')
    # create subparser for multiple commands
    subparsers = parser.add_subparsers()
    # set arguments and function for code-edit command
    code_edit_parser(subparsers).set_defaults(func=code_edit_function)
    # set arguments and function for review-to-file command
    review_to_file_parser(subparsers).set_defaults(func=review_to_file_function)
    # set arguments and function for config command
    set_api_key_parser(subparsers).set_defaults(func=set_api_key_function)
    # parse the arguments
    args = parser.parse_args()

    args.func(args)

if __name__ == '__main__':
    main()