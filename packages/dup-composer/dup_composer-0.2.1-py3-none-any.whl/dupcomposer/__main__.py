#!/usr/bin/env python3
"""Launch dupcomposer (CLI entrypoint)."""
import sys
import getopt
import os.path
from dupcomposer.backup_runner import read_config, BackupRunner
from dupcomposer.backup_config import BackupConfig

def main():
    # default config file to look for
    config_file = 'dupcomposer-config.yml'
    dry_run = False
    # Collecting and parsing options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:dh')
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    for opt, a in opts:
        if opt == '-c':
            if os.path.isfile(a):
                config_file = a
            else:
                usage()
                raise FileNotFoundError("Configuration file {} doesn't exist!"
                                        .format(a))
        elif opt == '-d':
            dry_run = True

    if not args or args[0] not in ['backup', 'restore']:
        print('backup|restore action is missing from the command!')
        usage()
        sys.exit(1)
        
    config_raw =  read_config(config_file)
    # Check if groups requested are valid
    for group in args[1:]:
        if group not in config_raw.get('backup_groups', {}):
            raise ValueError('No group {} in the configuration!'.format(group))

    # Setting up the environment
    config = BackupConfig(config_raw)
    runner = BackupRunner(config,args[0])

    # Do the actual run
    if dry_run:
        commands = runner.get_cmds_raw(args[1:])
        # Sorting keys for consistent ordering of output (for functional tests).
        for group in sorted(commands):
            print('Generating commands for group {}:\n'.format(group))

            for cmd in commands[group]:
                print(' '.join(cmd))

            print()
    else:
        # True run
        runner.run_cmds()
def usage():
    print("""-----
usage: dupcomp.py [-d] [-c <configpath>] backup|restore

optional arguments:
 -d                dry run (just print the commands to be executed)
 -c <configpath>   use the configuration file at <configpath>
-----""")
if __name__ == '__main__':
    main()
