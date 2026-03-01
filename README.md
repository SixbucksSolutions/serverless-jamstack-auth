# serverless-jamstack-auth

Receipe for a fully-serverless JAMstack frontend/REST API backend that does full user registration/authentication.

## API Backend

### Prepare API Backend

#### Project Domain Hosted By AWS Route 53

Hosting the domain at R53 makes later integration with other AWS services much easier.
You can host it elsewhere, but this writeup will be written assumin gthe project domain
is at R53, but this writeup will be written assumin gthe project domain
is at R53.

#### Create Kinde Application For API Backend

* Settings > Applications > Add Application
    * Name: "[your project] Backend"
    * Type: Machine to machine
    * Click Save
* Write down
    * Client ID
    * Client Secret

#### Create api CNAME

(OBE, Serverless Framework integration will handle)

#### Store Kinde Parameters For Lambda Function

* Go to the AWS console in the region where the REST API will be deployed
* Systems Manager Parameter Store
    * /[your project]/backend/kinde-client-id
    * /[your project]/backend/kinde-client-secret

#### Register your API

* Admin > Settings > APIs
* Name: {Your project] Backend
* Audience: https://api.[your domain]
* Click Save

#### Hook your API to your app


* Admin > Settings > Application > API's
* Your new API will show up
* Click triple dots
* Click "Authorize application"

#### Prepare the Management API for the Backend Application

* Applications > Backend App > APIs
* Enable mgmt API for the backend API
* ***add scopes***

#### Store Backend Parameters In Parameter Store

* add parameters

#### Give the getUser method permissions to read those parameter store keys

* Fafauth has that I think?
* Yeah https://github.com/TerryOtt/fafauth/blob/main/api/af-south-1/serverless.yml#L29

#### Get TLS cert for API Backend 

Think this is OBE, serverless will provision this for me since we have R53/ACM.
 
#### Modify serverless.yml

* Go to api/
* Update serverless.yml
    * provider.domain.name: api.[your domain]
    * provider.domain.certificateArn: [ARN of imported cert in ACM from last step]
    * provider.httpApi.authorizers.kinde.TokenAuthorizer.issuerUrl: https://[your-project].kinde.com 


### Deploy Backend

#### Install Serverless Framework 

#### Register/Login to Serverless 

Beyond scope.

#### Deploy

```bash
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

#### Add api CNAME

api.[your domain] CNAME to d-tarosfuk7b.execute-api.af-south-1.amazonaws.com

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

