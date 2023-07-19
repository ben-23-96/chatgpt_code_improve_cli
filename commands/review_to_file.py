from argparse import ArgumentParser
from tqdm import tqdm
from arguement_validator import ArgumentValidator
from code_parser import CodeParser
from gpt_request import GptRequest

def review_to_file_parser(subparsers):
    # set the command name to be used in termainal
    parser = subparsers.add_parser('review-to-file')
    
    # set the arguments
    parser.add_argument('filename', type=str,
                        help='The filename of the file containing the code. eg. main.py')
    parser.add_argument('--target-functions', type=str, nargs='*', default=[],
                        help='A space-separated list of function names to be targeted from the corresponding gpt_edit_review/filename folder.')
    parser.add_argument('--target-classes', type=str, nargs='*', default=[],
                        help='A space-separated list of function names to be targeted from the corresponding gpt_edit_review/filename folder. Should be provied as ClassName. Cannot be used if --target-methods also used on a method within one of the given classes.')
    parser.add_argument('--target-methods', type=str, nargs='*', default=[],
                        help='A space-separated list of method names to be targeted from the corresponding gpt_edit_review/filename folder. Each method should be given as ClassName.method. Cannot be used if --target-classes also used on the class the method is from.')
    
    return parser

def review_to_file_function(args):
     # create the class instances
    argument_valiadator = ArgumentValidator(args)

    code_parser = CodeParser(filename=args.filename, function_names=args.target_functions, class_names=args.target_classes, method_names=args.target_methods)

    try:
        # check arguements fit the requirements
        argument_valiadator.review_to_file_validate()
    except Exception as e:
        print(e)
        return
    
    # find the edited code inn th gpt_edit_review folder files
    code_list, not_found_list = code_parser.find_target_code_in_gpt_edit_review_folder()

    # if some functions were not found
    if len(not_found_list) > 0:
        # if no functions were found print message and return
        if len(code_list) == 0:
            function_names_str = (', ').join(args.target_functions)
            class_names_str = (', ').join(args.target_classes)
            method_names_str = (', ').join(args.target_methods)
            print(f'Unable to find any of the given functions, methods or classes in gpt_edit_review/{args.filename[:-3]} folder.\nFunctions provided: {function_names_str}\nMethods provided: {method_names_str}\nClasses provided: {class_names_str}')
            return
        # some functions were found display functions not found to user ask if to continue
        not_found_str = (', ').join(not_found_list)
        user_continue = input(f'In gpt_edit_review/{args.filename[:-3]} folder unable to find: {not_found_str}.\n Do you wish to continue with the functions that were found successfully ? y/n  ')
        if user_continue == 'y':
            # if continue remove not found items in class attributes
            code_parser.remove_not_found()
        else:
            # if not continue return
            return
        
    # edit the code in the file replacing the class or function or method with the gpt edited one
    code_parser.replace_target_functions_with_new_functions(new_functions=code_list)
    print('COMPLETED')