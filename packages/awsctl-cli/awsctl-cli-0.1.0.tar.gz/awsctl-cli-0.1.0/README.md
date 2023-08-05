# AWSCTL

`awsctl` is a utility for installing AWS packages on servers in the cloud. AWS packages such as Systems Manager, Cloudwatch, etc. have different installation methods which can be hard to manage when setting up a simple server. This package aims to make this as simple as `awsctl install ssm`.

## Usage

| Package | Command | Description |
|-|-|-|
| Cloudwatch | `awsctl install cloudwatch` | Installs the Cloudwatch agent and configures it to run on startup. |
| Systems Manager | `awsctl install ssm` | Installs the SSM agent and configures it to run on startup. |

## Operating System Support

Due to different installation methods we only support a subset of operating systems. We welcome additional operating systems!

| Operating System | Supported |
|-|:-:|
| Amazon Linux | :x: |
| Amazon Linux 2 | :white_check_mark: |
| Debian | :white_check_mark: |
| CentOS | :white_check_mark: |
| Red Hat | :white_check_mark: |
| Ubuntu 16.04 | :x: |
| Ubuntu 18.04 | :white_check_mark: |
