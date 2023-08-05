# textlog2json

This is software in **ALPHA** stage.
Multiprocessing is only supported on POSIX systems.

textlog2json is a self learning application that converts log messages
written in natural language to structured JSON logs.
For example `Login tom, tries 3` becomes `{user: "tom", tries: "3"}`.

Can be used in any UNIX pipeline but the developers focus is on integrating
it into logstash for the use with the elastic stack, to allow aggregations
and advanced filters on logs formatted in natural language. 

It is possible to run textlog2json distributed over multiple instances.

## Setup

textlog2json is optimized to be used with
[pypy3](https://www.pypy.org/index.html) an alternative much faster python3
interpreter. textlog2json will also run with cpython, the default python
implementation, but at a much slower pace.

Parts of textlog2json are written in C and need to be compiled with cffi. If
you use pip, it will compile the code for you.

Installation
 - Install pypy3: http://pypy.org/download.html#installing (or use python3)
 - Install textlog2json with pip: `pip install textlog2json`
 
## Knowledge Management

![Data Flow](doc/textlog2json-flow.png)

textlog2json is a self learning application that learns about patterns in log
messages on the fly. It is designed to process a stream of continuous log data.

It works by clustering log messages and looking for variable
parts in messages. This means it needs to see at least two variations
of a log message, before it will extract values.

Derived knowledge about patterns is periodically synchronized with a relational
db. textlog2json is known to work with SQLite and MySQL. Multiple instances of
textlog2json can sync with a single knowledge db to work on the same set of log
data.

If you want to use textlog2json on a fixed set of logdata in most cases you
want to run textlog2json twice.

## Usage

Run `textlog2json --help` for all options.

### Processing a simple file

To structure a simple line seperated list of messages (logfile.txt). It is recomended
to process the file twice (on the frist pass to train the application, on the second
pass to process the data.

1. `textlog2json --db sqlite:///logdata.db --in-format text --in logfile.txt >/dev/null`
2. `textlog2json --db sqlite:///logdata.db --in-format text --in logfile.txt -out logfile.json`

### Integration with Logstash

To integrate textlog2json with logstash you need to run textlog2json as a service that reads
and writes to named pipes. Then you can use
[pipelines](https://www.elastic.co/de/blog/logstash-multiple-pipelines) in logstash to read
and write to textlog2json.

1. Create named pipes
```
mkfifo /run/textlog2json_in
chown logstash:logstash /run/textlog2json_in
mkfifo /run/textlog2json_out
chown logstash:logstash /run/textlog2json_out
```

2. Run textlog2json as service that reads and writes to the created pipes, you can use the following
systemd configuration:
```
[Unit]
Description=Textlog2json converts unstructured log messages to structured json

[Service]
Type=simple
Environment='LANG=en_US.UTF-8' 'LC_ALL=en_US.UTF-8'
Restart=always
RestartSec=60

User=logstash
Group=logstash

PermissionsStartOnly=true
ExecStartPre=mkdir -p /usr/local/textlog2json
ExecStartPre=-chown logstash:logstash /usr/local/textlog2json

ExecStart=/bin/bash -c 'tail -n +1 -f /run/textlog2json_in | textlog2json --in-format json --db "sqlite:////usr/local/textlog2json/textlog2json.db" --out /run/textlog2json_out'

[Install]
WantedBy=multi-user.target
```

3. Create a logstash pipeline that writes to textlog2json
```
[...]

output {
    pipe {
        command => "bash -c 'cat - > /run/textlog2json_in'"
        codec => "json_lines"
        ttl => -1
        enable_metric => false
    }
}
```

4. Create a logstash pipeline that reads from textlog2json

```
[...]

input {
    pipe {
        command => "tail -n +1 -f /run/textlog2json_out"
        codec => "json"
        enable_metric => false
    }
}
```
    
## License

Copyright (c) 2018 dmTECH GmbH, https://www.dmtech.de

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
