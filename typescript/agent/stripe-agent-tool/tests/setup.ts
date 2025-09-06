// Global test setup
import "./config/environment";  // side-effect: loads env va

// Load environment variables for testing
config();

// Mock environment variables if not set
process.env.STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || 'sk_test_mock_key';
process.env.OPENAI_API_KEY = process.env.OPENAI_API_KEY || 'sk-mock-openai-key';
process.env.GALILEO_API_KEY = process.env.GALILEO_API_KEY || 'mock-galileo-key';
process.env.GALILEO_URL = process.env.GALILEO_URL || 'https://mock-galileo.com';
