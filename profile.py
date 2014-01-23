#!/usr/bin/python
#
# Script to pull provisioning profiles from Apple's developer portal.
# By Alexey Baj <alexey.baj@gmail.com> for Rob Terrell / TouchCentric
#
# Copyright 2010 TouchCentric LLC. All rights reserved.
#

import sys, re, urllib, urllib2, urlparse, cookielib, gzip, StringIO, optparse, os

# Apple cookie issue workaround 
# http://bugs.python.org/issue3924
class MyCookieJar(cookielib.CookieJar):
    def _cookie_from_cookie_tuple(self, tup, request):
        name, value, standard, rest = tup
        version = standard.get('version', None)
        if version is not None:
            version = version.replace('"', '')
            standard["version"] = version
        return cookielib.CookieJar._cookie_from_cookie_tuple(self, tup, request)

def fetch(url, data=None):
    data, headers = fetch_with_headers(url, data)
    return data

def bail_out(msg):
    print >>sys.stderr, msg
    sys.exit(1)

def fetch_with_headers(url, data=None):
    
    if data:
        data = urllib.urlencode(data)
    
    req = urllib2.Request(url, data)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows; U; Windows NT 5.1; en; rv:1.9.2) Gecko/20100115 Firefox/3.6 (.NET CLR 3.5.30729)")
    req.add_header("Accept-encoding", "gzip")

    x = urllib2.urlopen(req)
    data = x.read()
    if x.headers.get('content-encoding', None) == 'gzip':
        data = gzip.GzipFile(fileobj=StringIO.StringIO(data)).read()

    return data, x.headers

def extract_helper(regex, data):
    match = re.search(regex, data)
    if match:
        return match.group(1)
    raise Exception('Unexpected web page structure')

def downloadProfilesFromPageContent( content, provision_url, specifiedProfileName=None ):
	downloadable_links = re.findall( 'href="(.+blobId=(.+))">', content )
	if not downloadable_links:
		return False

	if specifiedProfileName:
		match = re.findall( 'href=".+view\.action\?provDisplayId=(.+)">(<span>|)(.+?)</', content )    
		match = [x[0] for x in match if x[2] == specifiedProfileName]
		if not match:
			return False

		downloadable_links = [x for x in downloadable_links if x[1] == match[0]]
		if not downloadable_links:
			return False

	for link in downloadable_links:
		data, headers = fetch_with_headers( urlparse.urljoin( provision_url, link[0] ) )
		fname = extract_helper( 'filename=(.+)', headers['Content-Disposition'] )
		with open( fname, 'wb' ) as f:
			f.write( data )
			print "Downloaded a profile named: %s [%s]" % ( fname, link[0] )

		if options.openAfterSaving:
			os.system( 'open "'+fname+'"' )

	return True


# handle cookies 
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(MyCookieJar()))
urllib2.install_opener(opener)

# process options
p = optparse.OptionParser( description='A script to fetch provision profiles from Apple site', prog='profile.py', \
    version='1.0', usage='usage: %prog file -a <appleID> -p <password> -t <team> -P <profile_name> -o')

p.add_option('-a', "--account", dest='appleID', help='Account\'s Apple ID')
p.add_option('-p', "--password", dest='password', help='Password')
p.add_option('-t', "--team", dest='team', help='Team')
p.add_option('-P', "--profile", dest='profile', help='Profile Name')
p.add_option('-o', "--open", action="store_true", default=False, dest='openAfterSaving', help='open after saving')
options, arguments = p.parse_args()

if not options.appleID or not options.password:
    bail_out('Both Apple ID and password have to be specified')

#https://developer.apple.com/devcenter/ios/index.action
initial_url = 'http://developer.apple.com/iphone/index.action'





# determine login url
data = fetch( initial_url )
login_url = extract_helper( 'href="(.+?login.+)"', data )


# fetch login page
data = fetch( login_url )
form_action = urlparse.urljoin( login_url, extract_helper( 'action="(.+DSAuthWeb\.woa.+)"' , data ) )


# perform login, if the page still has the login URL assume a login failure
data = fetch( form_action, { 'theAccountName' : options.appleID, 'theAccountPW' : options.password } )
if data.find( 'DSAuthWeb' ) != -1:
    bail_out( "Provided credentials are not authorized." )


# if we fetch the initial URL again and the content contains 'saveTeamSelection',
# assume that we are being asked to choose a team
data = fetch( initial_url )
if data.find( 'saveTeamSelection.action' ) != -1:
    match = re.search( 'value="(.+)">%s</option>' % options.team, data )
    if not match:
        bail_out( 'Team %s is not found.' % options.team )
        
    form_action = urlparse.urljoin( initial_url, '/iphone/saveTeamSelection.action' )
    data = fetch( form_action, { 'memberDisplayId' : match.group(1), 'action:saveTeamSelection!save' : 'Continue' } )


# no idea what /iphone/my/ indicates, somehow the profile urls are diff.
if data.find( '/iphone/my/' ) == -1:
    provision_url = 'http://developer.apple.com/iphone/manage/provisioningprofiles/index.action'
else:
    provision_url = 'http://developer.apple.com/iphone/my/provision/index.action'


# fetching list of dev. profiles
data = fetch( provision_url )


# search in dev. profiles for a match or download all
if( downloadProfilesFromPageContent( data, provision_url, options.profile ) and options.profile ):
	# specified profile was found in the dev. profiles - stop processing
	sys.exit( 0 )


# follow the 'Distribution' Link
if data.find( 'viewDistributionProfiles.action' ) == -1:
    bail_out( "Could not locate the Distribution Profiles link" )

dist_profiles_relative_url = extract_helper( 'href="(.+viewDistributionProfiles.+)"', data )
data = fetch( urlparse.urljoin( initial_url, dist_profiles_relative_url ) )


# search in dist. profiles for a match or download all
if( downloadProfilesFromPageContent( data, provision_url, options.profile ) is False ):
	bail_out( "No profiles named %s were found in the dev. or dist. profiles" % options.profile )
