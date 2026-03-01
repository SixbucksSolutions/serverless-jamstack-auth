# serverless-jamstack-auth

Receipe for a fully-serverless JAMstack frontend/REST API backend that does full user registration/authentication.

## API Backend

### Prepare API Backend

#### Project DNS Domain Hosted By AWS Route 53

Hosting the domain at R53 makes later integration with other AWS services much easier.

You can host your DNS elsewhere, but this writeup will be written assuming the project domain
is hosted with R53 because it dramatically simplifies TLS certificiates and DNS setup.

#### Create Kinde Application For API Backend

* Settings > Applications > Add Application
    * Name: **"[your project] Backend"**
    * Type: **Machine to machine**
    * Click **Save**
* Write down
    * Domain
    * Client ID
    * Client Secret


#### Prepare the Management API for the Backend Application

##### Authorize Backend To Interact With Kinde Management API

* In Kinde, **navigate to Applications > Backend App > APIs**
* Click the **triple dots** on the "Kinde Management API" line
* Click "**Authorize application**"
* The "**Is authorized**" check will appear for the Kinde Management API

#### Authorize Backend API For Neessary Management API Operations

* Click triple dots next to the Kinde Management API
* Click "**Manage scopes**"
* Click the enable toggle for the **`read:users`** scope
* Click **Save**
* Note that the Scopes column for the Kinde Mangagement API now reads "1"

#### Store Kinde Parameters For Lambda Function

* Go to the AWS console in the region where the REST API will be deployed
* Systems Manager > Parameter Store 
    * Kinde Domain
        * Path: **`/serverless-jamstack-auth/backend/auth/domain`**
        * Type: **String**
    * Kinde Client ID
        * Path: **`/serverless-jamstack-auth/backend/auth/client-id`**
        * Type: **String**
    * Kinde Client Secret
        * Path: **`/serverless-jamstack-auth/backend/auth/client-secret`**
        * Type: **String**

Use the appropriate values from Kinde that you wrote down earlier.

#### Update Allowed Origin Host

* Update `backend/handler.py`
    * Set `allowed_origin_url` at the top of the file to **`https://[your domain]`**

#### Update serverless.yml

* Update `backend/serverless.yml` in this repository
    * `provider.region`: ***(the AWS region code you are deploying your API backend to, e.g. `af-south-1`)***
    * `provider.domain.name`: **`api.[your domain]`**
    * `provider.httpApi.authorizers.kindeTokenAuthorizer.issuerUrl`: **"Domain" field from Kinde Backend app**
    * `provider.httpApi.authorizers.kindeTokenAuthorizer.audience`: **`https://api.[your domain]`**

### Test Backend Interface To Kinde Management API

Need to confirm our backend will be able to perform the needed actions with the Kinde Management API.

* In Kinde, Backend Application > APIs, click **Kinde Management API**
* Click **Test** in the left menu
* Select your backend app and click **Get Token**
* Copy the **Access Token**

```
curl --silent -H "Accept: application/json" -H "Authorization: Bearer [access token from Kinde]" https://[your-project].kinde.com/api/v1/users | jq
``` 

Result:
```
{
  "code": "OK",
  "users": null,
  "message": "Success",
  "next_token": null
}
```

### Deploy Backend

#### Install Serverless Framework 

Beyond scope.

#### Register/Login to Serverless 

Beyond scope.

#### Install Docker

Beyond scope.

#### Give current user the ability to execute Docker commands without sudo

Beyond scope

#### Give the current user the ability to create all needed resources in AWS

Beyond scope.

#### Deploy

```
cd .../serverless-jamstack-auth/backend
serverless deploy
```

Output will be similar to:

```
✔ Service deployed to stack serverless-jamstack-auth-backend-dev (99s)

endpoints:
  GET - https://[...].execute-api.[your API region].amazonaws.com/api/v001/ping
  GET - https://[...].execute-api.[your API region].amazonaws.com/api/v001/user
functions:
  ping: serverless-jamstack-auth-backend-dev-ping (15 MB)
  userGet: serverless-jamstack-auth-backend-dev-userGet (15 MB)
domain:
  name: api.[your domain]
  target: [...].execute-api.[your API region].amazonaws.com
  zone id: [...]
```

#### What Got Deployed

[insert diagram here]

### Test Backend

#### Test "Ping" Endpoint

```
time curl -i -H "Origin: https://[your domain]" -H "Accept: application/json" https://api.[your domain]/api/v001/ping
```

Result:
```
HTTP/2 200
date: Tue, 24 Feb 2026 12:43:31 GMT
content-type: application/json
content-length: 26
access-control-allow-origin: [your domain]
apigw-requestid: ZSV2Bh7CCfMEPSw=

{
    "message": "Pong!"
}
real    0m4.103s
user    0m0.017s
sys     0m0.004s
```

Note: we passed the Origin request header. The API replied with a header saying the offered origin is an allowed origin, 
making this API CORS-friendly.

#### Lambda Cold Start Penalty

That four second response time from the API *hurts*.

Re-run the `curl` command 1-2 more times to see how the response times are once the Lambda is warm.

```
HTTP/2 200
date: Sun, 01 Mar 2026 13:49:09 GMT
content-type: application/json
content-length: 26
access-control-allow-origin: https://serverless-jamstack-auth.click
apigw-requestid: Zi-Jei8myK4EJgQ=

{
    "message": "Pong!"
}
real    0m0.188s
user    0m0.016s
sys     0m0.002s
```

Going from 4,100 milliseconds to under 200 milliseconds is a dramatic improvement.

#### Test An Endpoint For Logged-In Users

```
$ time curl -i -H "Origin: https://[your domain]" -H "Accept: application/json" https://api.[your domain]/api/v001/user
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

Got a 401 "Not Authorized" response from AWS API Gateway because we aren't logged in to the app.

Note the `www-authenticate: Bearer` header that APIGW attaches. It tells the client
what credentials this endpoint expects (in our case, an OAuth bearer token).

## Frontend

### Prep Frontend

#### Create Frontend Kinde Application

1. Log into kinde.com
1. Click Settings > Applications
1. Click Add Application
    * Name: "**[your project] Frontend**"
    * Type: Select "**Front-end and mobile**"
    * Click "**Save**"
1. Click "**Details**" on left menu
1. Write down
    * **Domain**
    * **Client ID**
1. In **Callback URLs"
    * Set **Application homepage URI** to "`https://[your domain]`"
    * Set **Allowed callback URLs** to "`https://[your domain]`"
    * Set **Allowed logout redirect URLs** to "`https://[your domain]`"
1. In **Authentication experience**
    * Disable "**Ask for user first name and last name**"
1. Click **Save**

#### Set Kinde Frontend App Authentication Methods

1. Click **Authentication** on left menu
1. For this app
    * Disable: **Email + code**
    * Enable: **Email + password** (and any social connections selected when creating Kinde project)
1. Click **Save**

#### Register your REST API Backend in Kinde

* Go to top level **Home > Settings > APIs**
* Click "**Add API**"
* Name: **[Your project] Backend**
* Audience: **https://api.[your domain]**
* Click **Save**

#### Authorize Kinde Frontend App To Get Tokens For REST API Backend

* While in your API, click "**Applications**"
* Click triple dots next to "**[your project] Frontend**"
* Click "**Authorize application**"
* A check mark will show up on "**Is authorized**" for "[your project] Frontend"

#### Update Frontend Config

1. `cd .../serverless-jamstacl-auth/frontend`
1. Edit the `.env` file.
    * `VITE_KINDE_CLIENT_ID`: ***(Value written down when creating frontend application)*** 
        * NOTE: totally public value, not sensitive at all -- post it on a billboard!
    * `VITE_KINDE_DOMAIN`: ***`[your-project].kinde.com`***
    * `VITE_KINDE_REDIRECT_URL` : ***`https://[your domain]`***
    * `VITE_KINDE_LOGOUT_URL` : ***`https://[your domain]`***
    * `VITE_KINDE_TOKEN_AUDIENCE`: ***`https://api.[your domain]`***

#### Don't forget to update backend

1. Read client_id/client_secret from Parameter Store


#### Login to Cloudflare

Beyond scope.

#### Create Cloudflare Pages Project

asdfsf

#### Pop A Cold One
