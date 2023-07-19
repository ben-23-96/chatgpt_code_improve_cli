from argparse import ArgumentParser
from tqdm import tqdm
from arguement_validator import ArgumentValidator
from code_parser import CodeParser
from gpt_request import GptRequest

def gpt_edit_parser(subparsers):
    # set the command name to be used in termainal
    parser = subparsers.add_parser('gpt-edit')
    
    # set the arguments
    parser.add_argument('filename', type=str,
                        help='The filename of the file containing the code to be used. eg. main.py')
    parser.add_argument('--target-functions', type=str, nargs='*', default=[],
                        help='A space-separated list of function names to be targeted.')
    parser.add_argument('--target-classes', type=str, nargs='*', default=[],
                        help='A space-separated list of class names to be targeted. Should be provied as ClassName, targets every method in each class provided. Cannot be used if --target-methods also used on a method within one of the given classes.')
    parser.add_argument('--target-methods', type=str, nargs='*', default=[],
                        help='A space-separated list of method names to be targeted. Each method should be given as ClassName.method. Cannot be used if --target-classes also used on the class the method is from.')
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
    parser.add_argument('--temp', type=float, default=0.4, help='Affects the randomness of the output. Higher more creative lower more structured. Must be between 1 and 0. Default 0.4.')
    parser.add_argument('--create-review-file', action='store_true', help='If set, creates a file {function_name}.py in a folder gpt_edit_review containing the newly edited function code and the old function code. Allowing you to review before replacing the code in the actual file. Remember to gitignore or delete the folder created when done. Either this or edit-code-in-file must be set. Both can be set.')
    parser.add_argument('--edit-code-in-file', action='store_true', help='If set, rewrites the selected function with the newly edited version returned from gpt. If used advisable for code to be commited and saved in case of erroneus changes. Either this or create-review-file must be set. Both can be set.')
    return parser

def gpt_edit_function (args):
    
    # create the class instances
    argument_valiadator = ArgumentValidator(args)

    code_parser = CodeParser(filename=args.filename, function_names=args.target_functions, class_names=args.target_classes, method_names=args.target_methods)

    gpt_request = GptRequest(gpt_4=args.gpt_4)
    
    # tasks for the terminal progress bar
    total_tasks = 4 + args.create_review_file + args.edit_code_in_file

    with tqdm(total=total_tasks) as progress_bar:
    
        try:
            # check arguements fit the requirements
            argument_valiadator.gpt_edit_validate()
            progress_bar.set_description('Validated Arguments.')
            progress_bar.update()
        except Exception as e:
            print(e)
            return
        
        # find the code as str of the required functions, methods, classes
        functions_code_list, not_found_list = code_parser.find_target_code_gpt_edit()
        
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
        progress_bar.set_description('Retrieved target code as strings from file.')
        progress_bar.update()
        
        # create prompts message strings to be send to gpt api
        gpt_request.create_prompts(functions=functions_code_list, refactor=args.refactor, comments=args.comments, docstrings=args.docstrings, error_handling=args.error_handling)
        progress_bar.set_description('Created prompts to be sent to GPT.')
        progress_bar.update()
        
        # send the requests to the api return the newly edited functions as strings
        new_functions = gpt_request.make_GPT_requests()
        progress_bar.set_description('Retrieved responses from GPT.')
        progress_bar.update()
        if args.create_review_file:
            # create a file to view the original function or class and the gpt edited one for comparison
            code_parser.create_review_code_files(new_functions=new_functions)
            progress_bar.set_description('Created review code files.')
            progress_bar.update()
        if args.edit_code_in_file:
            # edit the code in the file replacing the class or function or method with the gpt edited one
            code_parser.replace_target_functions_with_new_functions(new_functions=new_functions)
            progress_bar.set_description('Edited code in file.')
            progress_bar.update()
    print('COMPLETED')