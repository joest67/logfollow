"""Control commands for running server.

This module should provide all necessary commands for working
with application environment, installation and post-installation
tuning and so on.

To use this utils just call ``logfollowctl`` with passed function name
as fisrt param.
"""

import os
import sys

from logfollow.install import StaticFilesUploader, STATIC_DIR

def upload_scripts(*args):
    """Upload JS/CSS files from CDN servers to local directory
    in order to work with project without internet connection.
    """
    StaticFilesUploader.upload()

def supervisor_config(*args):
    """Generate simple configuration for running logfollowd 
    server under supervisord.

    If first given argument will be the string with ".conf" suffix, 
    it will be used as full file name where we should dump generated 
    configuration. In other case it will be dump directly to STDOUT.

    All other arguments will be used as params for  ``logfollowd.py`` 
    server start. 
    """
    name = 'logfollowd'
    log = '/var/log/{name}.log'.format(name=name)

    # Check where we should dump generate configuration
    if len(args) and args[0][-5:] == '.conf':
        output = open(args[0], 'w')
        args = args[1:]
    else:
        output = sys.stdout

    print >> output, "\n".join([
        "[program:{name}]".format(name=name),
        "command=logfollowd.py {params}".format(params=' '.join(args)),
        "directory={dir}".format(dir=STATIC_DIR),
        "autorestart=true",
        "startsecs=5",
        "redirect_stderr=true",
        "stdout_logfile={log}".format(log=log),
        "user={user}".format(user=os.getlogin())
    ])

def check_env(*args):
    raise NotImplementedError()

if __name__ == '__main__':
    try:
        globals()[sys.argv[1]](*sys.argv[2:])
    except IndexError:
        print "Please, provide command to execute"    
    except KeyError:
        print "Unknown command given: {0}".format(sys.argv[1])
    except Exception, e:
        print "Error during command execution: {0}".format(str(e))
