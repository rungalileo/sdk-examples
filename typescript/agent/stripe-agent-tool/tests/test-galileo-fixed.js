const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testProperGalileoLogging() {
    console.log('🔬 Testing PROPER Galileo Input/Output Separation...');
    
    try {
        // Create agent
        const agent = new StripeAgent();
        await agent.init();
        
        // Start a session
        console.log('📊 Starting Galileo session...');
        const sessionId = await agent.startGalileoSession('Test Input/Output Session');
        console.log(`✅ Session started: ${sessionId}`);
        
        // Test with a clear user input vs agent output
        const userInput = 'Create a payment link for the Mars Explorer Kit for $199';
        
        console.log('🚀 Processing test message...');
        console.log(`📝 USER INPUT: "${userInput}"`);
        
        const response = await agent.processMessage(userInput);
        
        console.log('✅ Message processed successfully');
        console.log(`📝 AGENT OUTPUT: "${response.message.substring(0, 200)}..."`);
        
        if (response.data) {
            console.log('⏱️ Execution time:', response.data.executionTime + 'ms');
            console.log('🔧 Tools used:', response.data.toolsUsed);
        }
        
        // Log conversation
        console.log('📊 Logging conversation to Galileo...');
        await agent.logConversationToGalileo();
        console.log('✅ Conversation logged');
        
        // Conclude session
        console.log('🔒 Concluding Galileo session...');
        await agent.concludeGalileoSession();
        console.log('✅ Session concluded');
        
        console.log('\n🎉 INPUT/OUTPUT SEPARATION TEST COMPLETED!');
        console.log('📊 Check your Galileo dashboard to verify:');
        console.log(`   📥 INPUT should be: "${userInput}"`);
        console.log(`   📤 OUTPUT should be: "${response.message.substring(0, 100)}..."`);
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        process.exit(1);
    }
}

testProperGalileoLogging();
