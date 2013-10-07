import sys
import git_version

if __name__ == "__main__":
    

    if len( sys.argv ) < 2:
        print "Usage: %s initial-path" % sys.argv[0]
        exit(-1)


    git_root = git_version.locate_git_root( sys.argv[1] )
    
    #print "git root: %s" % str(git_root)

    code_version = None
    if git_root is not None:
        code_version = git_version.get_code_version( git_root )

    #print "code version: %s" % code_version
    print code_version

