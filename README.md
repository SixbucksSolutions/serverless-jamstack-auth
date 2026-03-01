# serverless-jamstack-auth

Receipe for an aentirely serverless JAMstack frontend/REST API backend deployment that offers 
full self-service user registration/authentication.

## Inspiration

After hearing about [Kinde's user authentication](https://www.kinde.com/authentication/) being 
supremely excellent for devs to integrate with, I gave it a whirl.

I came away from the experience so thoroughly impressed that was motivated to create a living
reminder to myself that a fully-authenticated JAMstack system that is nothing but JS running in 
your browser talking to a serverless REST API isn't as overwhelming/intimidating as it used to be.

This GitHuib repo is kind of a "starter" for me on my own projects, to remind myself that in 75 
minutes I can be sending authenticated requests that APIGW validates and sends to a Lambda 
function.

Help getting stuff built is a positive, and I know others who could benefit. So here ya go! :)

## Assumptions

### Project DNS Domain Hosted By AWS Route 53

Hosting the domain at R53 makes integration with other AWS services much easier.

You can host your DNS elsewhere and make it work, but this writeup will be written assuming 
the project domain is hosted with R53 because it **dramatically** simplifies several aspects of
an already-complicated recipe (namely: the integrations to create and deploy both TLS certificates 
as well as DNS records for the API Gateway).

## Recent-ish Ubuntu-ish bash Shell To Run Commands

I used an Ubuntu 24.04 LTS EC2 instance to run the CLI stuff in this recipe.

There's nothing stopping you from using Mac or Windows or Slackware circa 1994.

If you use something other than a fairly recent Debian/Ubuntu flavor, your steps may differ 
from mine.

## API Backend

### Prepare API Backend

#### Create Kinde Application For API Backend

* **Settings > Applications > Add Application**
    * Name: **"[your project] Backend"**
    * Type: **Machine to machine**
    * Click **Save**
* Write down
    * **Domain**
    * **Client ID**
    * **Client Secret**


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
    * Set `allowed_origin_url` at the top of the file to **`https://www.[your domain]`**

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

#### Install latest LTS Version Of NodeJS

I like using nvm as described [here](https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04#option-3-installing-node-using-the-node-version-manager).

#### Install Serverless Framework 

```
npm install -g serverless
```

#### Register/Login to Serverless 

```
serverless login
```

#### Install Docker

I like the instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)

#### Give current user the ability to execute Docker commands without sudo

```
sudo usermod -aG docker ${USER}
```

Log out and back in.

#### Give the current user the ability to create all needed resources in AWS


I'm lazy and give full AdministratorAccess to the EC2 I'm on.

If you want to be better, go for it.

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
time curl -i -H "Origin: https://www.[your domain]" -H "Accept: application/json" https://api.[your domain]/api/v001/ping
```

Result:
```
HTTP/2 200
date: Tue, 24 Feb 2026 12:43:31 GMT
content-type: application/json
content-length: 20
access-control-allow-origin: www.[your domain]
apigw-requestid: ZSV2Bh7CCfMEPSw=

{"message": "Pong!"}
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
content-length: 20
access-control-allow-origin: https://www.[your domain]
apigw-requestid: Zi-Jei8myK4EJgQ=

{"message": "Pong!"}
real    0m0.188s
user    0m0.016s
sys     0m0.002s
```

Going from 4,100 milliseconds to under 200 milliseconds is a dramatic improvement.

#### Test An Endpoint For Logged-In Users

```
$ time curl -i -H "Origin: https://www.[your domain]" -H "Accept: application/json" https://api.[your domain]/api/v001/user
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
1. Click **Settings > Applications**
1. Click **Add Application**
    * Name: "**[your project] Frontend**"
    * Type: Select "**Front-end and mobile**"
    * Click "**Save**"
1. Click "**Details**" on left menu
1. Write down
    * **Domain**
    * **Client ID**
1. In **Callback URLs"
    * Set **Application homepage URI** to "`https://www.[your domain]`"
    * Set **Allowed callback URLs** to "`https://www.[your domain]`"
    * Set **Allowed logout redirect URLs** to "`https://www.[your domain]`"
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
    * `VITE_KINDE_DOMAIN`: ***`https://[your-project].kinde.com`***
    * `VITE_KINDE_REDIRECT_URL` : ***`https://www.[your domain]`***
    * `VITE_KINDE_LOGOUT_URL` : ***`https://www.[your domain]`***
    * `VITE_KINDE_TOKEN_AUDIENCE`: ***`https://api.[your domain]`***

Note: these are all considered very public, as the JavaScript client can't hide any secrets.

### Deploy Frontend

#### Login to Cloudflare

Beyond scope.

#### Create Cloudflare Pages Project

1. Under Build, expand **Compute**
1. Select **Workers & Pages**
1. Click **Create Application** in top right
1. Select **Get Started** in the middle of the page next to "Looking to deploy Pages?"
1. Click the **Get Started** button for "Import an existing Git repository"
1. Select the proper **GitHub account** and **Repository** for your project
1. Click blue **Begin setup** button
    * Branch: **main**
    * Framework present: **None**
    * Build command: **`npm run build`** 
    * Build output directory: **`dist`**
    * Root directory (advanced): **`frontend`**
1. Click blue **Save and Deploy** button
1. Watch the build 
1. When it reads **`Upload complete`**, you're done

### What Got Deployed

[insert pic showing how UI plugs in]


### Add Custom Domain

1. Under your Pages project, click "**Custom domains**"
1. Domain name: **`www.[your-project]`**
    * Cloudflare Pages do not support sites at root of a domain *unless* they host the domain
    * Not willing to give that up based on all the TLS/DNS goodness we get for hosting at R53
1. Click blue "**Continue**"
1. Click blue "**Begin CNAME setup**"
1. Copy the offered `*.pages.dev` value

### Add CNAME Record in Route 53

* In Route 53, add a new DNS record for your project domain
* Click **Hosted Zones**
* Click your domain
* Click the orange "**Create record**" button 
    * Record name: `www`
    * Record type: **CNAME**
    * Alias: **no/off**
    * Value: **`[pages.dev value from Cloudflare].`**
        * Note the trailing dot; that matters!
        * e.g. `your-project.pages.dev.`
    * TTL (seconds): **60**
    * Routing policy: **Simple routing**
    * Click the orange "**Create records**" button

### Resume Custom Domain Setup in Cloudflare

1. Click blue "**Check DNS records**" button
1. Cloudflare will say "starting search"
1. Wait 10-20 seconds
1. 1. Cloudflare will say "starting search"
1. A green dialog will pop up saying "**Domain activated. Your DNS setup is complete.**"
1. Click blue "**Continue**" link
1. You'll be shown the list of custom domains that are active for your Cloudflare Pages site

## System Test

1. Go to `https://www.[your domain]`
1. Click **Sign Up**
1. Provide email/password or give permission to let another social provider authenticate you
1. Get redirected back to the homepage but it shows you logged in
1. Take bearer token value from console

```
curl -s -H "Accept: application/json" -H "Authorization: Bearer [bearer token]" https://api.[your domain] | jq
```

Output will be similar to:
```
{
  "id": "kp_...",
  "preferred_email": "terry.ott@sixbuckssolutions.com",
  "last_name": "Ott",
  "first_name": "Terry",
  "is_suspended": false,
  "total_sign_ins": 2,
  "failed_sign_ins": 0,
  "last_signed_in": "2026-03-01T19:54:37.337802+00:00",
  "created_on": "2026-03-01T19:47:41.070375+00:00"
}
```
