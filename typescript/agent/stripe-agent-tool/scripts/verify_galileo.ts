import dotenv from 'dotenv';
import { getLogger, getProjects, getLogStreams } from 'galileo';

// Load environment variables
dotenv.config();

async function verifyGalileoSetup() {
  console.log('🔍 Verifying Galileo Configuration...\n');

  // Check environment variables
  const requiredVars = {
    GALILEO_API_KEY: process.env.GALILEO_API_KEY,
    GALILEO_PROJECT: process.env.GALILEO_PROJECT,
    GALILEO_LOG_STREAM: process.env.GALILEO_LOG_STREAM,
  };

  console.log('📋 Environment Variables:');
  for (const [key, value] of Object.entries(requiredVars)) {
    if (!value) {
      console.log(`❌ ${key}: MISSING`);
    } else if (value.includes('your_') || value.includes('example')) {
      console.log(`⚠️  ${key}: ${value} (needs to be updated)`);
    } else {
      console.log(`✅ ${key}: ${value.substring(0, 10)}...`);
    }
  }

  // Test Galileo connection
  try {
    console.log('\n🔗 Testing Galileo Connection...');
    const logger = getLogger();
    console.log('✅ Galileo logger initialized successfully');

    // Test project access
    console.log('\n📁 Testing Project Access...');
    const projects = await getProjects();
    console.log(`✅ Found ${projects.length} projects`);
    
    const targetProject = process.env.GALILEO_PROJECT;
    const projectExists = projects.some(p => p.name === targetProject);
    
    if (projectExists) {
      console.log(`✅ Project "${targetProject}" exists`);
    } else {
      console.log(`❌ Project "${targetProject}" NOT FOUND`);
      console.log('Available projects:');
      projects.forEach(p => console.log(`  - ${p.name}`));
    }

    // Test log stream access
    if (projectExists) {
      console.log('\n📊 Testing Log Stream Access...');
      const logStreams = await getLogStreams();
      console.log(`✅ Found ${logStreams.length} log streams`);
      
      const targetLogStream = process.env.GALILEO_LOG_STREAM;
      const logStreamExists = logStreams.some(ls => ls.name === targetLogStream);
      
      if (logStreamExists) {
        console.log(`✅ Log stream "${targetLogStream}" exists`);
      } else {
        console.log(`❌ Log stream "${targetLogStream}" NOT FOUND`);
        console.log('Available log streams:');
        logStreams.forEach(ls => console.log(`  - ${ls.name}`));
      }
    }

  } catch (error) {
    console.log('\n❌ Galileo Connection Failed:');
    console.log(`Error: ${error.message}`);
    
    if (error.message.includes('403')) {
      console.log('\n🔧 Troubleshooting 403 Error:');
      console.log('1. Check your GALILEO_API_KEY is correct');
      console.log('2. Verify your API key has the right permissions');
      console.log('3. Make sure your Galileo account is active');
      console.log('4. Try regenerating your API key in the Galileo dashboard');
    }
  }

  console.log('\n📝 Next Steps:');
  console.log('1. Update your .env file with correct values');
  console.log('2. Create the project/log stream in Galileo if they don\'t exist');
  console.log('3. Run this script again to verify');
}

// Run the verification
verifyGalileoSetup().catch(console.error); 