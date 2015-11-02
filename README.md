cpm 2 pass
==========

This should convert [cpm](https://github.com/comotion/cpm) password databases to [pass](http://www.passwordstore.org/) passwords.


Usage
-----

```
usage: cpm2pass.py [-h] -i INFILE [-t {cpm,plain}] -m {simple,manual}
                   [-p PREFIX]

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        input file
  -t {cpm,plain}, --type {cpm,plain}
                        cpm file type (for debugging)
  -m {simple,manual}, --method {simple,manual}
                        choose which method to use to create pass entries
  -p PREFIX, --prefix PREFIX
                        add a prefix to all entries

```


Status
------

Worksforme.

I migrated ~90 passwords using this script without an exception ;).


License
-------

BSD 3-Clause. 
