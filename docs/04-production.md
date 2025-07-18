# Deploying to Production

If you're considering a deployment to production, there are a couple of things you need to consider.  While the best care has been taken to develop this accelerator, it just that - a solution accelerator, to get you going quickly, to get insights, while allowing you to develop it further to your own liking.

## Authentication

By default, the solution is only secured with Basic authentication.  The reverse proxy (Nginx) does have support for various authentication mechanism, be it OATH2, SAML, etc.  You can configure further restrictions based on your own IDP requirements.

* [Restricting Access with HTTP Basic Authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/)
* [Configure NGINX Plus for SAML SSO with Microsoft Entra ID](https://www.f5.com/company/blog/nginx/configure-nginx-plus-for-saml-sso-with-microsoft-entra-id)

## TLS / SSL usage

By default, the solution only serves data via port 80 (HTTP), primarily due to the inability to issue a secure certificate automatically.  Due to the reverse proxy being run as Nginx, it is a trivial task to issue a formal certificate, and host it via port 443.

* [Configuring HTTPS servers](https://nginx.org/en/docs/http/configuring_https_servers.html)

## Use of Load Balancers

You may opt to run a load balancer, and have the Cloud platform scale a number of instances based on the load.

## Containers with changing IP addresses

On AWS, the Fargate container will start with a different IP address.  This can make it tricky to find the system.  For a production roll out, do consider sticking an Application Load Balancer in front of the container with a Target Group to ensure the application is always reachable.

## Hosting on a private vs public network

It is entirely possible to run the application on a private network.  Things to keep in mind though.

* The `collector` needs access to the secret vault.  This access may require internet access, or at least access to the VPC service endpoint.
* The `collector` also needs internet access (direct, or via a NAT gateway) to perform queries against the SaaS services we'll be querying.
* If you're using containers, then all the containers must be able to read the images from the repo, which may also require internet access.
* All the containers will need access to the database.

## AWS Fargate

The solution accelerator has the AWS Fargate container set to the `FARGATE_SPOT` type.  This is a bit cheaper to run, but may get terminated by AWS at any time.  Consider changing it to `FARGATE` if you want a perisistent container.  Keep in mind that FARGATE may be slightly more expensive.

## Database sizing

By default the database is set to a system of 32GB in size with a limited amount of memory.  Do consider upgrading the capacity.
