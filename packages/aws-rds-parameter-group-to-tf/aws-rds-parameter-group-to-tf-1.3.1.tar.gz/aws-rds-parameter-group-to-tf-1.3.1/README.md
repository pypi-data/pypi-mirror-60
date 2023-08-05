# AWS RDS Parameter Group To Terraform Converter

Converts AWS RDS Parameter Group to a Terraform object. Helps during database major version upgrades.

## Requirements

1. Python3
2. A working `awscli` with read access to RDS.

## Installation

`pip install aws-rds-parameter-group-to-tf`

## Usage

Directly using the CLI:
```bash
$ aws configure # Make sure you are authenticated with AWS.
$ parametergrouptotf --name my-db-parameter-group
```

Or if you have your parameter group already in JSON format:
```bash
$ cat your-param-group.json | parametergrouptotf --stdin
```
