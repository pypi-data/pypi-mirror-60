import readline
import shlex
import app as App
import utils
import config

print('Enter a command to do something, e.g. `build`.')
print('To get help, enter `help`.')

while True:

    try:
        cmd, *args = shlex.split(input('> '))
    except:
        cmd = None
        print("You didn't pass a command")

    if cmd == None:
        print('...')

    elif cmd == 'exit':
        break

    elif cmd == 'help':
        print('...')

    elif cmd == 'build':
        App.init()
    elif cmd == 'preview':

        locales = dict(
            staging=config.web["staging"],
            production=config.web["production"]
        )

        if args[0] in locales:
            locale = str(args[0])
        else:
            locale = input("Which location? Type: staging or production: ")

        if locale == "staging":
            port = config.staging_port
        else:
            port = config.production_port

        utils.preview(locales[locale], port)

    else:
        print('Unknown command: {}'.format(cmd))
