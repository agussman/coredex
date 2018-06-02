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

 4) Test connecting to the Graph

Get the "Cluster endpoint" URL from the "Clusters" page. It will look something like `neptest2.cluster-cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com`.

Use the `curl` command to try and retrieve a portion of the graph:
```
$ curl -X POST -d '{"gremlin":"g.V().limit(1)"}' http://neptest2.cluster-cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com:8182/gremlin
```
The response should look something like this (because there's no data in the graph yet):
```
{"requestId":"acb1d7c6-4029-f995-2ee7-ea3d0fdea301","status":{"message":"","code":200,"attributes":{"@type":"g:Map","@value":[]}},"result":{"data":{"@type":"g:List","@value":[]},"meta":{"@type":"g:Map","@value":[]}}}
```

To make it look nice, we can add the following to our `~/.bashrc`:
```
alias ppjson='python -mjson.tool'
```
and then re-read it by running:
```
$ source ~/.bashrc
```

We can then pipe the output to `ppjson` to get more-readable output:
```
$ curl -X POST -d '{"gremlin":"g.V().limit(1)"}' http://neptest2.cluster-cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com:8182/gremlin | ppjson
{
    "requestId": "50b1dca5-418c-f683-54e5-2c17d078cbc8",
    "result": {
        "data": {
            "@type": "g:List",
            "@value": []
        },
        "meta": {
            "@type": "g:Map",
            "@value": []
        }
    },
    "status": {
        "attributes": {
            "@type": "g:Map",
            "@value": []
        },
        "code": 200,
        "message": ""
    }
}
```

# Inserting some Data

We can use the REST endpoint to insert data. For convienence we can put the Gremlin query in its own .json file and tell `curl` to read the data from there:
```
$ cat addVertex.json
{
  "gremlin": "g.addV('PERSON').property(id, '1').property('name', 'Alfred')"
}
$ curl -X POST -d @addVerticies.json http://neptest2.cluster-cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com:8182/gremlin | ppjson
```


# Troubleshooting

If `curl` doesn't produce a response at all, check that you created a Security Group that allows your EC2 instance to reach the Cluster endpoint

If you get `AccessDeniedException` messages as such:

```
$ curl nep-test001.cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com:8182
{"requestId":"0cb1d791-4016-6608-a167-8debd09a72be","code":"AccessDeniedException","detailedMessage":"Access Denied"}
```
you probably set "IAM DB authentication" to "Enable IAM DB authentication" instead of "Disable". As near as I can tell, this cannot be modified after launch.

It's possible you might see this message if you hit the IP directly:
```
$ curl 172.30.2.226:8182
{"requestId":"44b1d791-20b3-1ff9-43b7-60a48b16bf3e","code":"BadRequestException","detailedMessage":"Bad request."}
```
I don't know what this means (yet).





# References

 * [Connecting to Neptune with the Gremlin Console](https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-console.html)
