from argparse import ArgumentTypeError

class ArgumentValidator:
    def __init__(self, args):
        self.args = args

    def check_file_type(self):
        file_type = self.args.filename.split('.')[-1]
        if file_type not in ['py', 'js']:
            raise ArgumentTypeError('Invalid file type. Only Python (.py) and JavaScript (.js) files are allowed.')

    def check_review_and_edit(self):
        if not self.args.create_review_file and not self.args.edit_code_in_file:
            raise ArgumentTypeError('Either --create-review-file or --edit-code-in-file must be set. Both can be set.')

    def check_refactor_and_comments_and_docstrings_and_error_handling(self):
        if not self.args.refactor and not self.args.comments and not self.args.docstrings and not self.args.error_handling:
            raise ArgumentTypeError('At least one of --refactor, --comments, --docstrings, error-handling must be provided.')

    def validate(self):
        self.check_file_type()
        self.check_review_and_edit()
        self.check_refactor_and_comments_and_docstrings_and_error_handling()
