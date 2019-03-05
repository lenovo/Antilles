# File about user home template

```
SOURCES
  ├── profile.d
  │   ├── antilles-user-ssh-key-check.csh
  │   └── antilles-user-ssh-key-check.sh
  └── skel
      └───.ssh
          ├── config
          └── authorized_keys -> id_ecdsa.pub
```

- file under profile.d should install to /etc/profile.d
- file under skel should install to /etc/skel
