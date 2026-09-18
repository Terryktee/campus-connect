# Save this as frontend/Dockerfile

FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

# Startup command is set in docker-compose.yml (npm run dev for local dev).

