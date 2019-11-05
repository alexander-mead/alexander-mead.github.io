To update the website on the PHAS public server do `ssh -Y mead@ssh.phas.ubc.ca` and then the public webpages are in `/www/pubHtml/mead`. There is a symbolic link to this in my home directory `/home/mead`. I have set up a git repository on the physics web server, so you just need to go to `/www/pubHtml/mead` and do `git pull` to get the latest version. Note that you may also have to change the file permissions in order to make the website viewable to the public. This can be achieved with `chmod a+rX *` (noting the capial `X` carefully).

Note that you will need to manually update `images/cv.pdf`.

(Obsolete) To transfer this to the UBC PHAS server you should use FileZilla. FileZilla does not seem to work from UBC so I should do this transfer from home. Also I need to 'quick connect' to the sftp address.

This UBC PHAS version of the website lives here: http://www.phas.ubc.ca/~mead/
