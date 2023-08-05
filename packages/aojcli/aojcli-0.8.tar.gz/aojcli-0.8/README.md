# aojcli
AOJ submission tool on CLI  
[AIZU ONLINE JUDGE](http://judge.u-aizu.ac.jp/)

## System requirements
- Python 2.7
- libraries
    - [texttable](https://pypi.python.org/pypi/texttable/1.2.1)
    - [requests](https://github.com/requests/requests)

## Setup

### install
aojcli get credential from environment variables.  
You need to set your user id and password to environment variables.
```
$ pip install aojcli
$ echo 'export AOJCLI_ID=your_user_id_of_AOJ' >> ~/.bashrc
$ echo 'export AOJCLI_PASSWORD=your_password_of_AOJ' >> ~/.bashrc
```

### uninstall
```
$ pip uninstall aojcli
```

## Command

### submit
submit your code to AOJ.
```
$ aojcli submit ITP1_1_A C ITP1_1_A.c
```

### status
check your submission status of problem.
```
$ aojcli status ITP1_1_A
```

