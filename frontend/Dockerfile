FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.d/40-print-url.sh /docker-entrypoint.d/40-print-url.sh
RUN sed -i 's/\r$//' /docker-entrypoint.d/40-print-url.sh \
    && chmod +x /docker-entrypoint.d/40-print-url.sh
EXPOSE 80
