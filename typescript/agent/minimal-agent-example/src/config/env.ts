// src/config/env.ts
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import dotenv from "dotenv";
import dotenvFlow from "dotenv-flow";

// 1) Load a shared file FIRST (lowest precedence among files)
//    Real env vars in process.env always win.
const shared = path.join(os.homedir(), ".config", "secrets", "myapps.env");
if (fs.existsSync(shared)) {
  dotenv.config({ path: shared, override: false });
}

// 2) Let dotenv-flow load the standard cascade for the project:
//    .env -> .env.local -> .env.[NODE_ENV] -> .env.[NODE_ENV].local
dotenvFlow.config({
  node_env: process.env.NODE_ENV, // e.g. "development", "test", "production"
  silent: true,                   // don’t log missing files
});