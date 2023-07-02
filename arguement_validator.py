from argparse import ArgumentTypeError

class ArgumentValidator:
    def __init__(self, args):
        self.args = args

    def check_file_type(self):
        file_type = self.args.filename.split('.')[-1]
        if file_type not in ['py', 'js']:
            raise ArgumentTypeError('Invalid file type. Only Python (.py) and JavaScript (.js) files are allowed.')
        
    def check_one_of_method_or_class_or_function_provided(self):
        if not self.args.target_functions and not self.args.target_methods and not self.args.target_classes:
            raise ArgumentTypeError('At least one of --target-functions, --target-methods or target-classes must be provided.')

    def check_one_of_review_or_edit_provided(self):
        if not self.args.create_review_file and not self.args.edit_code_in_file:
            raise ArgumentTypeError('Either --create-review-file or --edit-code-in-file must be set. Both can be set.')

    def check_one_of_refactor_or_comments_or_docstrings_or_error_handling_provided(self):
        if not self.args.refactor and not self.args.comments and not self.args.docstrings and not self.args.error_handling:
            raise ArgumentTypeError('At least one of --refactor, --comments, --docstrings, error-handling must be provided.')
        
    def check_no_class_and_methods_clash(self):
        method_classes = [method.split('.')[0] for method in self.args.target_methods]
        if bool(set(self.args.target_classes) & set(method_classes)):
            raise ArgumentTypeError(f'Cannot provide --target-methods and --target-classes that contain the same class.\nTarget methods: {self.args.target_methods}\nTarget classes: {self.args.target_classes}')
        
    def check_temp_range(self):
        if self.args.temp < 0 or self.args.temp > 1:
            raise ArgumentTypeError("temp must be between 0 and 1.")

    def validate(self):
        self.check_file_type()
        self.check_one_of_method_or_class_or_function_provided()
        self.check_one_of_review_or_edit_provided()
        self.check_one_of_refactor_or_comments_or_docstrings_or_error_handling_provided()
        self.check_no_class_and_methods_clash()
        self.check_temp_range()
