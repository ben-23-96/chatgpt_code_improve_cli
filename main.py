from argparse import ArgumentParser
import json
from arguement_validator import ArgumentValidator
from code_parser import CodeParser
from gpt_request import GptRequest

def main():
    parser = ArgumentParser(
        description='Command line to interact with ChatGPT API to refactor code, add comments and docstrings, or add error handling.')

    parser.add_argument('filename', type=str,
                        help='The filename of the file containing the code to be used.')
    parser.add_argument('--target-functions', type=str, nargs='+', default=[],
                        help='A space-separated list of function names to be targeted for refactoring. ## CLASSES ##')
    parser.add_argument('--refactor', action='store_true',
                        help='If set, refactor the code.')
    parser.add_argument('--comments', action='store_true',
                        help='If set, add comments to the code.')
    parser.add_argument('--docstrings', action='store_true',
                        help='If set, add docstrings to the code.')
    parser.add_argument('--error-handling', action='store_true',
                        help='If set, add error handling to the code.')
    parser.add_argument('--gpt-4', action='store_true',
                        help='If set, GPT-4 will be used instead of the default GPT-3.')
    parser.add_argument('--create-review-file', action='store_true', help='If set, creates a file {function_name}.py in a folder gpt_function_review containing the newly edited function code and the old function code. Allowing you to review before replacing the code in the actual file. Either this or edit-code-in-file must be set. Both can be set.')
    parser.add_argument('--edit-code-in-file', action='store_true', help='If set, rewrites the selected function with the newly edited version returned from gpt. If used advisable for code to be commited and saved in case of erroneus changes. Either this or create-review-file must be set. Both can be set.')

    args = parser.parse_args()

    argument_valiadator = ArgumentValidator(args)
    
    try:
        argument_valiadator.validate()
    except Exception as e:
        print(e)
        return

    ## Print the arguments for demonstration
    print(json.dumps(vars(args), indent=2))

    code_parser = CodeParser(filename=args.filename)

    gpt_request = GptRequest(gpt_4=args.gpt_4)
    
    functions_code_list = code_parser.get_target_functions_code(function_names=args.target_functions)
    
    gpt_request.create_prompts(functions=functions_code_list, refactor=args.refactor, comments=args.comments, docstrings=args.docstrings, error_handling=args.error_handling)
    
    new_functions = gpt_request.make_GPT_requests()
    if args.create_review_file:
        code_parser.create_review_code_files(new_functions=new_functions)
    if args.edit_code_in_file:
        code_parser.replace_target_functions_with_new_functions(new_functions=new_functions)


if __name__ == '__main__':
    main()