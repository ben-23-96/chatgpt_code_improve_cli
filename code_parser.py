from redbaron import RedBaron
from os import makedirs
from argparse import ArgumentError

class CodeParser:
    def __init__(self, filename):
        self.filename = filename
        self.function_names_list = []
        self.original_functions_code_list = []
        self.function_not_found_list = []

    def get_target_functions_code(self, function_names: list):
        with open(self.filename, "r") as source_code:
            red = RedBaron(source_code.read())
    
        for function_name in function_names:
            function_node = red.find('def', function_name)
            if not function_node:
                self.function_not_found_list.append(function_name)
                continue
            self.function_names_list.append(function_node.name)
            self.original_functions_code_list.append(function_node.dumps())

        if len(self.original_functions_code_list) == 0:
            function_names_str = (', ').join(function_names)
            raise Exception(f'Unable to find any of the given functions in {self.filename}, the functions you provided were {function_names_str}')
    
        return self.original_functions_code_list, self.function_not_found_list
    
    def replace_target_functions_with_new_functions(self, new_functions: list):
        with open(self.filename, 'r') as source_code:
            red = RedBaron(source_code.read())
        
        functions_code_name_zip = zip(self.function_names_list, new_functions)
        
        for func_tuple in functions_code_name_zip:
            function_name = func_tuple[0]
            function_code = RedBaron(func_tuple[1]).find('def', function_name)
            red.find('def', function_name).replace(f'{function_code}\n\n')
        
        with open(self.filename, 'w') as source_code:
            source_code.write(red.dumps())
    
    def create_review_code_files(self, new_functions: list):
        makedirs('gpt_function_review', exist_ok=True)
        functions_zip = zip(self.function_names_list, self.original_functions_code_list, new_functions)
        for func_tuple in list(functions_zip):
            function_name = func_tuple[0]
            original_function = func_tuple[1]
            new_function = func_tuple[2]
            
            with open(f'gpt_function_review/{function_name}.py', "w") as f:
                f.write('##### NEW FUNCTION CODE #####\n\n')
                f.write(new_function)
                f.write('\n\n##### ORIGINAL FUNCTION CODE #####\n\n')
                f.write(original_function)