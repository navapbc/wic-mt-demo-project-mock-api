#!/usr/bin/env bash
# Run an ECS task using supplied configurations.
#
# See README.md for details on how this script works.
set -o errexit -o pipefail

DIR=$(dirname "${BASH_SOURCE[0]}")

usage() {
    echo "Usage: ./run-task.sh -a YOUR.NAME -e ENV_NAME -t TASK_NAME"
    echo "ex: ./run-task.sh -a bob.smith -e test -t db-migrate-up"
    echo "See the README.md for further details"
    exit 1
}

# This parses CLI arguments mapping the letter params to variables
# Note that if you want to add more params, you need to add the letter
# to the string next to getopts below
while getopts ":a:e:t:s:g:" opt; do
    case $opt in
        a)
            AUTHOR="$OPTARG"
            ;;
        e)
            ENV_NAME="$OPTARG"
            ;;
        t)
            TASK_NAME="$OPTARG"
            ;;
        s)
            SUBNETS="$OPTARG"
            ;;
        g)
            SECURITY_GROUPS="$OPTARG"
            ;;
        \?)
            echo "Invalid option -$OPTARG"
            exit 1
            ;;
    esac

    # Error if an argument has no parameter
    case $OPTARG in
        -*) 
            echo "Option $opt needs a valid argument"
            exit 1
            ;;
    esac
done

# If the required environment variables are missing, print the usage info and error.
if [ -z "$ENV_NAME" ] || [ -z "$TASK_NAME" ] || [ -z "$AUTHOR" ]; then
  usage
fi

# If no security groups were specified, fetch them from AWS. The response is formatted as
# {
#   "SecurityGroups": [
#       {"GroupName": "csv-handler", GroupId: "sg-123456789", ...}  
# ]}
if [ -z "$SECURITY_GROUPS" ]; then
    # The jq command grabs all returned security group IDs and formats it into a JSON array
    SECURITY_GROUPS=$(aws ec2 describe-security-groups --group-names csv-handler | jq -r --compact-output "[.SecurityGroups[].GroupId]")
fi

# If no subnets specified, fetch them from AWS. The response is formatted as
# {
#   "Subnets": [
#   {"SubnetId": "subnet-012345abc6789", ...},
#   {"SubnetId": "subnet-abcdef123ghij", ...}
# ]}
if [ -z "$SUBNETS" ]; then
    # TODO - potentially add a VPC to filter too
    # The jq command grabs all returned subnet IDs and formats it into a JSON array
    SUBNETS=$(aws ec2 describe-subnets | jq -r --compact-output "[.Subnets[].SubnetId]")
fi

# Using the network config template, populate it with
# either the supplied security group and subnet values
# or the ones we fetched from AWS.
NETWORK_CONFIG=$(jq \
    --argjson SECURITY_GROUPS "$SECURITY_GROUPS" \
    --argjson SUBNETS "$SUBNETS" \
    '.awsvpcConfiguration.securityGroups=$SECURITY_GROUPS |
     .awsvpcConfiguration.subnets=$SUBNETS' \
    $DIR/network_config.json.tpl)

# Use the container override file as-is
OVERRIDES=$(jq . $DIR/container_overrides.json.tpl)

# Build the ECS run-task command
AWS_ARGS=("--region=us-east-1"
    ecs run-task
    "--cluster=$ENV_NAME"
    "--started-by=$AUTHOR"
    "--task-definition=$TASK_NAME"
    "--launch-type=FARGATE"
    "--platform-version=1.4.0"
    --network-configuration "$NETWORK_CONFIG"
    --overrides "$OVERRIDES"
    )

# Print out the arguments
printf " ... %s" "${AWS_ARGS[@]}"

# Run the ECS task
RUN_TASK=$(aws "${AWS_ARGS[@]}")
echo "Started task:"
echo "$RUN_TASK" | jq .

TASK_ARN=$(echo $RUN_TASK | jq '.tasks[0].taskArn' | sed -e 's/^"//' -e 's/"$//')

# Wait for the ECS task to complete
# Note this will auto-timeout after 600 seconds
# https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecs/wait/tasks-stopped.html
aws ecs wait tasks-stopped --region us-east-1 --cluster $ENV_NAME --tasks $TASK_ARN

# Get the exit code
TASK_STATUS=$(aws ecs describe-tasks --cluster $ENV_NAME --task $TASK_ARN | jq -r '.tasks[]')
EXIT_CODE=$(echo $TASK_STATUS | jq '.containers[].exitCode')

if [ "$EXIT_CODE" == "null" ]; then
  STOPPED_REASON=$(echo "$TASK_STATUS" | jq '.stoppedReason')
  echo "ECS task failed to start:" >&2
  echo "$STOPPED_REASON" >&2
  exit 1
fi

for CONTAINER_EXIT_CODE in $EXIT_CODE
do
  if [ "$CONTAINER_EXIT_CODE" -ne 0 ]; then
    echo "ECS task ran into an error (exit codes $EXIT_CODE). Please check cloudwatch logs." >&2
    exit 1
  fi
done

echo "ECS task completed successfully."
exit 0
