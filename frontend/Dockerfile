# innobot_test/frontend/Dockerfile

# Stage 1: Build the React application
FROM node:22-alpine AS build
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Pass the Backend API URL as a build argument
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy the rest of the code and build for production
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy the built React app from Stage 1
COPY --from=build /app/dist /usr/share/nginx/html

# Copy our custom Nginx routing configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 inside the container
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]