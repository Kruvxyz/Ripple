# Use an official Node.js runtime as a parent image
FROM node:16-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json files
COPY package*.json ./

# Install any needed packages
RUN npm install

# Copy the rest of the app's source code
COPY . .

# Build the app for production
RUN npm run build

# Serve the app
RUN npm install -g serve
CMD ["serve", "-s", "build"]
# CMD ["npm", "start"]

# Expose port 3000 to the outside
EXPOSE 3000
