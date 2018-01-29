#!/usr/bin/env python
import os, sys, getopt, argparse, fnmatch, errno, subprocess, tempfile, platform, getpass, pprint, shutil
from subprocess import call

#program name available through the %(prog)s command
#can use prog="" in the ArgumentParser constructor
#can use the type=int option to make the parameters integers
#can use the action='append' option to make a list of options
#can use the default="" option to automatically set a parameter
parser = argparse.ArgumentParser(description="Install the Boulder based LaTex style files.",
                                 epilog="And those are the options available. Deal with it.")
group = parser.add_mutually_exclusive_group()
parser.add_argument("-nha","--nohash", help="Will run texhash command once the files are copied",
                    action="store_false")
group.add_argument("-q", "--quiet", help="decrease output verbosity to minimal amount",
                   action="store_true")
parser.add_argument("-m","--macports", help="modify the beamer base path on OSX if the user installed TexLive using macports",
                    action="store_true")
parser.add_argument("-p","--path", help="alternate path to the beamer base folder in the latex distribution")
parser.add_argument("-t","--texhash", help="alternate path to the texhash executable")
group.add_argument("-v", "--verbose", help="Increase output verbosity of lcg-cp (-v) or srm (-debug) commands",
                    action="store_true")
parser.add_argument('--version', action='version', version='%(prog)s 1.01')
parser.add_argument("-y", "--texlive_year", help="The texlive distribution year",
                    default="2015")
args = parser.parse_args()
if(args.verbose):
     print 'Number of arguments:', len(sys.argv), 'arguments.'
     print 'Argument List:', str(sys.argv)
     print "Argument ", args, "\n"

#
# Global Variables
#

QUIET             = args.quiet
VERBOSE           = args.verbose
DOHASH            = args.nohash
TEXLIVE_YEAR      = args.texlive_year
ALTERNATE_PATH    = args.path
ALTERNATE_TEXHASH = args.texhash
MACPORTS          = args.macports


theme_path = ""
color_path = ""
Outer_path = ""

OS = ""
flavor = ""
version = ""

def check_linux_folders():
    global theme_path
    global color_path
    global outer_path
    basepath = ALTERNATE_PATH if not ALTERNATE_PATH==None else "/usr/share/texmf/tex/latex/beamer/"
    theme_path = basepath+"base/themes/theme/"
    color_path = basepath+"base/themes/color/"
    outer_path = basepath+"base/themes/outer/"
    # To check if it is a directory (and it exists) use os.path.isdir
    # To check if something exists (direcotry, file, or otherwise), use os.path.exists
    theme = os.path.isdir(theme_path)
    color = os.path.isdir(color_path)
    outer = os.path.isdir(outer_path)
    if not QUIET: print "Themes exists? " + str(theme)
    if not QUIET: print "Color themes exists? " + str(color)
    if not QUIET: print "Outer themes exists? " + str(outer)

    if not theme:
        print "ERROR::The path to the beamer themes ("+str(theme_path)+") does not exist."
        print "Cannot continue."
        sys.exit()
    if not color:
        print "ERROR::The path to the beamer colors ("+str(color_path)+") does not exist."
        print "Cannot continue."
        sys.exit()
    if not outer:
        print "ERROR::The path to the beamer outer themes ("+str(outer_path)+") does not exist."
        print "Cannot continue."
        sys.exit()

def check_osx_folders():
    global theme_path
    global color_path
    global outer_path

    # Check for the base path to the files
    basepath=""
    if ALTERNATE_PATH != None:
        basepath = ALTERNATE_PATH
    elif MACPORTS:
        basepath = "/opt/local/share/texmf-texlive/tex/latex/"
    else:
        basepath = "/usr/local/texlive/"+TEXLIVE_YEAR+"/texmf-dist/tex/latex/"
    texlive = os.path.isdir(basepath)
    if not QUIET: print "TexLive exists? " + str(texlive)
    if not os.path.isdir(basepath):
        print "ERROR::The base bath to the texlive distribution ("+str(basepath)+")does not exist."
        print "Cannot continue."
        sys.exit()

    # Check to see if the beamertheme-boulder folder needs to be made
    basepath+="/beamertheme-boulder/"
    if not QUIET: print "Make beamertheme-boulder folder? " + str(not os.path.isdir(basepath))
    if not os.path.isdir(basepath):
        os.mkdir(basepath)

    theme_path = basepath
    color_path = basepath
    outer_path = basepath
    theme = os.path.isdir(theme_path)
    color = os.path.isdir(color_path)
    outer = os.path.isdir(outer_path)
    if not QUIET: print "Themes exists? " + str(theme)
    if not QUIET: print "Color themes exists? " + str(color) 
    if not QUIET: print "Outer themes exists? " + str(outer)

    if not theme:
        print "ERROR::The path to the beamer themes ("+str(theme_path)+") does not exist."
        print "Cannot continue."
        sys.exit()
    if not color:
        print "ERROR::The path to the beamer colors ("+str(color_path)+") does not exist."
        print "Cannot continue."
        sys.exit()
    if not outer:
        print "ERROR::The path to the beamer outer themes ("+str(outer_path)+") does not exist."
        print "Cannot continue."
        sys.exit()

def privledge_check():
    user = getpass.getuser()
    if not QUIET: print "User = " + str(user)
    if user != 'root':
        print "Sorry, you are not \"root\" and do not have enough privledges to continue."
        sys.exit()

def run_checks():
    print "************************************"
    print "* Running checks on the system ... *"
    print "************************************"

    privledge_check()

    kernel = platform.system()
    global OS
    global flavor
    global version
    if kernel == 'Linux':
        OS = "Linux"
        flavor = platform.linux_distribution()[0]
        version = platform.linux_distribution()[1]
        if not QUIET: print str(flavor) + "(" + str(OS) + ")" + str(version)
        check_linux_folders()
    elif kernel == 'Darwin':
        OS = "OSX"
        flavor = "Unknown"
        version = platform.mac_ver()[0]
        if not QUIET: print str(OS) + " " + str(version)
        check_osx_folders()
    else:
        print "ERROR::Unknown OS. Cannot confirm that installation will be successful. Process will not continue."
        sys.exit()

    print

def copy_set_of_files(dict, folder):
    for dst in dict:
        if not QUIET: print "Doing folder " + str(dst) + " ... "
        for f in range(1,len(dict[dst])):
            src  = dict[dst][f]
            dest = dict[dst][0]
            if not QUIET: print "\tCopying " + str(folder) + str(src) + " to " + str(dest) + " ... ",
            shutil.copy2(folder+src,dest)
            if not QUIET: print "DONE"

def copy_files():
    print "**********************************************"
    print "* Copying the files to the correct paths ... *"
    print "**********************************************"
    copyfileBeamerDict = {
        'theme' : (theme_path, "beamerthemeboulder.sty"),
        'color' : (color_path, "beamercolorthemeboulder.sty", "beamercolorthemeboulderbox.sty"),
        'outer' : (outer_path, "beamerouterthememiniframesboulder.sty", "UniversityLogos/beamerouterthemeboulderlogoreverse.pdf", "UniversityLogos/beamerouterthemeboulderlogoonelinecrop.pdf", "ExperimentLogos/beamerouterthemeCMS.png","ExperimentLogos/beamerouterthemeCDF.png","LaboritoryLogos/beamerouterthemeCERN.png","LaboritoryLogos/beamerouterthemeFNAL.png")
    }

    if VERBOSE and not QUIET:
        print "Dictionary"
        print "----------"
        pprint.pprint(copyfileBeamerDict)
        print

    copy_set_of_files(copyfileBeamerDict, "./")
    print

def do_tex_hash():
    print "***********************"
    print "* Running texhash ... *"
    print "***********************"

    if (ALTERNATE_TEXHASH!=None):
        os.system(ALTERNATE_TEXHASH+"/texhash")
    elif OS=="OSX":
        if MACPORTS:
            os.system("/opt/local/bin/texhash")
        else:
            os.system("/usr/local/texlive/"+TEXLIVE_YEAR+"/bin/x86_64-darwin/texhash")
    elif OS=="Linux":
        os.system("/usr/local/texlive/"+TEXLIVE_YEAR+"/bin/x86_64-linux/texhash")
    else:
        os.system("texhash")

run_checks()
copy_files()
if DOHASH:
    do_tex_hash()
