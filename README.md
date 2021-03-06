# coredex

Core set of software classes and ontological relationships for representing common datatypes in a graph database

The eventual purpose of this project is to provide a basic object model for representing data in a graph database. By including both an
ontologically valid model along with implenentation classes in software, it is hoped that these models will form a common framework
for tool and software development. Currently it covers getting started with AWS Neptune.

Here are [slides](https://docs.google.com/presentation/d/1p1C1NOKNhbwJ3cCUqECOSXqnz-3-wlLpIjt4Ftbcc80/edit?usp=sharing) and [only marginally-awkward video](https://youtu.be/-7ukAnT51CI?t=1900) from a Meetup talk I gave that provides an overview of Graph Databases and goes through the project.


# Setting up Neptune using the CloudFormation Stack wizard

Following instructions here: https://docs.aws.amazon.com/neptune/latest/userguide/quickstart.html

Before beginning, make sure you've created an existing EC2 ssh key (`.pem`).

 1) No changes on Select Template, hit Next
 2) On Specify Details under Parameters, change *DbInstanceType* to `db.r4.large`, *EC2ClientInstanceType* to `t2.micro`. Select your `.pem` for *EC2SSHKeyPairName*.
 3) Options, no change
 4) Review and Create
 5) Wait. This seems like it takes way longer than it should. Easy 10 minutes.

Once it completes, you'll have a `t2.micro` instance you can ssh into and from there you can access the Neptune instance gremlin endpoint on port 8182. It will also create a new VPC along with three subnets (one for each Availability Zone in us-east).

Something to be aware of is that the default Security Group settings allow port 8182 access to the bastion host. After everything is up and running, log into the bastion host / neptune client instance.

# Setting up Neptune manually (Not really recommended)

We're going to launch a Neptune Cluster and a small EC2 instance to connect to the cluster and host a lightweight web interface for exploring graph data.

 1) We start by going through the tutorial to [launch a Neptune Cluster](https://docs.aws.amazon.com/neptune/latest/userguide/get-started-CreateInstance-Console.html). The wizard will create a VPC and Subnets for you, if you don't already have them.

 2) The default wizard doesn't create a Security Group that allows access to the DB server. Needed to create a new security group that allows access on port 8182 and applied it to the cluster. Note that the default option is to apply it during the next maintenance window, which could potentially be a few days off, or you can just jam it now (guess which I chose?).

 3) Next I launched a `t2.micro` instance using an AWS Linux 2 AMI. Once it was running, I ssh'd in and installed Git and Apache (most of these steps are detailed [here](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.WebServerDB.CreateWebServer.html):

# Neptune REST API

After you log into your bastion host/neptune client, you may want to pull down the latest version of the scripts and sample data:
```
$ git clone https://github.com/agussman/coredex.git
```


Get the "Cluster endpoint" URL from the "Clusters" page. It will look something like `neptest2.cluster-cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com`. As that is a bit of a pain, let's assign it to an environmental variable:
```
$ NEPTUNE=neptest2.cluster-cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com
```

TODO: Use `aws neptune describe-db-clusters` to get the endpoint.

Use the `curl` command to try and retrieve a portion of the graph:
```
$ curl -X POST -d '{"gremlin":"g.V().limit(1)"}' http://$NEPTUNE:8182/gremlin
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
$ curl -X POST -d '{"gremlin":"g.V().limit(1)"}' http://$NEPTUNE:8182/gremlin | ppjson
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

# Inserting Data via the REST endpoint with curl

We can use the REST endpoint to insert data. For convienence we can put the Gremlin query in its own .json file and tell `curl` to read the data from there:
```
$ cat data/addVertex.json
{
  "gremlin": "g.addV('PERSON').property(id, '1').property('name', 'Alfred')"
}
$ curl -X POST -d @data/addVertex.json http://$NEPTUNE:8182/gremlin | ppjson
```

The above will create a single vertex (or node) which we can view by rerunning our earlier query.

It's possible to issue multiple gremlin commands in a single query. We can end the individual commands with `.next()` and separate them with a ' ' or a ';'.
```
$ cat data/addVertexAndEdge.json
{
  "gremlin": "g.addV('PERSON').property(id, '2').property('name', 'Betty').next() g.addE('MANAGES').from(g.V('2')).to(g.V('1')).property('dateStart', datetime('2018-06-01T00:00:00'))"
}
$ curl -X POST -d @data/addVertexAndEdge.json http://$NEPTUNE:8182/gremlin | ppjson
```

# Inserting and Querying Data via the Gremlin Console

If you launched the client instance via CloudFormation, Gremlin should be installed in your home directory and already configured with your cluster endpoint (yay for CloudFormation black magic!). Otherwise, installation instructions can be found here: [Getting Started with Neptune (Gremlin Console)](https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-console.html).

Launch the console with:
```
$ cd ~/apache-tinkerpop-gremlin-console-3.3.2/
$ bin/gremlin.sh
```

Connect to the Neptune DB instance:
```
gremlin> :remote connect tinkerpop.server conf/neptune-remote.yaml
```

Swith to remote mode:
```
gremlin> :remote console
```

Using the gremlin console, we can add another vertex and edge for someone using the same syntax as our JSON payload, with the slight wrinkle that they are not entirely a regular PERSON but are also an INTERN. This is useful if we want to represent nodes that are of multple classes/types:
```
gremlin> g.addV('PERSON::INTERN').property(id, '3').property('name', 'Carl')
==>v[3]
gremlin> g.addE('MANAGES').from(g.V('2')).to(g.V('3')).property('dateStart', datetime('2018-09-20T00:00:00'))
==>e[0cb2ff8d-324e-2699-d5d0-8186f7369d33][2-MANAGES->3]
```
We issued the above as two separate commands, but they could have been combined using the `.next() ` syntax used in the REST API call.

You can list the edges and vertices with:
```
gremlin> g.E()
==>e[f8b2fd35-ce79-ffd5-37ea-93cfffd06adb][2-MANAGES->1]
==>e[92b2fd4e-a834-5264-354c-c8b71af36310][2-MANAGES->3]
gremlin> g.V()
==>v[1]
==>v[3]
==>v[2]
```

To get actually useful information:
```
gremlin> g.V('3').labels()
==>PERSON::INTERN
gremlin> g.V('3').properties()
==>vp[name->Carl]
gremlin> g.V('3').valueMap(true).unfold()
==>id=3
==>label=PERSON::INTERN
==>name=[Carl]
```

Get all the `PERSON` vertices and their `name`s:
```
gremlin> g.V().hasLabel("PERSON").properties("name")
==>vp[name->Alfred]
==>vp[name->Carl]
==>vp[name->Betty]
```

To list all the `INTERN` nodes:
```
gremlin> g.V().hasLabel("INTERN").properties("name")
==>vp[name->Carl]
```

Run a traversal with values (valueMap())
```
gremlin> g.V().has('name', 'Betty').out('MANAGES').valueMap()
==>{name=[Alfred]}
==>{name=[Carl]}
```

To drop a vertex and it's associated edges (Sorry Carl, things didn't work out):
```
gremlin> g.V('3').drop()
```



Note that default cardinality on Verticies is different than on Edges. By default, Vertex properties have 'Set' cardinality, which (somewhat confusingly) means you can have multiples of the same property. For example:
```
g.V('1').property('favorite', 'apple')
g.V('1').property('favorite', 'pear')
g.V('1').property('favorite', 'banana')
```
will give you a vertex with three `favorite` properties:
```
gremlin> g.V('1').properties()
==>vp[name->Alfred]
==>vp[favorite->pear]
==>vp[favorite->banana]
==>vp[favorite->apple]
```

Whereas by default Edges will always update a property (aka 'single' cardinality):
```
g.V().outE().property('score', '42')
g.V().outE().property('score', '12')
g.V().outE().property('score', '88')
g.V().outE().properties()
==>p[dateStart->Fri Jun 01 00:00:...]
==>p[score->88]
```

In fact, edge properties always have 'single' cardinality; you can't make an edge property have 'set' cardinality (you have to create more edges).

However, you can make a Vertex property have 'single' cardinality by passing it `single` as a parameter:
```
g.V('1').property('favorite', 'mango')
g.V('1').property(single, 'favorite', 'kiwi')
g.V('1').properties()
==>vp[name->Alfred]
==>vp[favorite->kiwi]
```

# Visualizing AWS Neptune Graphs

We can view and explore our graph using [Graphexp](https://github.com/bricaud/graphexp).

If you didn't install Apache earlier, go back and install that or the web server of your choice.

## Installing Apache

You'll need a webserver for Graphexp. [Here](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.WebServerDB.CreateWebServer.html) is a pretty good overview of installing Apache but any webserver should do. In a nutshell:
```
$ sudo yum install -y httpd
$ sudo service httpd start
$ sudo chkconfig httpd on
$ sudo groupadd www
$ sudo usermod -a -G www ec2-user
```
log out, log back on
```
$ sudo chown -R root:www /var/www
$ sudo chmod 775 /var/www/html
$ sudo yum install git
```

## Graphexp

Clone the Graphexp checkout directly into the `/var/www/html` directory. Note that in a production environment you wouldn't want to do something like this, but I'm assuming you've locked down your security group so that only trusted parties have access to `:80` on your instance.

```
$ cd /var/www
$ git clone https://github.com/bricaud/graphexp.git html
```

In order to get Graphexp to work with AWS Neptune, edit `scripts/graphConf.js` and set `SINGLE_COMMANDS_AND_NO_VARS = true`. If you're working with non-trivial amounts of data, you'll also want to increase `REST_TIMEOUT` if you're working with non-trivial amounts of data.

We can now view Graphexp's web interface by connecting to our AMI instance. However, there's a slight wrinkle in that we still need to query the AWS Neptune backend for data and our _web browser_ will be sending those requests. This is an issue because only machines in the same VPC can connect to the Neptune cluster endpoint.

There are a couple of ways to address this. A simple hack is to forward `localhost:8182` to the Neptune cluster endpoint over our ssh connection to our AMI. To do that, we (re)launch an ssh session with the `-L` option to create an ssh tunnel:
```
$ ssh -vv -i ~/.ssh/your_aws.pem -L 8182:neptest2.cluster-cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com:8182 ec2-user@<publicip>
```

Now we can view Graphexp by connecting to our AWS Instance's public IP (provided you modified the Security Group to allow connecitons from your IP on port 80).

Change 'Protocol' to 'REST' (dropdown at the bottom) and click 'Get graph info'. If the box is checked, you'll see a summary of your graph.

In the search interface at the top, type 'PERSON' in the 'Node label' box and click 'Search'. You should see your nodes come back, and the relationships between them.

The GraphExp interface is little non-intuitive. If you find nodes mysteriously disappearing, try checking "Freeze exploration".


# Inserting GraphML

You can't. You have to convert it to CSV first.

# Converting GraphML to CSV and Insert

## Convert GraphML to CSV

Download the [GraphML 2 Neptune CSV](https://github.com/awslabs/amazon-neptune-tools/blob/master/graphml2csv/README.md) script part of [Amazon Neptune Tools](https://github.com/awslabs/amazon-neptune-tools):
```
$ clone https://github.com/awslabs/amazon-neptune-tools.git
```

Download some sample data. We're going to use air routes between airports (this is provided from the [Practical Gremlin](https://kelvinlawrence.net/book/Gremlin-Graph-Guide.html#air) online book, which is one of the better resources I've found):
```
$ wget https://raw.githubusercontent.com/krlawrence/graph/master/sample-data/air-routes-small.graphml
```

Convert it to CSV:
```
$ ./amazon-neptune-tools/graphml2csv/graphml2csv.py -i air-routes-small.graphml
infile = air-routes-small.graphml
Processing air-routes-small.graphml
Wrote 47 nodes and 602 attributes to air-routes-small-nodes.csv.
Wrote 1326 edges and 2652 attributes to air-routes-small-edges.csv.
```

## Loading a CSV into Neptune

This is fairly complicated and requires uploading properly formated CSV files (one for nodes and ones for edges) to S3, creating an S3 VPC endpoint, setting IAM privledges, and kicking off an async loading operation via the curl API. It's outside the current scope of this guide, but you can find instructions [here](https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load.html).

## Loading a CSV into Neptune with Python

Install `gremlinpython`:
```
$ pip install ‑‑user gremlinpython 
```

You can then load the CSV files with `csv2neptune.py`:
```
 ./csv2neptune.py -n $NEPTUNE:8182 -v ~/air-routes-small-nodes.csv -e ~/air-routes-small-edges.csv
```

The script is using the `gremlin-python` API to insert data into the Neptune endpoint:
```
    graph = Graph()

    g = graph.traversal().withRemote(DriverRemoteConnection(neptune_constr,'g'))
    # Load the nodes / vertices from csv
    with open(v_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            myid = id_transform(row["~id"])
            print(myid)
            v = g.addV(row["~label"]).property(T.id, myid)
            for key in row:
                if key.startswith('~'):
                    continue
                plabel, ptype = key.split(':')
                v.property(plabel, row[key])
            v.next()
```

One thing to note is that it include some useful classes to support creating properties of specific types, e.g., the `T.id` used above.


# WMATA Data Example

The script `wmata2csv.py` will download data from the Washington Metropolitan Area Transit Authority API and output CSV files that can be loaded into Neptune by `csv2neptune.py`.

In order to use the script, you'll need a WMATA API key, which you can painlessly sign up for here: [developer.wmata.com](https://developer.wmata.com/).

One you have your api key, you can run:
```
$ ./wmata2csv.py --api_key $APIKEY
```

This will output CSV files to the `data/` directory. You can then load these with:
```
$ ./csv2neptune.py -n $NEPTUNE:8182 -v data/station-nodes.csv -e data/station-edges.csv
```

# Teardown

*Note that this is unrecoverable! It will delete all the things!!!*

1) Go to the CloudFormation endpoint in the AWS Console

2) Select the parent stack (e.g., the one w/o "NESTED" in the Stack Name)

3) From the "Actions" dropdown select "Delete Stack"

4) This will _terminate_ your Neptune instance, _terminate_ the EC2 instance, VPC, and subnets.

# Troubleshooting

1) If `curl` doesn't produce a response at all, check that you created a Security Group that allows your EC2 instance to reach the Cluster endpoint

2) If you get `AccessDeniedException` messages as such:

```
$ curl nep-test001.cvinl5ewseag.us-east-1-beta.neptune.amazonaws.com:8182
{"requestId":"0cb1d791-4016-6608-a167-8debd09a72be","code":"AccessDeniedException","detailedMessage":"Access Denied"}
```
you probably set "IAM DB authentication" to "Enable IAM DB authentication" instead of "Disable". As near as I can tell, this cannot be modified after launch.

3) It's possible you might see this message if you hit the IP directly:
```
$ curl 172.30.2.226:8182
{"requestId":"44b1d791-20b3-1ff9-43b7-60a48b16bf3e","code":"BadRequestException","detailedMessage":"Bad request."}
```
I don't know what this means (yet).

4) The current version (0.8.0) of GraphExp has a bug where it won't pull back details on an individual vertex of `id` is an integer (it'll throw what looks like a CORS exception).That's why csv2neptune.py does the funky think w/ altering the ids.

5) If something works correctly in the gremlin terminal but you're getting a strange error when you attempt to recreate it with `gremlin-python`, you might be missing a `.next()`. The terminal automatically adds a terminating step.

# Closing Thoughts

 * A lot (all) of the Gremlin / TinkerPop documentation is aggressively obtuse and inaccessible. If you are a "learn from first principles" kinda person, good news! If you are a "learn from some basic examples and intuiting the functionality" well, you found this page at least. The [Neptune Gremlin Quickstart](https://docs.aws.amazon.com/neptune/latest/userguide/quickstart.html#quickstart-graph-gremlin) was helpful too.

 * [graphml is not natively loadable](https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format.html), you'll need to convert it to csv first using [GraphML2CSV](https://github.com/awslabs/amazon-neptune-tools/blob/master/graphml2csv/README.md).

# References

 * [Launching a Neptune DB Cluster](https://docs.aws.amazon.com/neptune/latest/userguide/get-started-CreateInstance-Console.html)
 * [EC2 Web Server](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.WebServerDB.CreateWebServer.html)
 * [Connecting to Neptune with the Gremlin Console](https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-console.html)
 * [Neptune Gremlin Quickstart](https://docs.aws.amazon.com/neptune/latest/userguide/quickstart.html#quickstart-graph-gremlin)
 * [Neptune Gremlin Implementation Differences, plus info on Cardinality ](https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html)
 * [Installing Apache Web Server on AWS Linux 2](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.WebServerDB.CreateWebServer.html)
 * [Gremlin Graph Guide](https://kelvinlawrence.net/book/Gremlin-Graph-Guide.html) is fairly accessible and in-depth and the source of the FlightPaths data
