# serverless-jamstack-auth

Receipe for a fully-serverless JAMstack frontend/REST API backend that does full user registration/authentication.

## API Backend

### Prepare API Backend

#### Project Domain Hosted By AWS Route 53

Hosting the domain at R53 makes later integration with other AWS services much easier.
You can host it elsewhere, but this writeup will be written assumin gthe project domain
is at R53, but this writeup will be written assuming the project domain is at R53.

#### Create Kinde Application For API Backend

* Settings > Applications > Add Application
    * Name: **"[your project] Backend"**
    * Type: **Machine to machine**
    * Click Save
* Write down
    * Domain
    * Client ID
    * Client Secret


#### Prepare the Management API for the Backend Application

##### Authorize Backend To Interact With Kinde Management API

* In Kinde, navigate to Applications > Backend App > APIs
* Click triple dots next to Kinde Management API
* Click "Authorize application"
* The "Is authorized" check will appear for the Kinde Management API

#### Authorize Backend API For Neessary Management API Operations

* Click triple dots next to the Kinde Management API
* Click "Manage scopes"
    iam:
      role:
        statements:
          # Permission to get exactly two specific parameters for our function to avoid needing to push code due to an IdP change
          - Effect: 'Allow'
            Action:
              - 'ssm:GetParameter'
              - 'ssm:GetParameters'
            Resource:
              - 'arn:aws:ssm:${aws:region}:${aws:accountId}:parameter/fafauth/apigw_custom_authorizer/client_token_signing_keys_jwks'
              - 'arn:aws:ssm:${aws:region}:${aws:accountId}:parameter/fafauth/apigw_custom_authorizer/token_claims_validation_values'
* Click the enable toggle for the `read:users` scope
* Click Save
* Note that the Scopes column for the Kinde Mangagement API now reads "1"

#### Store Kinde Parameters For Lambda Function

* Go to the AWS console in the region where the REST API will be deployed
* Systems Manager > Parameter Store 
    * Kinde Client ID
        * Path: **`/[your project]/backend/auth/client-id`**
        * Type: **String**
    * Kinde Client Secret
        * Path: **`/[your project]/backend/auth/client-secret`**
        * Type: **String**

Use the appropriate two values from Kinde that you wrote down earlier.

#### Update serverless.yml

* Go to api/
* Update serverless.yml
    * `provider.domain.name`: **`api.[your domain]`**
    * `provider.httpApi.authorizers.kindeTokenAuthorizer.issuerUrl`: **"Domain" field from Kinde Backend app**
    * `provider.httpApi.authorizers.kindeTokenAuthorizer.audience`: **`https://api.[your domain]`**
    * `functions.userGet.iam.role.statements.Resource`: ***(update to `...:/parameter/[your project]/backend/auth/...`***

### Deploy Backend

#### Install Serverless Framework 

Beyond scope.

#### Register/Login to Serverless 

Beyond scope.

#### Deploy

```
serverless deploy
```

Output will be similar to:

```
endpoints:
  GET - https://8od6x91bvf.execute-api.af-south-1.amazonaws.com/api/v001/ping
  GET - https://8od6x91bvf.execute-api.af-south-1.amazonaws.com/api/v001/user
functions:
  ping: jamstack-auth-quickstart-dev-ping (1.1 kB)
  userGet: jamstack-auth-quickstart-dev-userGet (1.1 kB)
domain:
  name: api.jamstack-auth.publicntp.net
  target: d-tarosfuk7b.execute-api.af-south-1.amazonaws.com
  zone id: Z2DHW2332DAMTN
```

#### Prepare the Management API for the Backend Application

* Applications > Backend App > APIs
* Enable mgmt API for the backend API
* ***add scopes***


#### What got deployed

### Test Backend

#### Ping Endpoint

```
time curl -i -H "Origin: https://jamstack-auth.publicntp.net" https://api.jamstack-auth.publicntp.net/api/v001/ping
```

Result:
```
date: Tue, 24 Feb 2026 12:43:31 GMT
content-type: application/json
content-length: 26
access-control-allow-origin: https://jamstack-auth.publicntp.net
apigw-requestid: ZSV2Bh7CCfMEPSw=

{
    "message": "Pong!"
}
real    0m0.788s
user    0m0.019s
sys     0m0.003s
```

Note: we passed the Origin request header and the API replied saying it was an allowed origin, 
so this is a CORS-friendly API

Run this a few times to see the cold start penalty drop.

#### Get User Endpoint

```
$ time curl -i -H "Origin: https://jamstack-auth.publicntp.net" https://8od6x91bvf.execute-api.af-south-1.amazonaws.com/api/v001/user
```

Result:
```
HTTP/2 401
date: Fri, 27 Feb 2026 09:28:22 GMT
content-type: application/json
content-length: 26
www-authenticate: Bearer
apigw-requestid: ZbyEkhg1ifMEJLA=

{"message":"Unauthorized"}
```

Got a 401 "Not Authorized" response because we didn't pass authentication.

Note the `www-authenticate: Bearer` header that APIGW attaches. It tells the client
what credentials this endpoint expects (in our case, an OAuth bearer token).

## Frontend

### Prep Frontend

#### Create Frontend Kinde Application

1. Log into kinde.com
1. Click Settings > Applications
1. Click Add Application
    * Enter a name
    * Type: "Front-end and mobile", then Save
    * In Quick start, select JavaScript then Save
    * Select Existing codebase tab (under Technology, next to "Starter kit")
    * Where is your project running: "https://[your domain]" and click Set
    * Click Set next to callback URL and logout URL (accept defaults)
    * Note your app-specific Kinde domain (e.g., `https://your-proj.kinde.com`)

#### Register your API in Kinde

* Admin > Settings > APIs
* Name: {Your project] Backend
* Audience: https://api.[your domain]
* Click Save

#### Hook your API to your app in Kinde


* Admin > Settings > Application > API's
* Your new API will show up
* Click triple dots
* Click "Authorize application"

