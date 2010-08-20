ProfilePuller
=============

A script to download provisioning profiles (.mobileprovision) from Apple's iPhone Developer Program Portal site. This can be particularly useful if you use continuous build integration, or if you have a bazillion profiles to manage.

This script was written by Alexey Baj for TouchCentric LLC (http://touchcentric.com) with some additions by Rob Terrell. 


Usage
-----

	Usage: profile.py file -a <appleID> -p <password> -t <team> -P <profile_name> -o

	Options:
	  --version                         show program's version number and exit
	  -h, --help                        show this help message and exit
	  -a APPLEID, --account=APPLEID     account Apple ID
	  -p PASSWORD, --password=PASSWORD  account Password
	  -t TEAM, --team=TEAM              Team name (if needed)
	  -P PROFILE, --profile=PROFILE     Profile Name to download (if not present, all will be downloaded)
	  -o, --open            			open after saving (for auto-adding to XCode)


This is a python script, so you will either need to set the executable bit on the file (i.e. chmod u+x profile.py) or execute the command with python.

	rob$ python ./profile.py --account "crazy8@mac.com" --password "whatever" --team "Stinkbot LLC" --profile "Wildcard Dev Profile" --open

and

	rob$ python ./profile.py -a "crazy8@mac.com" -p "whatever" -t "Stinkbot LLC" -P "Wildcard Dev Profile"


More Information
----------------

For more information, contact Rob Terrell at http://touchcentric.com

