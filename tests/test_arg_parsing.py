from konsoru import CLI


def check_args(*args):
    print('args =', args)


cli = CLI(enable_traceback=True)
cli.add_function(check_args, name='check')
cli.loop()
