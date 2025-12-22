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


### On using Custom scopes via Cognito

* Need to create a Resource Server for the user pool first in order to define custom scopes:

    https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-define-resource-servers.html#cognito-user-pools-define-resource-servers-about-resource-servers


* Can't access custom scopes using the boto3 cognito-idp client; need to create a custom domain and then point it to the Token Endpoint:
    ```
    The token endpoint becomes publicly available when you add a domain to your user pool.
    ```

    https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html


    https://github.com/aws/aws-sdk/issues/178

    https://github.com/aws/aws-sdk/issues/178#issuecomment-2389662983

* To fix the issue of not being able to use custom domain, can use Lambda Triggers:

    https://aws.amazon.com/blogs/security/how-to-customize-access-tokens-in-amazon-cognito-user-pools/

    https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html


    example using Node.js:

    https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html#aws-lambda-triggers-pre-token-generation-example-version-2-overview


* Example of PreToken Lambda trigger for Agent

  https://aws.amazon.com/blogs/security/empower-ai-agents-with-user-context-using-amazon-cognito/



### REFS:

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



https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/cognito/cognito_idp_actions.py