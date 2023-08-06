from .mac import MacGen
from .args import get_args

class Cli:
    def __init__(self):
        self.args = get_args()

        self.macgen = MacGen()

    def run(self):
        args = {
            'sep': '' if self.args.no_separator else self.args.separator,
            'is_multicast': self.args.is_multicast,
            'is_local': self.args.is_local,
        }
        mac = self.macgen.generate_text(**args)
        print(mac)
