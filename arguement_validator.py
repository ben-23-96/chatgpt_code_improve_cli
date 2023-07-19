from argparse import ArgumentTypeError
from os import listdir

class ArgumentValidator:
    def __init__(self, args):
        """
    Parameters:
    args (list): A list of arguments from the CLI.
    """
        self.args = args

    def check_file_type(self):
        """
    Check the file type of the given filename.
        
    Raises:
        ArgumentTypeError: If the file type is not '.py'.
    """
        # Get the file type by splitting the filename at the last dot and taking the last part
        file_type = self.args.filename.split('.')[-1]
    
        # if the file type is not '.py' raise a error
        if file_type != 'py':
            raise ArgumentTypeError('Invalid file type. Only Python (.py) files are allowed.')

    def check_one_of_method_or_class_or_function_provided(self):
        """
    Check if at least one of target functions, target methods, or target classes is provided.

    Raises:
        ArgumentTypeError: If none of the target functions, target methods, or target classes are provided.
    """
        if not self.args.target_functions and not self.args.target_methods and not self.args.target_classes:
            raise ArgumentTypeError('At least one of --target-functions, --target-methods or --target-classes must be provided.')

    def check_one_of_review_or_edit_provided(self):
        """
    Checks if either --create-review-file or --edit-code-in-file is set.
    Raises an ArgumentTypeError if neither option is set.
    """
        if not self.args.create_review_file and not self.args.edit_code_in_file:
            raise ArgumentTypeError('Either --create-review-file or --edit-code-in-file must be set. Both can be set.')

    def check_one_of_refactor_or_comments_or_docstrings_or_error_handling_provided(self):
        """
    Check if at least one of the options --refactor, --comments, --docstrings, --error-handling is provided.
    
    Raises:
        ArgumentTypeError: If none of the options are provided.
    """
        if not self.args.refactor and not self.args.comments and not self.args.docstrings and not self.args.error_handling:
            raise ArgumentTypeError('At least one of --refactor, --comments, --docstrings, --error-handling must be provided.')

    def check_no_class_and_methods_clash(self):
        """
    Check if there is a clash between the target classes and target methods.
    Raises an ArgumentTypeError if there is a clash.
    """
        # Get the class names from the target methods
        method_classes = [method.split('.')[0] for method in self.args.target_methods]
    
        # raise a error if there is any intersection between the target classes and method classes
        if bool(set(self.args.target_classes) & set(method_classes)):
            raise ArgumentTypeError(f'Cannot provide --target-methods and --target-classes that contain the same class.\nTarget methods: {self.args.target_methods}\nTarget classes: {self.args.target_classes}')

    def check_temp_range(self):
        """
    Checks if the temperature value is within the range of 0 and 1.
    
    Raises:
        ArgumentTypeError: If the temperature value is not between 0 and 1.
    """
        if self.args.temp < 0 or self.args.temp > 1:
            raise ArgumentTypeError("temp must be between 0 and 1.")

    def check_method_in_correct_format (self):
        """
    Check if the methods in the target_methods list are in the correct format.
    The correct format is ClassName.method, where ClassName starts with an uppercase letter
    and method is separated from the class name by a dot (.).
  
    Raises:
        ArgumentTypeError: If any method in the target_methods list does not match the correct format.
    """
        for method in self.args.target_methods:
            # Check if the first character of the method is not uppercase or if there is no dot in the method
            if not method[0].isupper() or '.' not in method:
                raise ArgumentTypeError(f"error with method formating for {method}, must be ClassName.method")

    def check_file_folder_exists_review_to_file(self):
        """
    Check if a folder for the filename exists in the gpt_edit_review folder. Used in the review-to-file command.

    Raises:
        ArgumentTypeError: If the folder for the fiename does not exist.
    """
        filename_folder_name = self.args.filename[:-3]
        if filename_folder_name not in listdir('gpt_edit_review'):
            raise ArgumentTypeError(f'No folder in gpt_edit_review for filename: {filename_folder_name}. No functions have been edited from the file and placed in the folder for review.')
        
    def check_gpt_edit_folder_exists_review_to_file(self):
        """
    Check if the gpt_edit_review folder exists. Used in the review-to-file command.

    Raises:
        ArgumentTypeError: If the gpt_edit_review folder does not exist.
    """
        try:
            listdir('gpt_edit_review')
        except Exception:
            raise ArgumentTypeError('Cannot use the review-to-code command as there is no gpt_edit_review folder. No functions have been edited and placed in the folder for review.')


    def gpt_edit_validate(self):
        """
    Validates the input provided to the function for the gpt_edit command.
    """
        # Check the file type
        self.check_file_type()
    
        # Check if either method, class, or function is provided
        self.check_one_of_method_or_class_or_function_provided()
    
        # Check if either review or edit is provided
        self.check_one_of_review_or_edit_provided()
    
        # Check if either refactor, comments, docstrings, or error handling is provided
        self.check_one_of_refactor_or_comments_or_docstrings_or_error_handling_provided()
    
        # Check for clash between classes and methods
        self.check_no_class_and_methods_clash()
    
        # Check the range of temporary variables
        self.check_temp_range()
    
        # Check if methods are in the correct format
        self.check_method_in_correct_format()

    def review_to_file_validate(self):
        """Validates the input provided to the function for the gpt_edit command."""
        # Check the file type
        self.check_file_type()

        # Check for clash between classes and methods
        self.check_no_class_and_methods_clash()
    
        # Check if methods are in the correct format
        self.check_method_in_correct_format()
        
        # Check if either method, class, function is provided
        self.check_one_of_method_or_class_or_function_provided()

        # Check if gpt_edit_review_folder_exists
        self.check_gpt_edit_folder_exists_review_to_file()
        
        # Check if a folder exists for the given filename in gpt_edit_review folder
        self.check_file_folder_exists_review_to_file()
