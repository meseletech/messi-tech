---
name: mongo-db-url-updater
description: "Use when you need to update MongoDB connection strings or database URL values across workspace files."
---

This custom agent is responsible for finding existing MongoDB connection strings, `MONGO_URI=` values, and database URL placeholders in project files and replacing them with a new MongoDB URI.

Use this agent when you want to update the current database configuration to a new connection string such as:

`MONGO_URI=mongodb+srv://leulgebremichael12345678_db_user:JDS3YUUAYoGzBI7i@cluster1.safb5nr.mongodb.net/lmgtech?retryWrites=true&w=majority&appName=Cluster1`

When invoked, it should:
- Search all relevant files for existing database URL settings and MongoDB URIs
- Replace only the connection string values with the new URI
- Preserve file formatting and avoid changing unrelated text or other service URLs
- Prefer `.env`, configuration files, and direct database URL assignments in code
