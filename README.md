# GPT Code Edit

gpt-code-edit is a Command Line Interface that allows you to target specific functions, classes, or methods in a file and use chatgpt to perform several edits on them including refactoring, adding comments, adding docstrings, or adding error handling. 

## Github

https://github.com/ben-23-96/chatgpt_code_improve_cli

## PyPI

https://pypi.org/project/gpt-code-edit/

## Prerequisites

- Python 3.9
- An active OpenAI account with API keys

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install GPT code edit.

```bash
pip install gpt-code-edit
```

# Usage

## Set API Key

First, you need to set your OpenAI API key. You can find your key at [OpenAI Platform](https://platform.openai.com/account/api-keys) if you have a valid OpenAI account.

```bash
gpt set-api-key <api_key>
```

### Arguments

| Argument | Description |
| :--- | :--- |
| `<api_key>` | The OpenAI API key for the user. |

## Code Edit

This command allows you to target specific functions, classes, or methods in a file and perform several edits on the code including refactoring, adding comments, adding docstrings, or adding error handling.

```bash
gpt code-edit <filename> [--target-functions <function1> <function2> ...] [--target-classes <class1> <class2> ...] [--target-methods <class1.method1> <class2.method2> ...] [--refactor] [--comments] [--docstrings] [--error-handling] [--gpt-4] [--temp <temperature>] [--create-review-file] [--edit-code-in-file]
```

**Note**: One of `--create-review-file` or `--edit-code-in-file` must be set. Both can be set at the same time.

**Note**: One of `--refactor`, `--comments`, `--docstrings` or `--error-handling` must be set. Multiple can be set at the same time.

**Note**: One of `--target-functions`, `--target-methods` or `--target-classes` must be set. Multiple can be set at the same time.

### Example

The following command would add GPT generated comments into the function foo located in the main.py file.

```bash
gpt code-edit main.py --target-functions foo --comments --edit-code-in-file
```

### Arguments

| Argument | Description |
| :--- | :--- |
| `<filename>` | The filename of the file containing the code (eg. main.py). |
| `--target-functions` | A space-separated list of function names to be targeted. |
| `--target-classes` | A space-separated list of class names to be targeted. Each class should be provided as `ClassName`. This will target every method in each class provided. This cannot be used if `--target-methods` is also used on a method within one of the given classes. |
| `--target-methods` | A space-separated list of method names to be targeted. Each method should be given as `ClassName.method`. This cannot be used if `--target-classes` is also used on the class the method is from. |
| `--refactor` | If set, refactor the code. |
| `--comments` | If set, add comments to the code. |
| `--docstrings` | If set, add docstrings to the code. |
| `--error-handling` | If set, add error handling to the code. |
| `--gpt-4` | If set, GPT-4 will be used instead of the default GPT-3. |
| `--temp` | Affects the randomness of the output. A higher value makes the output more creative and a lower value makes it more structured. Must be between 1 and 0. The default is 0.4. |
| `--create-review-file` | If set, creates a file `{function_name}.py` in a folder `gpt_edit_review` containing the newly edited function code and the old function code. This allows you to review the code before replacing it in the actual file. Remember to gitignore or delete the folder created when done. |
| `--edit-code-in-file` | If set, rewrites the selected code within the file with the newly edited version returned from GPT. If used, it is advisable for code to be committed and saved in case of erroneous changes. |

## Review to File

If when using code-edit the --create-review-file flag has been used so the edited code has been placed in a file for review, this command allows you to apply the changes to the actual file.

```bash
gpt review-to-file <filename> [--target-functions <function1> <function2> ...] [--target-classes <class1> <class2> ...] [--target-methods <class1.method1> <class2.method2> ...]
```

### Arguments

| Argument | Description |
| :--- | :--- |
| `<filename>` | The filename of the file containing the original code (eg. main.py). |
| `--target-functions` | A space-separated list of function names to be targeted from the corresponding `gpt_edit_review/<filename>` folder. |
| `--target-classes` | A space-separated list of class names to be targeted from the corresponding `gpt_edit_review/<filename>` folder. Each class should be provided as `ClassName`. This cannot be used if `--target-methods` is also used on a method within one of the given classes. |
| `--target-methods` | A space-separated list of method names to be targeted from the corresponding `gpt_edit_review/<filename>` folder. Each method should be given as `ClassName.method`. This cannot be used if `--target-classes` is also used on the class the method is from. |

