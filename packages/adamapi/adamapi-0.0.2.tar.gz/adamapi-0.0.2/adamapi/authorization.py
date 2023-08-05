"""
Copyright (c) 2020 MEEO s.r.l.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import requests
import logging
logger = logging.getLogger( 'adamapi' )

from . import AdampyError


class Auth():
    def __init__( self, key=None, url=None ):
        """
        Authorization class used to manage users credentials
        """
        self.key = key
        self.url = url

    def authorize( self ):
        """
        try to autorize the adamapi to the target adam instance
        """
        #verify if key are valid
        self._check()

        url = os.path.join( 'accounts', 'api', 'auth' )
        r=self.client(url,{},"GET")
        #r = requests.get( url, headers = { 'Authorization': self.key} )
        res = r.json()
        if r.status_code !=200:
            raise AdampyError( res['response'] )
        else:
            logger.info( res )
            return res[ 'response' ]

    def _check( self ):
        """
        verify if the user key and the adam url are valid
        """
        self.getKey()
        self.getAdamEndpoint()

        if self.key is None:
            raise AdampyError( "key can not be None" )
        if self.url is None:
            raise AdampyError( "url (adam endpoint) can not be None" )

    def setKey( self, key ):
        """
        set the user key
        """
        self.key = key

    def setAdamEndpoint( self, url ):
        """
        set the adam endpoint url
        """
        self.url = url

    def getKey( self ):
        """
        key priority:
        1 - use the key declared on this module
        2 - use a key exported as envvars
        3 - try to retrieve the key from $HOME/.adamapirc
        """
        if self.key is not None:
            pass
        elif os.environ.get( 'ADAMPY_KEY') is not None:
            self.key = os.environ.get( 'ADAMPY_KEY' )
            logger.debug( 'Get key from envvar' )
        else:
            try:
                self.key = self._getRc()[ 'key' ]
                logger.debug( 'Get key from adamapirc' )
            except:
                None
        if self.key is None: #again
            logger.warning( "API key not specified" )
        return self.key

    def getAdamEndpoint( self ):
        """
        adam endpoint priority:
        1 - use the url declared on this module
        2 - use a url exported as envvars
        3 - try to retrieve the url from $HOME/.adamapirc
        """
        if self.url is not None:
            pass
        elif os.environ.get( 'ADAMPY_URL') is not None:
            self.url = os.environ.get( 'ADAMPY_URL' )
            logger.debug( 'Get url from envvar' )
        else:
            try:
                self.url = self._getRc()[ 'url' ]
                logger.debug( 'Get url from adamapirc' )
            except:
                None
        if self.url is None: #again
            logger.warning( "ADAM API endpoint not specified" )
        return self.url

    def _getRc( self ):
        """
        check if ~/.adamapirc file exist ant try to extract url and key from it
        """
        api_rc = os.environ.get( 'ADAMPY_RC', os.path.expanduser( '~/.adamapirc' ) )
        config_dict = {}
        if os.path.isfile( api_rc ):
            with open( api_rc ) as f:
                for line in f.readlines():
                    line = line.strip()
                    if line.lstrip( '#' ) == line:
                        try:
                            key, val = line.split( '=', 1 )
                            config_dict[ key.strip() ] = val.strip()
                        except:
                            logger.warning( 'Invalid settings in "%s" - %s' %( api_rc, line ) )
        return config_dict

    def client(self,query,params,request_type):
        """
        The client method that perfomr the requests appending the Authorization header
        """
        headers={ 'Authorization': self.key}
        url=os.path.join(self.url,query)

        if request_type=='GET':
            logger.info("Get request started")
            r=requests.get(url,params=params,headers=headers)
            return r
        elif request_type=='POST':
            logger.info("Post request started")
            r=requests.post(url,data=params,headers=headers)
            return r
        else:
            raise AdampyError( "Request type not supported" )

