# serverless-jamstack-auth
Demonstration of a serverless JAMstack frontend/REST API backend with full user authentication
# jamstack-auth-quickstart-backend

Serverless REST API backend for the JAMstack Auth Quickstart project

## API Backend

### Prepare API Backend

#### Project Domain Hosted By AWS Route 53

Hosting the domain at R53 makes later integration with other AWS services much easier.
You can host it elsewhere, but this writeup will be written assumin gthe project domain
is at R53, but this writeup will be written assumin gthe project domain
is at R53.


#### Create Kinde Application

1. Log into kinde.com
1. Add Application
    * Enter a name
    * Type: "Front-end and mobile", then Save
    * In Quick start, select JavaScript then Save
    * Select Existing codebase tab (under Technology, next to "Starter kit")
    * Where is your project running: "https://[your domain]" and click Set
    * Click Set next to callback URL and logout URL (accept defaults)
    * Note your app-specific Kinde domain (e.g., `https://your-proj.kinde.com`)

#### Register your API

* Admin > Settings > APIs
* Name: Something memorable
* Audience: https://api.[your domain]
* Click Save

#### Hook your API to your app


* Admin > Settings > Application > API's
* Your new API will show up
* Click triple dots
* Click "Authorize application"

#### Create Kinde Application For API Backend

* Settings > Applications > Add Application
    * Name: jamstack-auth-quickstart-backend
    * Type: Machine to machine
    * Click Create
* Write down
    * Custom Domain
    * Client ID
    * Client Secret



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

#### Add auth CNAME

To to your DNS and add a CNAME from auth.[your-dmain] to your Kinde OIDC server.

#### Test CNAME

```
$ dig auth.jamstack-auth.publicntp.net

; <<>> DiG 9.18.39-0ubuntu0.24.04.2-Ubuntu <<>> auth.jamstack-auth.publicntp.net
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 43191
;; flags: qr rd ra; QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;auth.jamstack-auth.publicntp.net. IN   A

;; ANSWER SECTION:
auth.jamstack-auth.publicntp.net. 41 IN CNAME   sixbuckssolutionsllc.kinde.com.
sixbuckssolutionsllc.kinde.com. 41 IN   A       35.160.27.135
sixbuckssolutionsllc.kinde.com. 41 IN   A       52.40.72.86

;; Query time: 0 msec
;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
;; WHEN: Fri Feb 27 09:47:08 UTC 2026
;; MSG SIZE  rcvd: 137
```

So the CNAME is up.


