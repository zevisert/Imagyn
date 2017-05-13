# Project website
> We're supposed to have a website for our team as part of the 499 requirements. So here's a start.

## Basics
- Node.js / Express static file server
- HTML / CSS pulled from [HTML5up](https://html5up.net)

## Local dev setup
This is just static files, so any way you want to serve the `static` directory will do.
The way it works currently is by using an Express.js static server.

Use Node `v7.10.0` and npm `4.2.0` so your dev matches what's on the server. Suggest NVM (Node Version Manager) to quickly change node versions.

There's seperate server files for dev and prod. You shouldn't need to edit these for the time being.
- `dev.js`: Runs an HTTP only server serving the contents of the `static` directory.
 - Requires a `.env` file with `HTTP_PORT` set.
```
> npm install
> echo "HTTP_PORT=8080" > .env
> npm run dev
```


- `prod.js`: Runs an HTTP server that only responds with 301 redirects to the same resource behind HTTPS. The HTTPS server does the same thing that the dev version.
 - Requires a `.env` file with `HTTP_PORT`, `HTTPS_PORT` and `SSL_PASSPHRASE` set.
```
> npm install
> echo -ne "HTTP_PORT=80\nHTTPS_PORT=443\nSSL_PASSPHRASE=<[///]>"
> npm start
```
