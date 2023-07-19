from argparse import ArgumentParser
from commands.gpt_edit import gpt_edit_parser, gpt_edit_function
from commands.review_to_file import review_to_file_parser, review_to_file_function


def main():
    parser = ArgumentParser(
        description='Command line to interact with ChatGPT API to refactor code, add comments and docstrings, or add error handling.')
    # create subparser for multiple commands
    subparsers = parser.add_subparsers()
    # set arguments and function for gpt-edit command
    gpt_edit_parser(subparsers).set_defaults(func=gpt_edit_function)
    # set arguments and function for review-to-file command
    review_to_file_parser(subparsers).set_defaults(func=review_to_file_function)
    # parse the arguments
    args = parser.parse_args()

    args.func(args)

if __name__ == '__main__':
    main()