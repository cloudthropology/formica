---
title: Template File Reference
weight: 200
---

All templates in formica are defined in CloudFormation template files. The files have to follow the naming convention
of `*.template.(json|yaml|yml)`. This means we support your template files in either json or yaml/yml. Any existing
CloudFormation template is valid in Formica, so you can easily import an existing stack.

When formica is started it will load all `*.template.(json|yaml|yml)` files from the current directory and merge
them into one CloudFormation stack. You can mix `json` or `yaml` file in the same directory.
This makes your CloudFormation stack more modular and helps you to keep an overview.
[`formica template`]({{< relref "/tools/formica/commands/template.md" >}}) can be used to print that template to the console.

To be able to change files dynamically we use [Jinja2](http://jinja.pocoo.org/docs/2.9/templates/), a widely used templating
engine. It allows you to iterate over values, define variables or use filters to change text, e.g. when a value has to
be alphanumeric and you want to strip special characters.

## Enhancing Templates

When using Formica, there are three places that variables can be set. The first is to use inline `{% set foo = "bar" %}`
Jinja2 syntax. More commonly, you'll want to vary the values based on which stack you're deploying. All commands that
take parameters and stack changes (`diff`, `new`, `change`, etc) accept a `--vars foo=bar baz=box` syntax. More
complex or nested values can be specified in a stack config file:

```
stack: my-cool-resources
vars:
  foo: bar
  complex_thing:
    a:
      - 1
      - 2
      - 3
    b: something
  max_size: 10
```

Any `--vars` CLI options will override the stack config, similar to parameters. You can then loop or base
conditionals on these custom values.

```
{% for i in complex_thing.a %}myrsrc{{ i }}{% endfor %}

{% if max_size > 3 %}
  {{ max_size }}
{% else %}
  3
{% endif %}
```

## Available AWS Resources

As Formica uses the official CloudFormation syntax directly all CloudFormation resources or options are supported.

In the following example we're creating an S3 bucket that can be used for hosting static pages.

```yaml
Resources:
  WebBucket:
    Type: "AWS::S3::Bucket"
    Properties:
      BucketName: flomotlik.me
      AccessControl: PublicRead
      WebsiteConfiguration:
        IndexDocument: index.html
```

## Additional template functions

The following functions can be used in your templates:

### resource

This function will remove any non-alphanumeric characters and convert the first character to uppercase. This is
especially helpful when you want to set logicalIds in your template from a variable:

```yaml
{% set domain = 'flomotlik.me' %}
Resources:
  {{ domain | resource }}:
    Type: "AWS::S3::Bucket"
    Properties:
      BucketName: {{ domain }}
      AccessControl: PublicRead
      WebsiteConfiguration:
        IndexDocument: index.html
```

will result in

```json
{
    "Resources": {
        "FlomotlikMe": {
            "Properties": {
                "AccessControl": "PublicRead",
                "BucketName": "flomotlik.me",
                "WebsiteConfiguration": {
                    "IndexDocument": "index.html"
                }
            },
            "Type": "AWS::S3::Bucket"
        }
    }
}
```

### mandatory

Set a variable to mandatory so if its not set the template building will fail. This is especially important
when writing a module that expects variables:

```yaml
Resources:
  {{ domain | mandatory | resource }}:
    Type: "AWS::S3::Bucket"
```

```
root@62d81801cc09:/app/examples/s3-bucket# formica template
FormicaArgumentException: Mandatory variable not set.
For Template: "./example.template.yml"
If you use it as a template make sure you're setting all necessary vars
```

### code

Import code from a file and escape newlines and apostrophes. It will load the file from the same folder that
your template is in. You can even use the templating syntax inside of that included file, including the code command
described here.

In the following example we create a LambdaFunction and want to inline the code. This is great for simple functions
as you're able to test your code as a standard python file, but can include it directly into the CloudFormation template.

If you use yaml make sure to add apostrophes around the `{{ code('something.file) }}` call, otherwise escaped newlines
might be escaped or treated differently by the yaml parser. You can see the right way to do this in the following example:

```yaml
Resources:
  LambdaTestFunction:
    Type: "AWS::Lambda::Function"
    Properties:
      Handler: "index.handler"
      Role:
        Fn::GetAtt:
          - "LambdaExecutionRole"
          - "Arn"
      Code:
        Zipfile: "{{ code('code.py') }}"
      Runtime: "python3.7"
```

Sometimes including it directly leads to issues with characters yaml wants to interpret, so another way to include code is through the pipe string handling in yaml:

```yaml
Resources:
  LambdaTestFunction:
    Type: "AWS::Lambda::Function"
    Properties:
      Handler: "index.handler"
      Role:
        Fn::GetAtt:
          - "LambdaExecutionRole"
          - "Arn"
      Code:
        Zipfile: |
          {{ code('code.py') | indent (10)}}
      Runtime: "python3.7"
```

Indention is important here as otherwise whitespace will be added to the file making the string handling problematic.

By default 'code' escapes newlines and apostrophes by using the `code_escape` function defined below. Use the `file` function if you don't want to escape the content.

```python
def handler(event, context):
    print(event)
    return event
```

Running `formica template` in the same directory will result in the following CloudFormation template:

```json
{
    "Resources": {
        "LambdaTestFunction": {
            "Properties": {
                "Code": {
                    "Zipfile": "def handler(event, context):\n    print(event)\n    return event\n"
                },
                "Handler": "index.handler",
                "Role": {
                    "Fn::GetAtt": [
                        "LambdaExecutionRole",
                        "Arn"
                    ]
                },
                "Runtime": "python3.7"
            },
            "Type": "AWS::Lambda::Function"
        }
    }
}
```

If you want to set specific Jinja variables just for loading this particular file you can add them to the code function as arguments `"{{ code('code.py', VAR='something') }}"`.

### code_escape

In case you want to pass code around in variables it can be helpful to use code_escape to make sure newlines
and apostrophes are properly escaped so you can inline any kind of files:


```yaml
Resources:
  LambdaTestFunction:
    Type: "AWS::Lambda::Function"
    Properties:
      Handler: "index.handler"
      Role:
        Fn::GetAtt:
          - "LambdaExecutionRole"
          - "Arn"
      Code:
        Zipfile: {{ code('code.py') | code_escape }}
      Runtime: "python3.7"
```

### code_array

Sometimes you might want to take the contents of a file as input for an array (line-by-line). Combine `code()` with `code_array` to make that happen:

```yaml
Resources:
  ...
  ListOfItems: {{ code('my-list') | code_array }}
```



### file

If you just want to load the contents of a file without escaping them you can do that by using the file function, e.g. `Zipfile: {{ file('code.py') | code_escape }}`.

### files

Sometimes you want to iterate over a list of files and use that list to create Resources in your Template. For example when deploying Service Control Policies its easier if we can simply create the corresponding files in a subdirectory and then load all files.

The `files` function helps there as it gives you a list of all template files it finds with the ability to filter them.
Filtering uses the standard unix like wildcard mechanism (implemented by pythons fnmatch library), so you can do `subfolder/*` or `sub*/*.json`.

```yaml
Resources:
  {{for SCP in files('scps/*')}}
  {{SCP | resource}}:
    ...
  {{endfor }}
```

### novalue

Sometimes you only want to add a property to a resource in case a variable is set, for example from a parent
module. One way to implement this would be to surround that parameter with an if statement, but that
makes the templates a bit bloated.

Another way is to use the `novalue` filter to use the `AWS::NoValue` pseudoparameter CloudFormation provides
in case a variable is empty. For example in case we want to create a Lambda function in a module and set its
name only if the `Name` variable is set, otherwise return `AWS::NoValue` we would do the following:

```
Name: {{ Name | novalue }}
```

### now and utcnow

Sometimes you need to set dates in your template. For this we've included [Arrow](https://arrow.readthedocs.io/en/latest/)
and made it available through the `now` and `utcnow` functions.

For example if we create an API Key for an AppSync Api we need to set an expiration on the Key. To make it easy to
set forward moving keys we can set it to 1week after deployment:

```
Expires: {{now().shift(weeks=1).timestamp}}
```

Which will result in

```
"Expires": 1535117482
```

Another use case is when you want to add a random string to your template, for example an API Gateway deployment
won't redeploy unless you rename it on every deploy. To do this you can do the following:

```
ApiGatewayDeployment{{now().timestamp}}:
  Type: ....
  Properties: ...
```

So every time you redeploy the stack the old deployment will be removed and replaced with a new one. Check out the
[Arrow documentation(https://arrow.readthedocs.io/en/latest/) for all details.
