# notion-log-exec

![](https://api.travis-ci.org/Adjective-Object/notion-log-exec.svg?branch=master)

Run a command and report the result back to notion

```
usage: notion-log-exec [--config config] [--log_failure_only]  [command_args [command_args ...]]


Runs a command and reports the result back to a collection row on Notion

positional arguments:
  command_args

optional arguments:
  -h, --help            show this help message and exit
  --config config, -c config
                        Path to a config file
  --log_failure_only    Append an entry to the log only when the command fails
```
