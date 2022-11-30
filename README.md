# Well Architected Framework Review Cli

A python tool to create or update Well Architected Tool workloads with preconfigured answers which are solved already by central Landing Zone solutions. Can be used to migrate workloads from one account to another. Can be used to store custom lens templates and to publish them to your AWS accounts.

## Prerequisites
To run the tool it is required that AWS CLI and python is installed on the execution environment.

### AWS CLI v2
AWS CLI v2 can be installed following the [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
After installing the AWS CLI the AWS credentials are also needed to be configured:
```sh
aws configure
```

The tool will use the default environment profile or the one which is configured at `AWS_PROFILE` envrionment variable.

### python
Python can be downloaded and installed from this location: [python.org](https://www.python.org/downloads/).

* Using pip, install needed libraries 
```sh
pip install -r requirements.txt
```

### Usecases

Publish custom lenses.
Create new workloads.
Update workloads.
Save workload content with different lenses into templates.
Generete new templates for different lenses.
List workloads.

### Usage

Well-architected framework review CLI tool is helping to handle automatically some well-architected tool functionalities. See subcommands for more details.

```sh
wafr-cli.py [-h] {manage-template,create-workload,update-workload,publish-lens} ...
```

```sh
positional arguments:
  {manage-template,create-workload,update-workload,manage-lens}
                        Select one of the subcommands.
```
```sh
optional arguments:
  -h, --help            show this help message and exit
```

#### Examples

Publish new lens:

```sh
wafr-cli.py publish-lens -t lenses\eks.json
```

Create new workload:

```sh
wafr-cli.py create-workload -t templates\tsyeks.yaml -w example_workload -d "Just and example" -e pre-prod - John Doe -ds
```

### Manage templates

Commands to generate and save templates. Also used to list workload from which the template can be generated.

```sh
wafr-cli.py manage-template [-h] [-w WORKLOADID] [-o OUTPUTFILE] [-s] [-l] [-c {eks}]
```

```sh
optional arguments:
  -h, --help            show this help message and exit
  -w WORKLOADID, --workloadid WORKLOADID
                        An already available workload id from where the tool will get the questions and answers.
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        The location of the file where the generated template will to be saved.
  -s, --saveworkload    By activating this option the content of the workload will be saved to the template. If not used the behaviour is that a new default template is generated
  -l, --listworkloads   List the available workload ids of the currently used account.
  -c {tsyeks}, --customlens {tsyeks}
                        Generate custom lens template from an already existing custom lens workload.
```

### Creating new workloads

Create workload can be used to generate new workload in the currently configured account with standard and custom templates. The templates can be of different lens type, e.g. standard well-architected or custom eks       
lens.

```sh
wafr-cli.py create-workload [-h] -t TEMPLATE_FILE_PATH -w WORKLOADNAME -d DESCRIPTION -e {prod,pre-prod} [-a [ACCOUNTIDS ...]] [-r [REGIONS ...]] -o REVIEWOWNER [-ds] [-ta {enable,disable}]
```

```sh
optional arguments:
  -h, --help            show this help message and exit
  -t TEMPLATE_FILE_PATH, --templatefile TEMPLATE_FILE_PATH
                        Template file path used to create a new workload from. Default templates in the templates folder.
  -w WORKLOADNAME, --workloadname WORKLOADNAME
                        Name of the new workload.
  -d DESCRIPTION, --description DESCRIPTION
                        Description of the new workload.
  -e {prod,pre-prod}, --environment {prod,pre-prod}
                        Environment where the workload is running [prod, pre-prod].
  -a [ACCOUNTIDS ...], --accountids [ACCOUNTIDS ...]
                        The AWS account IDs where the workload is running.
  -r [REGIONS ...], --regions [REGIONS ...]
                        The regions where the workload is running. e.g. eu-central-1.
  -o REVIEWOWNER, --reviewowner REVIEWOWNER
                        The name of the reviewer who created this WAFR workload.
  -ds, --disablestandard
                        Disable the questions from the standard lens. Usable when the workload is created with custom lens.
  -ta {enable,disable}, --trustedadvisor {enable,disable}
                        Enable or disable the Trusted Advisor integration [enable, disable]
```

### Updating existing workloads

Update workload can be used to update existing workloads in the currently configured account with standard and custom templates. The templates can be of different lens type, e.g. standard well-architected or custom eks   
lens.

```sh
wafr-cli.py update-workload [-h] -t TEMPLATE_FILE_PATH -w WORKLOADNAME [-ds]
```

```sh
optional arguments:
  -h, --help            show this help message and exit
  -t TEMPLATE_FILE_PATH, --templatefile TEMPLATE_FILE_PATH
                        Template file path used to create a new workload from. Default templates in the templates folder.
  -w WORKLOADNAME, --workloadname WORKLOADNAME
                        Name of the updated workload.
  -ds, --disablestandard
                        Disable the questions from the standard lens. Usable when the workload is created with custom lens.
```

### Publishing custom lenses

Publish a new custom lens version or creates a new one if does not exist.

```sh
wafr-cli.py publish-lens [-h] -t LENS_FILE_PATH -v LENSVERSION
```

```sh
optional arguments:
  -h, --help            show this help message and exit
  -t LENS_FILE_PATH, --templatepath LENS_FILE_PATH
                        Create a new custom lens version from template. Example templates are in the lenses folder.
  -v LENSVERSION, --lensversion LENSVERSION
                        Publish a new version of your the lens.
```

## Planned features 
- Create automated test and pipeline
- Add functionality to remove the selections from remote workload if in template the question is not answered - handle carefully!
- Add workload and lens deletion functionality.
- Listing lenses and adding lens ARN as parameter
- Take current region as default

## Issues
