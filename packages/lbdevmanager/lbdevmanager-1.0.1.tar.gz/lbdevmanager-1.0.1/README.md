LHCb Dev Install manager
========================


Sets of tools that manage the packages installed on the DEV installation area

The lib has 3 different usages:

*  Verification of the yaml based on a schema
---------------------------------------------
`lbdevcheck [OPTIONS] validate <name_of_the_yaml.yaml>`

Available options:

`
  -h, --help            Show the help message and exit
  -d, --debug           Show debug information
`

*  Generation of the list of files to install in a separate branch
------------------------------------------------------------------
`lbdevcheck [OPTIONS] generate-list <name_of_the_yaml.yaml>`

Available options:

`
  -h, --help            Show the help message and exit
  -d, --debug           Show debug information
  -p <Gitlab token>, --gitlab_token= <Gitlab token>
                        Gitlab token used to login into gitlab. (Used if
                        the machine that runs the scripts has not been ssh paired)
  -u  <Gitlab user>, --gitlab_user= <Gitlab user>
                        Gitlab user used to login into gitlab (Used if
                        the machine that runs the scripts has not been ssh paired)
  -g  <Gitlab repository>, --gitlab_repo= <Gitlab repository>
                        Gitlab repositor where the yaml file is stored
  -b  <Gitlab branch>, --gitlab_branch= <Gitlab branch>
                        Gitlab branch the name of the branch used to store the list of files
                        to install. The default value is installed_files
`

The usages are called in the CI on cvmfsdev-sw. The last one needs to be called on the machine that is using lbinstall (e.g CVMFS stratom 0)

The script will automatically compute the diff from the lastinstalled tag, install the files and then update the lastinstalled tag.