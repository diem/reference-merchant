FROM nginx:1.17-alpine as dynamic_conf

#-------------------------------------------------------------------
FROM dynamic_conf as default_conf
COPY nginx.conf /etc/nginx/nginx.conf
COPY tmp/frontend/. /html/
