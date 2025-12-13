### On OAUTH2

The flow for the current application is a password flow, whereby the `username` and `password` are submitted in exchange for a bearer token which is appended to request headers as Json Web Token

There are other flow types:

* Authorization code grant with PKCE
    most secure and recommended flow for web and mobile apps, involving user login, getting an authorization code and exchanging it for tokens

* Client Credentials Grant
    machine to machine communnication where application acts on behalf of user, using client ID/Secret to get an access token

* Resource Owner Password Credentials Grant
    legacy; users provide credentials directly

* Implicit Grant
    for older SPA apps where tokens returned directly in URL

* Device Authorization Flow
    for smart TVs where users authenticate on separate device

* Refresh Token Grant
    obtain new access tokens when old ones expire, without requiring the user to login in again

key roles in OAuth flow
* Resource Owner - user who owns the data
* Client - application requesting access
* Authorization server - authenticates user and issues tokens
* Resource Server - hosts the protected data

* To create scopes in token returned from cognito user pools, we need to create a Resource Server under domains?

    https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-define-resource-servers.html

* Note on testing login and logout in Swagger UI. The Swagger UI created the authorize form for logging in. It can also log you out by clicking on Logout link.
    The same login and logout API routes don't work as they don't set the Bearer token header; the swagger UI provides this....

    which means even if we call logout via the API, we still have the previous token which is still valid...

    need to cache the token with the user 



### REFS:

* https://docs.aws.amazon.com/cognito/latest/developerguide/token-revocation.html

* https://docs.aws.amazon.com/cognito/latest/developerguide/token-revocation.html

* https://stackoverflow.com/questions/76867554/fastapi-how-to-access-bearer-token

* https://medium.com/@prithvi.atal/securing-fastapi-applications-with-aws-cognito-a-step-by-step-guide-to-jwt-authentication-0a34002f60f5

* https://timothy.hashnode.dev/building-an-authentication-api-with-aws-cognito-and-fastapi#heading-b-creating-a-user-pool

* https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/python/example_code/cognito#code-examples

* https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools.html

* https://github.com/Timothy-py/FastCognito/tree/main

* https://gofastmcp.com/integrations/aws-cognito#step-2%3A-fastmcp-configuration

* https://stackoverflow.com/questions/57538122/how-can-i-get-a-jwt-access-token-from-aws-cognito-as-admin-in-python-with-boto3

* https://cameledge.com/post/web-development/secure-api-oauth2-jwt-aws-cognito-part-1

* https://cameledge.com/post/web-development/secure-api-oauth2-jwt-aws-cognito-part-2