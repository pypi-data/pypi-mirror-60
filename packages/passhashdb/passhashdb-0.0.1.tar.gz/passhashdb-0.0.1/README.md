passhashdb
==========
Password Hash Database is an efficient way of checking passwords
against a password (hash) list.

This is specifically written to handle the files from
[Have I been Pwned: Pwned Passwords][haveibeenpwned-passwords] lists.


# Setup
Install this package using `pip`:
```
$ sudo pip3 install passhashdb-x.x.x.tar.gz
```

Download the [latest password file][haveibeenpwned-passwords],
and extract the text file.

Convert the text format to binary "passhashdb" format. This will take a while!
```
$ hibp-to-passhashdb pwned-passwords-sha1-ordered-by-hash-v5.txt \
    pwned-passwords-sha1-ordered-by-hash-v5.bin
```

I recommend "installing" the file to `/usr/share`.


# Use with Samba
This can be used with Samba's [`check password script`][check-password-script]
hook to check passwords as they are changed.

I recommend writing a small wrapper script like this:
**`/etc/samba/check_password.sh`**
```sh
#!/bin/sh
PASSDB="/usr/share/pwned-passwords-sha1-ordered-by-hash-v5.bin"
LOGFILE="/var/log/samba/check-passhashdb.log"

exec /usr/local/bin/samba-check-passhashdb $PASSDB 2>> $LOGFILE
```

Then add this to `/etc/samba/smb.conf`:
```
check password script = /etc/samba/check_password.sh
```


[haveibeenpwned-passwords]: https://haveibeenpwned.com/Passwords
[check-password-script]: https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html#idm1473
