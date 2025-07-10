import { createDefaultPreset } from "ts-jest";

const tsJestTransformCfg = createDefaultPreset().transform;

/** @type {import("jest").Config} **/
export default {
  preset: "ts-jest",
  testEnvironment: "node",
  extensionsToTreatAsEsm: [".ts"],
  setupFilesAfterEnv: [],
  detectOpenHandles: true,
  transform: {
    "^.+\\.tsx?$": ['ts-jest', { /* ts-jest config goes here in Jest */ }],
},
};