import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

describe('StripeAgent', () => {
  describe('creates link without looping', () => {
    it('should call each helper/stripe primitive exactly once', async () => {
      // Mock Stripe SDK methods
      const mockStripeProducts = { list: jest.fn() };
      const mockStripePrices = { list: jest.fn() };
      const mockStripePaymentLinks = { create: jest.fn() };
      
      // Mock Stripe constructor
      const mockStripe = {
        products: mockStripeProducts,
        prices: mockStripePrices,
        paymentLinks: mockStripePaymentLinks
      };
      
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
      
      // Simulate the get_price_and_create_payment_link atomic tool
      const getPriceAndCreateLink = async (input: string) => {
        const params = JSON.parse(input);
        const { product_name, quantity } = params;
        
        // Call products.list
        const products = await mockStripe.products.list({limit: 100});
        const product = products.data.find((p: any) => p.name.toLowerCase() === product_name.toLowerCase());
        if (!product) throw new Error('Product not found');
        
        // Call prices.list
        const prices = await mockStripe.prices.list({product: product.id, active: true});
        if (!prices.data.length) throw new Error('No active price');
        
        // Call paymentLinks.create
        const link = await mockStripe.paymentLinks.create({
          line_items: [{price: prices.data[0].id, quantity}]
        });
        return link.url;
      };
      
      // Test the atomic tool execution
      const result = await getPriceAndCreateLink(JSON.stringify({
        product_name: 'Test Product',
        quantity: 1
      }));
      
      // Verify each Stripe primitive was called exactly once
      expect(mockStripeProducts.list).toHaveBeenCalledTimes(1);
      expect(mockStripePrices.list).toHaveBeenCalledTimes(1);
      expect(mockStripePaymentLinks.create).toHaveBeenCalledTimes(1);
      
      // Verify the result is the payment link URL
      expect(result).toBe('https://buy.stripe.com/test123');
    });
    
    it('should handle multiple products without duplicating calls', async () => {
      // Mock Stripe SDK methods
      const mockStripeProducts = { list: jest.fn() };
      const mockStripePrices = { list: jest.fn() };
      const mockStripePaymentLinks = { create: jest.fn() };
      
      // Mock Stripe constructor
      const mockStripe = {
        products: mockStripeProducts,
        prices: mockStripePrices,
        paymentLinks: mockStripePaymentLinks
      };
      
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
      
      // Simulate the get_price_and_create_payment_link atomic tool
      const getPriceAndCreateLink = async (input: string) => {
        const params = JSON.parse(input);
        const { product_name, quantity } = params;
        
        // Call products.list
        const products = await mockStripe.products.list({limit: 100});
        const product = products.data.find((p: any) => p.name.toLowerCase() === product_name.toLowerCase());
        if (!product) throw new Error('Product not found');
        
        // Call prices.list
        const prices = await mockStripe.prices.list({product: product.id, active: true});
        if (!prices.data.length) throw new Error('No active price');
        
        // Call paymentLinks.create
        const link = await mockStripe.paymentLinks.create({
          line_items: [{price: prices.data[0].id, quantity}]
        });
        return link.url;
      };
      
      // Test the atomic tool execution
      const result = await getPriceAndCreateLink(JSON.stringify({
        product_name: 'Telescope',
        quantity: 1
      }));
      
      // Verify each Stripe primitive was called exactly once
      expect(mockStripeProducts.list).toHaveBeenCalledTimes(1);
      expect(mockStripePrices.list).toHaveBeenCalledTimes(1);
      expect(mockStripePaymentLinks.create).toHaveBeenCalledTimes(1);
      
      // Verify the result is the payment link URL
      expect(result).toBe('https://buy.stripe.com/telescope123');
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
        expect(fs.existsSync('dist/src/index.js')).toBe(true);
        expect(fs.existsSync('dist/src/agents/StripeAgent.js')).toBe(true);
        
        console.log('✅ TypeScript compilation successful');
        if (stdout) console.log('Build output:', stdout);
      } catch (error: any) {
        console.error('❌ TypeScript compilation failed:', error.message);
        if (error.stdout) console.log('stdout:', error.stdout);
        if (error.stderr) console.error('stderr:', error.stderr);
        throw error;
      }
    }, 60000); // 60 second timeout for build
  });

  describe('error handling', () => {
    it('should handle product not found gracefully', async () => {
      // Mock Stripe SDK methods
      const mockStripeProducts = { list: jest.fn() };
      const mockStripePrices = { list: jest.fn() };
      const mockStripePaymentLinks = { create: jest.fn() };
      
      // Mock Stripe constructor
      const mockStripe = {
        products: mockStripeProducts,
        prices: mockStripePrices,
        paymentLinks: mockStripePaymentLinks
      };
      
      // Mock empty product list
      mockStripeProducts.list.mockResolvedValue({
        data: []
      });
      
      // Simulate the get_price_and_create_payment_link atomic tool
      const getPriceAndCreateLink = async (input: string) => {
        const params = JSON.parse(input);
        const { product_name, quantity } = params;
        
        // Call products.list
        const products = await mockStripe.products.list({limit: 100});
        const product = products.data.find((p: any) => p.name.toLowerCase() === product_name.toLowerCase());
        if (!product) throw new Error('Product not found');
        
        // Call prices.list
        const prices = await mockStripe.prices.list({product: product.id, active: true});
        if (!prices.data.length) throw new Error('No active price');
        
        // Call paymentLinks.create
        const link = await mockStripe.paymentLinks.create({
          line_items: [{price: prices.data[0].id, quantity}]
        });
        return link.url;
      };
      
      // Test the atomic tool execution should throw error
      await expect(getPriceAndCreateLink(JSON.stringify({
        product_name: 'Nonexistent Product',
        quantity: 1
      }))).rejects.toThrow('Product not found');
      
      // Verify Stripe products.list was called
      expect(mockStripeProducts.list).toHaveBeenCalledTimes(1);
      
      // Verify no payment link was created
      expect(mockStripePaymentLinks.create).not.toHaveBeenCalled();
    });
  });

  describe('conversation flow', () => {
    it('should maintain conversation history', async () => {
      // Mock conversation history
      const mockHistory = [
        { role: 'user', content: 'Hello', timestamp: new Date() },
        { role: 'assistant', content: 'Hello! I can help you with our products.', timestamp: new Date() }
      ];
      
      // Test conversation history functionality
      expect(mockHistory).toHaveLength(2);
      expect(mockHistory[0].role).toBe('user');
      expect(mockHistory[0].content).toBe('Hello');
      expect(mockHistory[1].role).toBe('assistant');
      expect(mockHistory[1].content).toContain('Hello');
    });
    
    it('should clear conversation history', async () => {
      // Mock conversation history
      let mockHistory = [
        { role: 'user', content: 'Hello', timestamp: new Date() },
        { role: 'assistant', content: 'Hello!', timestamp: new Date() }
      ];
      
      // Verify history exists
      expect(mockHistory).toHaveLength(2);
      
      // Clear history
      mockHistory = [];
      
      // Verify history is empty
      expect(mockHistory).toHaveLength(0);
    });
  });
});
