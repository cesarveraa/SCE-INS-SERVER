# gateway/Dockerfile

FROM nginx:1.25-alpine

# Copiamos la config de Nginx
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
