"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// Global test setup
const dotenv_1 = require("dotenv");
// Load environment variables for testing
(0, dotenv_1.config)();
// Mock environment variables if not set
process.env.STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || 'sk_test_mock_key';
process.env.OPENAI_API_KEY = process.env.OPENAI_API_KEY || 'sk-mock-openai-key';
process.env.GALILEO_API_KEY = process.env.GALILEO_API_KEY || 'mock-galileo-key';
process.env.GALILEO_URL = process.env.GALILEO_URL || 'https://mock-galileo.com';
//# sourceMappingURL=setup.js.map