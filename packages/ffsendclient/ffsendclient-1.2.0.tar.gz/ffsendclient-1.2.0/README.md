# Firefox Send Client #

```
         __.|.__
     .-"'..':`..`"-.
   .' .' .  :  . `. `.
  / .  FFSENDCLIENT . \
 /_ _._ _.._:_.._ _._ _\
   '   '    |    '   '
            |
            |
            |
         \  |  /
          \ | /
           \ /
            '
```

*Firefox Send API Client*

ffsendclient is a library for interfacing with Firefox Send <https://send.firefox.com/> or your own instance of it.

## Install ##
```
➜ pipenv install ffsendclient
➜ # ...or...
➜ pip3 install ffsendclient
```

## Usage ##
Basic file upload...
``` pythonstub
>>> import os
>>> from ffsendclient import SendClient
>>> send = SendClient('send.firefox.com')
>>> up_data = os.urandom(1024)
>>> fid, owner_token, url = send.upload('ffsendclient.bin', up_data)
>>> fid
'eb99746752a74975'
>>> owner_token
'fc8a7a910688869021be'
>>> url
'https://send.firefox.com/download/eb99746752a74975/#xsKqVUcdh_Dp6GDn2zUVLg'
```
... and continue to download:
```
>>> secret = url.split('#')[1]
>>> secret
'xsKqVUcdh_Dp6GDn2zUVLg'
>>> file_name, down_data = send.download(fid, secret)
>>> file_name
'ffsendclient.bin'
>>> up_data == down_data
True
```
Passwords, download limits and time limits are also supported. Full
documentation is at <https://gitlab.com/skorov/ffsendclient>.

## Supported ##
- Python 3.6+
- Firefox Send v3.0.21+

## Not yet supported ##
 - Multi-file upload/download
 - Firefox authentication

:copyright: (c) 2019 by Alexei Doudkine.
:license: Apache 2.0, see LICENSE for more details.
