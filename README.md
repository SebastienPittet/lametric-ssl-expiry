# lametric-ssl-expiry

Public API to display the remaining days before expiration of a public SSL certificate.
The result is a JSON content, consumed by a Lametric Time application (ssl-expiry) and also available as a web application.

## Run the Python app as a service
https://www.shubhamdipt.com/blog/how-to-create-a-systemd-service-in-linux/

## Container
- docker build . -t ssl-expiry:version  (will produce an image size of < 30 MB)
- docker run -d -p 5000:5000 <docker image>
- docker push exo.container-registry.com/pittet-sebastien/ssl-expiry:version

## Find it in the store
https://apps.lametric.com/apps/ssl_expiry/8659

## Demo
- https://certificate.pittet.org/api/v1?hostname=lametric.com&port=443
- Web application [https://certificate.pittet.org](https://certificate.pittet.org)

## Default values
If the application is unconfigured, the default values are set to:
* hostname: lametric.com
* port: 443

## Contributions
Please send Pull Request !
