from os import path, makedirs

def set_api_key_parser(subparsers):
    # set the command name to be used in termainal
    parser = subparsers.add_parser('set-api-key')

    # set the arguments
    parser.add_argument('api_key', type=str, help='The open ai api key for the user. Key can be found here https://platform.openai.com/account/api-keys if you have a valid openai account.')

    return parser

def set_api_key_function(args):
    """
    Prompts the user for their OpenAI API key and saves it to a configuration file in the user's home directory.
    """

    # api key supplied by the user
    api_key = args.api_key
    
    # Define the directory and file path for the configuration file
    config_dir = path.expanduser('~/.chatgpt_cli/')
    config_file = path.join(config_dir, 'config.txt')
    
    # Create the configuration directory if it doesn't exist
    makedirs(config_dir, exist_ok=True)
    
    # write the API key to the configuration file
    with open(config_file, 'w') as f:
        f.write(api_key)

    print('API key saved.')