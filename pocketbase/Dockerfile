FROM alpine:3.18

# Instala utilidades necesarias
RUN apk add --no-cache curl unzip

# Descarga la versión estable de PocketBase (ajusta la versión según requieras)
RUN curl -fsSL https://github.com/pocketbase/pocketbase/releases/download/v0.16.7/pocketbase_0.16.7_linux_amd64.zip -o pb.zip \
    && unzip pb.zip -d /pb \
    && rm pb.zip

WORKDIR /pb

# Crea la carpeta de datos si no existe
RUN mkdir -p /pb/pb_data

# Exponemos el puerto 8090
EXPOSE 8090

CMD ["./pocketbase", "serve", "--http=0.0.0.0:8090", "--dir=/pb/pb_data"]
