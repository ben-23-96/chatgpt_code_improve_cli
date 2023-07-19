from redbaron import RedBaron
from os import makedirs, listdir

class CodeParser:
    def __init__(self, filename: str, function_names: list = [], class_names: list = [], method_names: list = []):
        self.filename = filename
        self.function_names = function_names
        self.class_names = class_names
        self.method_names = method_names
        self.found_code_names_list = []
        self.found_code_list = []
        self.not_found_code_names_list = []
        self.code_review_files = []

    def find_target_code_gpt_edit(self):
        # open file and parse the contents 
        with open(self.filename, "r") as source_code:
            parser = RedBaron(source_code.read())
        
        # find the classes methods and functions 
        for name in self.function_names:
            self.find_function(parser=parser, function_name=name)
        for name in self.method_names:
            self.find_method(parser=parser, class_method_name=name)
        for name in self.class_names:
            self.find_class(parser=parser, class_name=name)
        
        # return the found functions as strings in a list and the names of the functions not found in another list 
        return self.found_code_list, self.not_found_code_names_list
    
    def find_target_code_in_gpt_edit_review_folder(self):
        # get a list of the files in the gpt_edit_review/filename folder
        self.code_review_files = listdir(f'gpt_edit_review/{self.filename[:-3]}')
        # find the edited versions of the target functions, methods, classes in the gpt_edit_review folder files
        for name in self.function_names:
            self.check_code_in_review_file(name, self.find_function)
    
        for name in self.class_names:
            self.check_code_in_review_file(name, self.find_class)
    
        for name in self.method_names:
            self.check_code_in_review_file(name, self.find_method)

        # return the found functions as strings in a list and the names of the functions not found in another list 
        return self.found_code_list, self.not_found_code_names_list

    def check_code_in_review_file(self, name, process_func):
        # if a file for the function, method, class exists in gpt_edit_review folder
        if f'{name}.py' in self.code_review_files:
            # open the file and find the edited code
            with open(f'gpt_edit_review/{self.filename[:-3]}/{name}.py', "r") as source_code:
                parser = RedBaron(source_code.read())
                process_func(parser, name)
        # if not found add to not found list
        else:
            self.not_found_code_names_list.append(name)

    
    def find_class(self, parser, class_name):
        # find the class
        class_node = parser.find('class', class_name)
        if not class_node:
            self.not_found_code_names_list.append(class_name)
        # find all methods in the class
        method_nodes = class_node.find_all('def')
        # create a list of all method names as ClassName.method
        method_names = [f'{class_name}.{method_node.name}' for method_node in method_nodes]
        # create a list of the code of each method as a string, replace removes string if class is from gpt_edit_review file
        methods_code = [method_node.dumps().replace(f'\n##### ORIGINAL CLASS CODE #####\n', '') for method_node in method_nodes]
        # add found function names
        self.found_code_names_list.extend(method_names)
        # add found code strings
        self.found_code_list.extend(methods_code)

    def find_method(self, parser, class_method_name):
        # split ClassName.method to ClassName and method
        class_name, method_name = class_method_name.split('.')
        # find the class node in the file
        class_node = parser.find('class', class_name)
        # if not found add method to not found list
        if not class_node:
            self.not_found_code_names_list.append(class_method_name)
            #continue
        # find the method on the class
        method_node = class_node.find('def', method_name)
        # if not found add method to not found list
        if not method_node:
            self.not_found_code_names_list.append(class_method_name)
            #continue
        # add found function names to list
        self.found_code_names_list.append(class_method_name)
        # add found function code strings to list
        self.found_code_list.append(method_node.dumps().replace(f'\n##### ORIGINAL METHOD CODE #####\n', ''))

    def find_function(self, parser, function_name):
        # find the function
        function_node = parser.find('def', function_name)
        # if not found add to not found list and continue
        if not function_node:
            self.not_found_code_names_list.append(function_name)
            #continue
        # add the name of the function to the found functions list
        self.found_code_names_list.append(function_name)
        # add the code of the function as a str to a list, replace removes string if function is from gpt_edit_review file
        self.found_code_list.append(function_node.dumps().replace(f'\n##### ORIGINAL FUNCTION CODE #####\n', ''))

    def replace_target_functions_with_new_functions(self, new_functions: list):
        # parse the file
        with open(self.filename, 'r') as source_code:
            parser = RedBaron(source_code.read())
        # create zip containing the name of the function or method and the newly edited version of it as a str
        functions_name_code_zip = zip(self.found_code_names_list, new_functions)
        
        for name, function_code in functions_name_code_zip:
            if '.' in name:
                # must be class method
                class_name, method_name = name.split('.')
                # find the class
                class_node = parser.find('class', class_name)
                new_method = RedBaron(function_code)
                # replace the method in the parser object with the newly edited version of the method
                class_node.find('def', method_name).value = new_method[0].value.dumps().rstrip()
            else:
                # must be function
                # parse the new function code
                new_function = RedBaron(function_code).find('def', name)
                # replace the function in the parser object with the newly edited version of the function
                parser.find('def', name).value = new_function.value.dumps().rstrip()
        
        # write the edited file content from the parser into the file
        with open(self.filename, 'w') as source_code:
            source_code.write(parser.dumps())
    
    def create_review_code_files(self, new_functions: list):
        # make folder to store created files
        makedirs('gpt_edit_review', exist_ok=True)
        makedirs(f'gpt_edit_review/{self.filename[:-3]}', exist_ok=True)
        # create zip of function/method name, the original function code, and the newly edited function code
        functions_zip = zip(self.found_code_names_list, self.found_code_list, new_functions)
        # create list to store the methods for a class if the whole class was provided in as a --target-class
        classes_name_code_zip_list= []
        for function_name, original_code, new_code in functions_zip:
            # if class method ClassName.method
            if '.' in function_name:
                # if ClassName in the class names provided, therefore method code part of a full class provided
                class_name = function_name.split('.')[0]
                if class_name in self.class_names:
                    # add ClassName.method and new function code to list to be used in create_class_code_review_file function
                    classes_name_code_zip_list.append((function_name, new_code))
                    continue
                # else method was not given as part of a full class
                else:
                     # write the original code and new code to a file for comparison for a class method
                    with open(f'gpt_edit_review/{self.filename[:-3]}/{function_name}.py', "w") as f:
                        f.write('##### NEW METHOD CODE #####\n\n')
                        f.write(f'class {class_name}:\n    ')
                        f.write(new_code.replace('\n    ', '\n        '))
                        f.write('\n\n##### ORIGINAL METHOD CODE #####\n\n')
                        f.write(f'class {class_name}:\n    ')
                        f.write(original_code)
                        continue
            # write the original code and new code to a file for comparison if function
            with open(f'gpt_edit_review/{self.filename[:-3]}/{function_name}.py', "w") as f:
                f.write('##### NEW FUNCTION CODE #####\n\n')
                f.write(new_code)
                f.write('\n\n##### ORIGINAL FUNCTION CODE #####\n\n')
                f.write(original_code)
            # call method that will write full classes to file for comparison
            self.create_class_code_review_file(classes_name_code_zip_list)

    def create_class_code_review_file(self, classes_names_code_list):
        # parse th file
        with open(self.filename, "r") as source_code:
            parser = RedBaron(source_code.read())
        # loop through given classes
        for class_name in self.class_names:
            # group all ClassName.methods for given ClassName into list
            class_tuples = [name_new_code_tuple for name_new_code_tuple in classes_names_code_list if name_new_code_tuple[0].split('.')[0] == class_name]
            # find the class in parser object
            class_node = parser.find('class', class_name)
            # original class code as string
            original_class_code = class_node.dumps()
            for name, new_code in class_tuples:
                new_method = RedBaron(new_code)
                # replace method with newly edited method in the parser
                class_node.find('def', name.split('.')[1]).value = new_method[0].value.dumps().rstrip()
            # new class code as string
            new_class_code = class_node.dumps()
            # create output string
            output_str = '##### NEW CLASS CODE #####\n\n'
            output_str += new_class_code
            output_str += '\n\n##### ORIGINAL CLASS CODE #####\n\n'
            output_str += original_class_code
            # write original class and new class to file for comparison
            with open(f'gpt_edit_review/{self.filename[:-3]}/{class_name}.py', "w") as f:
                f.write(output_str)

    def remove_not_found(self):
        self.class_names = [class_name for class_name in self.class_names if not class_name in self.not_found_code_names_list]