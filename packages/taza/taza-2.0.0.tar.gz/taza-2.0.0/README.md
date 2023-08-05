Taza
=====

Taza is a Python library with a set of abstractions over Tacyt that provides an OO layer over the query language.

### Instalation

Install via pip

    pip install taza
	
The libraries for tacyt are vendored inside taza, this is because the Tacyt python client is not distributed using pip.
	
### Usage

The library has currently two main components, the wrapper for the API and the query abstractions.

To use the API wrapper you must instantiate a `TazaClient` class.

```python
from taza.tacyt.TacytApp import TacytApp
from taza import TazaClient

app = TacytApp(APP_ID, SECREY_KEY)
client = TazaClient(app)
```

Clients can also be instantiated with a factory method that wraps the TacytApp class. Removing the need of importing Tacyt to the current script.

```python
from taza import TazaClient

client = TazaClient.from_credentials(APP_ID, SECRET_KEY)
```

#### Querying tacyt

You can send queries to tacyt for searching apps throught the `search_apps_with_query` method. This method will handle pagination automatically. It returns a generators, so no query is actually made until the data is collected.

For example, let's get the SHA256 hash of the apk of whatsapp.

```python
from taza import TazaClient

client = TazaClient.from_credentials(APP_ID, SECRET_KEY)

query = "packageName:com.whatsapp AND origin:GooglePlay"
fields = ["sha256"]

apps = client.search_apps_with_query(query, fields) # No actual connection to Tacyt done here.

for app in apps: # Now the generator starts yielding and therefore connecting to Tacyt.
	print(app)
```

#### Query language abstraction

The queries are send as a string to Tacyt, this means that the queries must be managed as strings, which sometimes can get messy. Taza has an OO abstraction that allows to write queries in Python.

First, each predicate can he specified with the `cond` class. There are shorthands for common predicates (at least common to me).

```python
from taza.query import cond, packageName, fromGooglePlay

q1 = cond('packageName', 'com.company.awesome_app')
q2 = packageName('com.company.awesome_app')

str(q1) # => "packageName:com.company.awesome_app"
str(q2) # => "packageName:com.company.awesome_app"
str(fromGooglePlay) => "origin:GooglePlay"

assert str(q1) == str(q2)
```

The predicates can be combined with AND, OR and NOT operators.

```python
from taza.query import cond, packageName, fromGooglePlay

q1 = cond('packageName', 'com.company.awesome_app')
q2 = packageName('com.company.awesome_app')

str(q1 & fromGooglePlay) # => "packageName:com.company.awesome_app AND origin:GooglePlay"
str(q2 | -fromGooglePlay) # => "packageName:com.company.awesome_app OR -origin:GooglePlay"
```

Bear in mind that Tacyt only allows up to 40 predicates per query.

If you need to agreggate several predicates under the same operator, you can use the `or_many` and `and_many` functions. They are usefull if you need to define the query programatically under a set of elements.

```python
from taza.query import cond, packageName, fromGooglePlay

q1 = packageName("app1")
q2 = packageName("app2")
q3 = packageName("app3")

assert or_many(q1, q2, q3) == (q1 | q2 | q3)

qs = [fromGooglePlay, cond('versionCode', '42'), packageName('my.another.app')]
assert and_many(*qs) == (fromGooglePlay & cond('versionCode', '42') & packageName('my.another.app'))
```

These queries are sent to the `search_apps_with_query` method in the same way that string based queries are sent. The whatsapp example could be rewritten as such.

```python
from taza import TazaClient
from taza.query import packageName, fromGooglePlay

client = TazaClient.from_credentials(APP_ID, SECRET_KEY)

query = packageName('com.whatsapp') & fromGooglePlay
fields = ["sha256"]

apps = client.search_apps_with_query(query, fields) # No actual connection to Tacyt done here.

for app in apps: # Now the generator starts yielding and therefore connecting to Tacyt.
	print(app)
```
