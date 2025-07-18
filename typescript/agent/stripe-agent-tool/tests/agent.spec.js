"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const StripeAgent_1 = require("../src/agents/StripeAgent");
const langchain_1 = require("@stripe/agent-toolkit/langchain");
const openai_1 = require("@langchain/openai");
const agents_1 = require("langchain/agents");
const stripe_1 = __importDefault(require("stripe"));
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
// Mock dependencies
jest.mock('@stripe/agent-toolkit/langchain');
jest.mock('@langchain/openai');
jest.mock('langchain/agents');
jest.mock('stripe');
jest.mock('langchain/hub');
describe('StripeAgent', () => {
    let agent;
    let mockStripeToolkit;
    let mockLLM;
    let mockAgentExecutor;
    let mockStripe;
    let mockStripeProducts;
    let mockStripePrices;
    let mockStripePaymentLinks;
    beforeEach(() => {
        jest.clearAllMocks();
        // Mock Stripe resources
        mockStripeProducts = {
            list: jest.fn(),
        };
        mockStripePrices = {
            list: jest.fn(),
        };
        mockStripePaymentLinks = {
            create: jest.fn(),
        };
        // Mock Stripe instance
        mockStripe = {
            products: mockStripeProducts,
            prices: mockStripePrices,
            paymentLinks: mockStripePaymentLinks,
        };
        stripe_1.default.mockImplementation(() => mockStripe);
        // Mock StripeAgentToolkit
        mockStripeToolkit = {
            getTools: jest.fn().mockReturnValue([]),
        };
        langchain_1.StripeAgentToolkit.mockImplementation(() => mockStripeToolkit);
        // Mock ChatOpenAI
        mockLLM = {};
        openai_1.ChatOpenAI.mockImplementation(() => mockLLM);
        // Mock AgentExecutor
        mockAgentExecutor = {
            invoke: jest.fn(),
        };
        agents_1.AgentExecutor.mockImplementation(() => mockAgentExecutor);
        // Mock langchain/hub pull function
        const mockPull = jest.fn().mockResolvedValue({
            template: 'mock prompt template'
        });
        jest.doMock('langchain/hub', () => ({
            pull: mockPull
        }));
        // Mock the structured chat agent creation
        const mockCreateStructuredChatAgent = jest.fn().mockResolvedValue({});
        jest.doMock('langchain/agents', () => ({
            AgentExecutor: agents_1.AgentExecutor,
            createStructuredChatAgent: mockCreateStructuredChatAgent
        }));
    });
    describe('creates link without looping', () => {
        it('should call each helper/stripe primitive exactly once', async () => {
            // Setup test data
            const mockProduct = {
                id: 'prod_test123',
                name: 'Test Product',
                created: 1234567890
            };
            const mockPrice = {
                id: 'price_test123',
                product: 'prod_test123',
                unit_amount: 2000,
                currency: 'usd'
            };
            const mockPaymentLink = {
                id: 'plink_test123',
                url: 'https://buy.stripe.com/test123'
            };
            // Mock Stripe API responses
            mockStripeProducts.list.mockResolvedValue({
                data: [mockProduct]
            });
            mockStripePrices.list.mockResolvedValue({
                data: [mockPrice]
            });
            mockStripePaymentLinks.create.mockResolvedValue(mockPaymentLink);
            // Mock agent execution result
            mockAgentExecutor.invoke.mockResolvedValue({
                output: "Perfect! I've created your payment link.",
                intermediateSteps: [
                    {
                        action: {
                            tool: 'get_price_and_create_payment_link',
                            toolInput: JSON.stringify({ product_name: 'Test Product', quantity: 1 })
                        },
                        observation: 'https://buy.stripe.com/test123'
                    }
                ]
            });
            // Initialize agent
            agent = new StripeAgent_1.StripeAgent();
            await agent.init();
            // Process purchase message
            const response = await agent.processMessage('I want to buy Test Product');
            // Verify each Stripe primitive was called exactly once
            expect(mockStripeProducts.list).toHaveBeenCalledTimes(1);
            expect(mockStripePrices.list).toHaveBeenCalledTimes(1);
            expect(mockStripePaymentLinks.create).toHaveBeenCalledTimes(1);
            // Verify the response contains the payment link
            expect(response.success).toBe(true);
            expect(response.message).toContain('https://buy.stripe.com/test123');
            // Verify no looping occurred (agent executor called once)
            expect(mockAgentExecutor.invoke).toHaveBeenCalledTimes(1);
        });
        it('should handle multiple products without duplicating calls', async () => {
            // Setup test data with multiple products
            const mockProducts = [
                { id: 'prod_1', name: 'Telescope', created: 1234567890 },
                { id: 'prod_2', name: 'Space Suit', created: 1234567891 }
            ];
            const mockPrice = {
                id: 'price_telescope',
                product: 'prod_1',
                unit_amount: 50000,
                currency: 'usd'
            };
            const mockPaymentLink = {
                id: 'plink_telescope',
                url: 'https://buy.stripe.com/telescope123'
            };
            // Mock Stripe API responses
            mockStripeProducts.list.mockResolvedValue({
                data: mockProducts
            });
            mockStripePrices.list.mockResolvedValue({
                data: [mockPrice]
            });
            mockStripePaymentLinks.create.mockResolvedValue(mockPaymentLink);
            // Mock agent execution result
            mockAgentExecutor.invoke.mockResolvedValue({
                output: "Perfect! I've created your payment link for the Telescope.",
                intermediateSteps: [
                    {
                        action: {
                            tool: 'get_price_and_create_payment_link',
                            toolInput: JSON.stringify({ product_name: 'Telescope', quantity: 1 })
                        },
                        observation: 'https://buy.stripe.com/telescope123'
                    }
                ]
            });
            // Initialize agent
            agent = new StripeAgent_1.StripeAgent();
            await agent.init();
            // Process purchase message
            const response = await agent.processMessage('I want to buy Telescope');
            // Verify each Stripe primitive was called exactly once
            expect(mockStripeProducts.list).toHaveBeenCalledTimes(1);
            expect(mockStripePrices.list).toHaveBeenCalledTimes(1);
            expect(mockStripePaymentLinks.create).toHaveBeenCalledTimes(1);
            // Verify the response
            expect(response.success).toBe(true);
            expect(response.message).toContain('https://buy.stripe.com/telescope123');
            // Verify no looping occurred
            expect(mockAgentExecutor.invoke).toHaveBeenCalledTimes(1);
        });
    });
    describe('compiles clean', () => {
        it('should run npm run build successfully', async () => {
            try {
                const { stdout, stderr } = await execAsync('npm run build');
                // Check that build completed successfully
                expect(stderr).not.toContain('error');
                expect(stderr).not.toContain('Error');
                // Optional: Check that output files were created
                const fs = require('fs');
                expect(fs.existsSync('dist')).toBe(true);
                expect(fs.existsSync('dist/index.js')).toBe(true);
                expect(fs.existsSync('dist/agents/StripeAgent.js')).toBe(true);
                console.log('✅ TypeScript compilation successful');
                if (stdout)
                    console.log('Build output:', stdout);
            }
            catch (error) {
                console.error('❌ TypeScript compilation failed:', error.message);
                if (error.stdout)
                    console.log('stdout:', error.stdout);
                if (error.stderr)
                    console.error('stderr:', error.stderr);
                throw error;
            }
        }, 60000); // 60 second timeout for build
    });
    describe('error handling', () => {
        it('should handle product not found gracefully', async () => {
            // Mock empty product list
            mockStripeProducts.list.mockResolvedValue({
                data: []
            });
            // Mock agent execution result with error
            mockAgentExecutor.invoke.mockResolvedValue({
                output: "I apologize, but I couldn't find that product in our inventory.",
                intermediateSteps: [
                    {
                        action: {
                            tool: 'get_price_and_create_payment_link',
                            toolInput: JSON.stringify({ product_name: 'Nonexistent Product', quantity: 1 })
                        },
                        observation: 'Error: Product not found'
                    }
                ]
            });
            // Initialize agent
            agent = new StripeAgent_1.StripeAgent();
            await agent.init();
            // Process purchase message for non-existent product
            const response = await agent.processMessage('I want to buy Nonexistent Product');
            // Verify Stripe products.list was called
            expect(mockStripeProducts.list).toHaveBeenCalledTimes(1);
            // Verify response handles error gracefully
            expect(response.success).toBe(true);
            expect(response.message).toContain("couldn't find that product");
            // Verify no payment link was created
            expect(mockStripePaymentLinks.create).not.toHaveBeenCalled();
        });
    });
    describe('conversation flow', () => {
        it('should maintain conversation history', async () => {
            // Initialize agent
            agent = new StripeAgent_1.StripeAgent();
            await agent.init();
            // Mock initial response
            mockAgentExecutor.invoke.mockResolvedValue({
                output: 'Hello! I can help you with our products.',
                intermediateSteps: []
            });
            // Send first message
            await agent.processMessage('Hello');
            // Check conversation history
            const history = agent.getConversationHistory();
            expect(history).toHaveLength(2); // user + assistant
            expect(history[0].role).toBe('user');
            expect(history[0].content).toBe('Hello');
            expect(history[1].role).toBe('assistant');
            expect(history[1].content).toContain('Hello');
        });
        it('should clear conversation history', async () => {
            // Initialize agent
            agent = new StripeAgent_1.StripeAgent();
            await agent.init();
            // Mock response
            mockAgentExecutor.invoke.mockResolvedValue({
                output: 'Hello!',
                intermediateSteps: []
            });
            // Send message
            await agent.processMessage('Hello');
            // Verify history exists
            expect(agent.getConversationHistory()).toHaveLength(2);
            // Clear history
            agent.clearConversationHistory();
            // Verify history is empty
            expect(agent.getConversationHistory()).toHaveLength(0);
        });
    });
});
//# sourceMappingURL=agent.spec.js.map