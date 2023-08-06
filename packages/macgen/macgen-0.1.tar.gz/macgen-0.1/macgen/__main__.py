from macgen.cli import Cli

def cli():
    try:
        cli_app = Cli()
        cli_app.run()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    cli()
