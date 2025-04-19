

PORT_TO_USE = 1234
PPERCENT_INTERVAL = 5
UNSET_NAME_MSG = "name not set for ip:{}"
ACCESSIBLE_FILES_FOLDER = "downloadable/"
FILESENDINGBUFFER = 2048
RECEIVE_BUFFER = 1024
LOG_FILE = 'log.txt'
NAMES_FILE = 'names.txt'
WELCOME_MSG = "Connection Succesful!"

HELP_MESSAGE_SET = {"\n"
"Commands:\n"
"help: sends this list of commands\n"
"close: closes the connection with the server\n"
"hello: sends hello world message\n"
"get name: gets the name for your ip address\n"
"set name: sets the name for your ip address\n"
"download: download a file from the server\n"
"cat gay: :3\n"
"null: sends a null character\n"
"return: sends a return character\n"
"any other command: sends a confirmation message\n"
}

SERVER_HELP_MESSAGE = {
    "\ncommands:\n"
    "help: dislpays this message\n"
    "quit: closes the server\n"
    "log: logs a custom message\n"
    "clients: prints a list of connected clients\n"
    "names: prints a list of saved names\n"
    "send: sends a message to a client by index in clients list\n"
    "any other command: displays unknown command message\n"
}
