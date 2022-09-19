# Run Task
The `run-task.sh` is a wrapper shell script around the AWS run task command for starting ECS tasks. It helps setup and find the parameters necessary for starting an ECS task.

# Setup
This command requires you to have the [AWS CLI](https://aws.amazon.com/cli/) setup and configured locally.

It also heavily uses `jq` for parsing and generating the CSV configurations.

# Usage

`./run-task.sh -a your.name -e test -t your-task-definition` is the most basic way to run a task.

The script has the following parameters:
* `-a` - The author running the script (eg. if your name is Bob Smith, put `-a bob.smith`)
* `-e` - The environment you want to run the script in (eg. `-e test`)
* `-t` - The ECS task definition you want to run (Your task definitions can be found at https://us-east-1.console.aws.amazon.com/ecs/home#/taskDefinitions , eg `-t db-migrate-up`)
* `-s` - (Optional) - The subnets the ECS task could run in (eg. `-s '["subnet-123456789", "sg-567890654"]'`)
    * If no subnet is specified, the script will fetch all subnets attached to the account.
* `-g` - (Optional) - The security group IDs to attach to the ECS task (eg. `-g '["sg-1234", "sg-3456"]'`)
    * If no security groups are specified, the `csv-handler` security group is fetched (TODO)

## Template Files
Two JSON template files exist which are used to help format the JSON configurations.

### Network config
The network config should be left as-is, as the subnet and security groups are specified as described in the usage section above.

### Container overrides
The container overrides are used for adjusting the ECS task you're running.

* `name` - Specifies what ECS container to run the ECS task in (by default is `test-mock-api-container` at the moment.) 
* `command` - (Optional) What command to run for the ECS task. **This overrides whatever the default command for a task is**. The original command will not run, and instead this command will be run, which means it is possible to use an existing ECS task to run one that hasn't been fully configured.
    * Each separate word in the command should be an item in an array. For example, to run `poetry run db-migrate-up` you would want to specify `["poetry", "run", "db-migrate-up"]`.
* `environment` - (Optional) Environment variable overrides to change the defaults on the container.

Note that the command and environment do not change the ECS task itself, and only override the values for the run you are starting. Running the task again without any overrides will use the defaults.

```json
{
  "containerOverrides": [
    {
        "name": "test-mock-api-container",
        "command": ["poetry", "run", "db-migrate-up"],
        "environment": [
            {
                "name":"LOG_FORMAT",
                "value":"json"
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
* The container name is hardcoded in the container overrides. Ideally it should factor in the environment + potentially vary with the ECS task.
* Network configuration should not have public IP addresses, however we need to reconfigure our networking to make that work.