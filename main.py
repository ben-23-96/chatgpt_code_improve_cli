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
    parser.add_argument('--target-functions', type=str, nargs='*', default=[],
                        help='A space-separated list of function names to be targeted.')
    parser.add_argument('--target-classes', type=str, nargs='*', default=[],
                        help='A space-separated list of class names to be targeted. Should be provied as ClassName, targets every method in each class provided. Cannot be used if --target-methods also used on a method within one of the given classes.')
    parser.add_argument('--target-methods', type=str, nargs='*', default=[],
                        help='A space-separated list of method names to be targeted for refactoring. Each method should be given as ClassName.method. Cannot be used if --target-classes also used on the class the method is from.')
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

    print(json.dumps(vars(args), indent=2))

    argument_valiadator = ArgumentValidator(args)

    code_parser = CodeParser(filename=args.filename, function_names=args.target_functions, class_names=args.target_classes, method_names=args.target_methods)

    gpt_request = GptRequest(gpt_4=args.gpt_4)
    
    try:
        # check arguements fit the requirements
        argument_valiadator.validate()
    except Exception as e:
        print(e)
        return
    
    # find the code as str of the required functions, methods, classes
    functions_code_list, not_found_list = code_parser.get_target_functions_code()
    
    # if some functions were not found
    if len(not_found_list) > 0:
        # if no functions were found print message and return
        if len(functions_code_list) == 0:
            function_names_str = (', ').join(args.target_functions)
            class_names_str = (', ').join(args.target_classes)
            method_names_str = (', ').join(args.target_methods)
            print(f'Unable to find any of the given functions, methods or classes in {args.filename}.\nFunctions provided: {function_names_str}\nMethods provided: {method_names_str}\nClasses provided: {class_names_str}')
            return
        # some functions were found display functions not found to user ask if to continue
        not_found_str = (', ').join(not_found_list)
        user_continue = input(f'In {args.filename} unable to find: {not_found_str}.\n Do you wish to continue with the functions that were found successfully ? y/n  ')
        if user_continue == 'y':
            # if continue remove not found items in class attributes
            code_parser.remove_not_found()
        else:
            # if not continue return
            return
    
    # create prompts message strings to be send to gpt api
    gpt_request.create_prompts(functions=functions_code_list, refactor=args.refactor, comments=args.comments, docstrings=args.docstrings, error_handling=args.error_handling)
    
    # send the requests to the api return the newly edited functions as strings
    new_functions = gpt_request.make_GPT_requests()
    if args.create_review_file:
        # create a file to view the original function or class and the gpt edited one for comparison
        code_parser.create_review_code_files(new_functions=new_functions)
    if args.edit_code_in_file:
        # edit the code in the file replacing the class or function or method with the gpt edited one
        code_parser.replace_target_functions_with_new_functions(new_functions=new_functions)


if __name__ == '__main__':
    main()