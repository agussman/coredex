# coredex

Core set of software classes and ontological relationships for representing common datatypes in a graph database

The purpose of this project is to provide a basic object model for representing data in a graph database. By including both an
ontologically valid model along with implenentation classes in software, it is hoped that these models will form a common framework
for tool and software development.

Following instructions here: https://docs.aws.amazon.com/neptune/latest/userguide/quickstart.html

# Setting up Neptune

Going through the steps in the tutorial.

 1) Go through the tutorial to launch a Neptune Cluster

 2) The default wizard doesn't create a Security Group that allows access to the DB server. Needed to create a new security group that allows access on port 8182 and applied it to the cluster. Note that the default option is to apply it during the next maintainence window, which could potentially be a few days off, or you can just jam it now (guess which I chose?).

 3) Setting up an EC2 Instance

Currently unable to connect to my Neptune DB... :/

$ curl nep-test001.cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com:8182
{"requestId":"0cb1d791-4016-6608-a167-8debd09a72be","code":"AccessDeniedException","detailedMessage":"Access Denied"}

$ curl 172.30.2.226:8182
{"requestId":"44b1d791-20b3-1ff9-43b7-60a48b16bf3e","code":"BadRequestException","detailedMessage":"Bad request."}

Possibly the issue was having IAM manage my RDS credentials?

# References

 * [Connecting to Neptune with the Gremlin Console](https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-console.html)
