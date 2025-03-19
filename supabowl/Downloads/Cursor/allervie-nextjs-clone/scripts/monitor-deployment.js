#!/usr/bin/env node

const { execSync } = require('child_process');

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  underscore: '\x1b[4m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

// Get app ID from command line arguments
let appId = process.argv[2];

if (!appId) {
  try {
    console.log(`${colors.yellow}No App ID provided. Fetching most recent app...${colors.reset}`);
    const output = execSync('doctl apps list --format ID,Spec.Name --no-header | grep "allervie-analytics-dashboard" | head -n1', { encoding: 'utf8' });
    appId = output.trim().split(/\s+/)[0];
    
    if (!appId) {
      console.error(`${colors.red}Could not find app. Please provide App ID as argument.${colors.reset}`);
      process.exit(1);
    }
  } catch (error) {
    console.error(`${colors.red}Error finding app: ${error.message}${colors.reset}`);
    process.exit(1);
  }
}

console.log(`${colors.bright}${colors.blue}Allervie Analytics Dashboard Deployment Monitor${colors.reset}\n`);
console.log(`${colors.cyan}Monitoring app with ID: ${appId}${colors.reset}`);

// Get app details
try {
  const appDetails = execSync(`doctl apps get ${appId} --format ID,Spec.Name,DefaultIngress,ActiveDeployment.Phase --no-header`, { encoding: 'utf8' });
  const [id, name, url, phase] = appDetails.trim().split(/\s+/);
  
  console.log(`\n${colors.bright}App Details:${colors.reset}`);
  console.log(`  ID:     ${id}`);
  console.log(`  Name:   ${name}`);
  console.log(`  URL:    ${url}`);
  console.log(`  Status: ${getColorForPhase(phase)}${phase}${colors.reset}`);
  
  // Test health endpoint
  if (url) {
    try {
      console.log(`\n${colors.bright}Testing Health Endpoint:${colors.reset}`);
      const healthStatus = execSync(`curl -s -o /dev/null -w "%{http_code}" https://${url}/api/health`, { encoding: 'utf8' });
      
      if (healthStatus.trim() === '200') {
        console.log(`  ${colors.green}Health endpoint is responding correctly (200 OK)${colors.reset}`);
        
        // Get health details
        const healthDetails = execSync(`curl -s https://${url}/api/health`, { encoding: 'utf8' });
        const healthData = JSON.parse(healthDetails);
        
        console.log(`  Status: ${healthData.status === 'healthy' ? colors.green : colors.yellow}${healthData.status}${colors.reset}`);
        console.log(`  Environment: ${healthData.environment}`);
        console.log(`  Version: ${healthData.version}`);
        
        if (healthData.config && healthData.config.missingVariables) {
          console.log(`  ${colors.yellow}Missing variables: ${healthData.config.missingVariables.join(', ')}${colors.reset}`);
        }
      } else {
        console.log(`  ${colors.red}Health endpoint returned status ${healthStatus}${colors.reset}`);
      }
    } catch (error) {
      console.log(`  ${colors.red}Could not connect to health endpoint${colors.reset}`);
    }
  }
  
  // Get latest deployment
  const deploymentId = execSync(`doctl apps list-deployments ${appId} --format ID --no-header | head -n1`, { encoding: 'utf8' }).trim();
  
  if (deploymentId) {
    console.log(`\n${colors.bright}Latest Deployment (${deploymentId}):${colors.reset}`);
    
    const deploymentDetails = execSync(`doctl apps get-deployment ${appId} ${deploymentId} --format Phase,Progress,Created,Updated --no-header`, { encoding: 'utf8' });
    const [deployPhase, progress, created, updated] = deploymentDetails.trim().split(/\s+/);
    
    console.log(`  Status:   ${getColorForPhase(deployPhase)}${deployPhase}${colors.reset}`);
    console.log(`  Progress: ${progress || 'N/A'}`);
    console.log(`  Created:  ${created}`);
    console.log(`  Updated:  ${updated}`);
  }
  
  // Show logs commands
  console.log(`\n${colors.bright}View Logs:${colors.reset}`);
  console.log(`  ${colors.cyan}doctl apps logs ${appId}${colors.reset}`);
  console.log(`  ${colors.cyan}doctl apps logs ${appId} --follow${colors.reset}`);
  
} catch (error) {
  console.error(`${colors.red}Error monitoring deployment: ${error.message}${colors.reset}`);
}

// Helper function to get color for phase
function getColorForPhase(phase) {
  if (!phase) return colors.reset;
  
  switch (phase.toUpperCase()) {
    case 'ACTIVE':
    case 'DEPLOYED':
    case 'RUNNING':
      return colors.green;
    case 'BUILDING':
    case 'DEPLOYING':
    case 'PENDING':
      return colors.yellow;
    case 'ERROR':
    case 'FAILED':
      return colors.red;
    default:
      return colors.reset;
  }
}