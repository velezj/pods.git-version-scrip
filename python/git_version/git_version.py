import os
import os.path
import git


#-----------------------------------------------------------------------------

##
## Returns the given path forced to be a directory (append "./" if not a dir)
def ensure_dir( path ):
    if path is None:
        return None
    if os.path.basename( path ) != '':
        return os.path.join( path, "./" )
    return path

#-----------------------------------------------------------------------------

##
## Return the root git directory for the git repository including the 
## given path. This is in particularly useful for submodules, which are
## git repositories themselves but we want to find the "parent" git repo
## which includes the submodules.
def locate_git_root( initial_path ):
    
    # get the real absolute path
    path = ensure_dir( os.path.realpath( os.path.normpath( os.path.dirname( initial_path ) ) ) )

    #print ".. initial path: %s" % path
    #print ".. path: %s" % path

    # search for ".git" folders until we hit the "topmost" consecutive
    # .git folder in the path
    top_most_git_path = None
    while( os.path.exists( path ) and path != "/" ) :
        
        # search for .git
        #print ".. checking path: %s" % path
        if os.path.exists( os.path.normpath( os.path.join( path, ".git/" ) ) ):
            top_most_git_path = path
                
        # go up hte path
        path = ensure_dir( os.path.normpath( os.path.join( path, "../" ) ) )
        
    #print "..topmost path: %s" % top_most_git_path
    #print "..retuning path: %s" % ensure_dir( top_most_git_path )
    return ensure_dir( top_most_git_path )
    



#----------------------------------------------------------------------------

##
## Returns a JSON string with the code version for the
## root git repo containing the given path.
## (optionally, do not wuery for hte root repo is use_given_path=True)
def get_code_version( repo_filename = None, 
                      return_empty_keys=False,
                      use_given_path=False):
    """Return the code repository version of the GIT repository at the given
       lcoation. If no location is given, the current working directory is
       used instead.
       Right now, this will alway assume you have the "origin" remote set up
       and that is the URL returned under repo_url.
       The returned version is a python dictionary with the following fields:
         { "repo_url" : "<url>",
           "branch" : "<branch>",
           "head" : "<commit-hashtag>",
           "head_date" : "<timestamp>",
           "diffs: [<all diffs from head>],
           "untracked_files" : [<all files untracked>]}
           
       If any field is empty ([]), then the return dictionary will not
       have the keys unless return_empty_keys=True is given as argument.
       """
    
    if repo_filename is None:
        repo_filename = os.getcwd()
    #print "Repo Filename: %s" % repo_filename
    repo_root = None
    if use_given_path:
        repo_root = repo_filename
    else:
        repo_root = locate_git_root( repo_filename )

    print "Repo Root: %s" % repo_root

    repo = git.Repo( repo_root )
    print "Repo: %s" % repo.git_dir 

    # gather all diffs from the current head
    for head in repo.heads:
        working_diffs = head.commit.diff( None, create_patch=True )
        all_diffs = { "deleted" : [],
                      "added" : [],
                      "modified" : [],
                      "renamed" : []}
        for d in working_diffs:
            if d.deleted_file:
                all_diffs["deleted"].append( { "path" : d.a_blob.path,
                                               "head" : 
                                               { "name" : head.name,
                                                 "commit" : head.commit.hexsha } } )
            elif d.new_file:
                all_diffs["added"].append( { "path" : d.b_blob.path,
                                             "head" : 
                                             { "name" : head.name,
                                               "commit" : head.commit.hexsha } } )
            elif d.renamed:
                all_diffs["renamed"].append( {"from" : d.rename_from,
                                              "to" : d.rename_to,
                                              "head" : 
                                              { "name" : head.name,
                                                "commit" : head.commit.hexsha } } )
            else:
                # OK, this is tricky:
                # We *only* get blobs if we have actual content change.
                # However, for submodules we will get a "diff" for
                # untracked changes with no blob
                if d.a_blob is not None:
                    all_diffs["modified"].append( {"path" : d.a_blob.path,
                                                   "patch" : d.diff,
                                                   "head" : 
                                                   { "name" : head.name,
                                                     "commit" : head.commit.hexsha } } )
                else:
                    # here, we have untracked content in the submodules
                    # So we recursively get their code version (for the
                    # submodule repo) and store it
                    # The information is in hte raw diff (nowehere else!)
                    raw_diff = d.diff
                    
                    # parse the raw diff to extract the submodule path
                    lines = raw_diff.split('\n')
                    if( len( lines ) != 5 ) :
                        
                        # this is not what we expect, 
                        # just make a raw diff section
                        all_diffs['modified'].append(
                            { "patch" : d.diff,
                              "head" :
                              { "name" : head.name,
                                "commit" : head.commit.hexsha } } )
                    else:
                        path = lines[0][5:]
                        git_path = os.path.join( repo.git_dir, ".." + path )
                        print "SUBMODULE: %s" % git_path
                        # sub_cv = get_code_version( git_path, 
                        #                            return_empty_keys = return_empty_keys,
                        #                            use_given_path = True )
                        # all_diffs["modified"].append(
                        #     { "submodule" : sub_sc } )
                        
                    
                    
                
    # ok, now gather all untracked files
    # (this will take care of using hte .gitignore! )
    ut = repo.untracked_files
    untracked_files = []
    for name in ut:
        path = os.path.join( repo.working_dir, name ) 
        
        # explicitly ignore job-local files
        # and last-changed-process.txt files
        if path.find( "job-local" ) != -1 or path.find( "last-change-processed" ) != -1:
            continue
        if path.find( "build/" ) != -1 or path.find("experiments/") != -1:
            continue
        with open( path ) as f:
            untracked_files.append( { "path" : path,
                                      "contents" : f.read(),
                                      "modified_time" : os.path.getmtime( path ) } )
    
    # create the resulting dictionary
    res = {
        "repo_url" : repo.remotes.origin.url,
        "branch" : repo.active_branch.path,
        "head" : repo.head.reference.commit.hexsha,
        "head_date" : repo.head.reference.commit.committed_date,
        "diffs" : all_diffs,
        "untracked_files" : untracked_files }
    if return_empty_keys == False:
        if len(untracked_files) == 0:
            del res["untracked_files"]
        if len(working_diffs) == 0:
            del res["diffs"]
    
    return res

#----------------------------------------------------------------------------
