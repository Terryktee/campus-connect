FROM node:20-slim AS dependencies

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

FROM node:20-slim AS development

WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
