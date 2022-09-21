# Run Task
The `run-task.sh` is a wrapper shell script around the AWS run task command for starting ECS tasks. It helps setup and find the parameters necessary for starting an ECS task.

# Setup
This command requires you to have the [AWS CLI](https://aws.amazon.com/cli/) setup and configured locally. Make sure to [setup your AWS account credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) before running this script. Running `aws configure` should also walk you through whatever is necessary to get connected.

An easy way to validate you have the AWS CLI configured correctly is to do `aws s3 ls` which will list any S3 buckets in your account.

The script also heavily uses `jq` for parsing and generating the CSV configurations, which should automatically be installed on any machine.

# Usage

`./run-task.sh -a your.name -e test -t your-task-definition` is the most basic way to run a task.

The script has the following parameters:
* `-a` - The author running the script (eg. if your name is Bob Smith, put `-a bob.smith`)
* `-e` - The environment you want to run the script in (eg. `-e test`)
    * This assumes that the ECS cluster you want to run in is named exactly your environment (ie. a cluster named just `test`)
    * This also is used to determine the ECS container to override and run with (eg. `{ENVIRONMENT}-mock-api-container`)
* `-t` - The ECS task definition you want to run (Your task definitions can be found at https://us-east-1.console.aws.amazon.com/ecs/home#/taskDefinitions , eg `-t db-migrate-up`)
* `-s` - (Optional) - The subnets the ECS task could run in (eg. `-s '["subnet-123456789", "sg-567890654"]'`)
    * If no subnet is specified, the script will fetch all subnets attached to the account.
* `-g` - (Optional) - The security group IDs to attach to the ECS task (eg. `-g '["sg-1234", "sg-3456"]'`)
    * If no security groups are specified, the `csv-handler` security group is fetched (TODO)

## Template Files
Two JSON template files exist which are used to help format the JSON configurations.

### Network config
The [network config template](./network_config.json.tpl) should be left as-is, as the subnet and security groups are specified as described in the usage section above, and values added to the file will be overriden by the script.

### Container overrides
The [container override template](./container_overrides.json.tpl) is used for adjusting configurations of the ECS task you're running.

* `name` - Specifies what ECS container to run the ECS task in - overriden automatically to `{ENVIRONMENT}-mock-api-container` at the moment.
* `command` - (Optional) What command to run for the ECS task. **This overrides whatever the default command for a task is**. The original command will not run, and instead this command will be run, which means it is possible to use an existing ECS task to run one that hasn't been fully configured.
    * Each separate word in the command should be an item in an array. For example, to run `poetry run db-migrate-up` you would want to specify `["poetry", "run", "db-migrate-up"]`.
* `environment` - (Optional) Environment variable overrides to change the defaults on the container.

Note that the command and environment do not change the ECS task itself, and only override the values for the run you are starting. Running the task again without any overrides will use the defaults.

See the [CLI documentation](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecs/run-task.html) for further details on container overrides you can specify.

You cannot override sensitive environment variables pulled from parameter store as those are only able to be set when the ECS container is created.
# Example

## Basic
You have an ECS task definition named `example-ecs-task-definition` that you want to run a script in. You want to run this script in your `test` environment, and want to run the ECS task without any overrides (ie. leaving the command, environment variables, subnets, and security groups alone).

You just need to run `./run-task.sh -a your.name -e test -t example-ecs-task-definition` which should startup your task with all the normal defaults.

## Override Example
You have an ECS task definition named `example-ecs-task-definition` that you want to run a script in. You want to run this script in your `test` environment, but want to override everything possible and set them instead as:
* The command run by the ECS task -> `poetry run db-migrate-up`
* The environment variables of the ECS task -> `LOG_FORMAT=json`
* The subnets -> `subnet-1234, subnet-4567`
* The security groups -> `sg-abcd`

Subnets and security groups need to be specified as command line parameters like so:
`./run-task.sh -a your.name -e test -t example-ecs-task-definition -s '["subnet-1234", "sg-4567"]' -g '["sg-abcd"]'`
Note that the formatting must match this format exactly with `'` quotes containing the array, and `"` quotes surrounding the names of the names of the subnets and security groups.

To override the command and environment variables, you'll need to open the [container_overrides.json.tpl](./container_overrides.json.tpl) file and edit it. The `name` field should be left alone as the script will overwrite any values, but you can set the command you want to run by adding command to override JSON. Do not attempt to specify a command as a single string with spaces as it will fail to run, each "word" of the command must be a separate string in the array.

Additionally, you can set as many environment variable overrides as you want by specifying the name and value you want for each one. For this example, your file would now look like:

```json
{
  "containerOverrides": [
    {
        "name": "PLACEHOLDER OVERRIDEN BY SCRIPT  - SEE README FOR HOW THIS GETS SET",
        "command": ["poetry", "run", "db-migrate-up"],
        "environment": [
            {
                "name":"LOG_FORMAT",
                "value":"json"
            },
            {
                "name":"OUTPUT_PATH",
                "value":"s3://bucket/path/to"
            }
        ]
    }
  ]
}
```

# TODO
As we are building this alongside some of our infrastructure setup, not everything is 100% setup. A few TODOs we will circle back to include:
* The subnets should be filtered to the correct VPC. Right now we only have one VPC, but if you run with multiple, you'll likely want to be able to choose the correct one (eg. a non-prod, or prod VPC which could be figured out by the environment variable)
* The security group fetched should ideally be something more general like one for all ECS tasks (and potentially more than 1).
* The container name is hardcoded to be `{ENV_NAME}-mock-api-container`. Ideally it should factory in the ECS task and choose the right container.
* Network configuration should not have public IP addresses, however we need to reconfigure our networking to make that work.