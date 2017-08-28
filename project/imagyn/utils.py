import os
import argparse


class IsRWDir(argparse.Action):
    """
    Argpase action to check if a directory has read and write permissions
    """
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("output_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK & os.W_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("output_dir:{0} does not have R/W access".format(prospective_dir))
