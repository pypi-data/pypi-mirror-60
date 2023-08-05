![Version](https://img.shields.io/pypi/v/cognito-oauthtools) ![Build Status](https://img.shields.io/github/workflow/status/josephbmanley/cognito-oauthtools/build/master) ![Supported Versions](https://img.shields.io/pypi/pyversions/cognito-oauthtools)

# cognito-oauthtools

Simple AWS Cognito client to simplify project implementation.

## Getting Started

### Installation

cognito-oauthtools can easily be install using pip:

```bash
pip install cognito-oauthtools
```

## Objects

### Client

`cognito_oauthtools.Client`

#### Intializing

To intialize a `cognito_oauthtools.Client`, you must pass it:

- `endpoint`

  The dns name of the Cognito endpoint

- `client_id`

  The id of your Cognito authorizer clinet

- `client_secret`

  The secret for your Cognito client

- `host_domain`

  The domain name of the server that cognito will hit with oauth redirects

- `logout_path` = `"/"`

  Path on the host to return to after logging out

- `redirect_path` = `"/oauth"`

  Path on the host to return to after logging in

```python
oauth = cognito_oauthtools.Client('ENDPOINT.amazoncognito.com', 'CLIENT_ID', 'CLIENT_SECRET', 'myapp.example')
```

#### Properties

- `loginUrl`

  Cognito URL to authorize

- `registerUrl`

  Cognito URL to register a new user

- `logoutUrl`

  Cognito URL to logout

#### Methods

- `get_token(code)`

  Method that gets cognito token from the oauth return code

### User

`cognito_oauthtools.User`

#### Intializing

To intialize a `cognito_oauthtools.User`, you must pass it:

- `client`

  `cognito_oauthtools.Client` object for the user to use

- `token`

  The user's authorization token

```python
user = cognito_oauthtools.User(client, "xxxxTOKENxxxx")
```
