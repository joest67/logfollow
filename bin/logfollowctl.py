"""Control commands for running server.

This module should provide all necessary commands for working
with application environment, installation and post-installation
tuning and so on.
"""

import sys

def upload_scripts(*args):
    """Upload JS/CSS files from CDN servers to local directory
    in order to work with project without internet connection.
    """
    from logfollow.install import StaticFilesUploader
    StaticFilesUploader.upload()

def supervisor_config(*args):
    raise NotImplementedError()

def check_env(*args):
    raise NotImplementedError()

if __name__ == '__main__':
    try:
        globals()[sys.argv[1]](sys.argv[2:])
    except IndexError:
        print "Please, provide command to execute"    
    except KeyError:
        print "Unknown command given: {0}".format(sys.argv[1])
    except Exception, e:
        print "Error during command execution: {0}".format(str(e))
