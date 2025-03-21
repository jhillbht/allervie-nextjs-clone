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

try {
  // Get app details
  const appDetails = execSync(`doctl apps get ${appId} --format ID,Spec.Name,DefaultIngress,ActiveDeployment.Phase --no-header`, { encoding: 'utf8' });
  const [id, name, url, phase] = appDetails.trim().split(/\s+/);
  
  console.log(`\n${colors.bright}App details:${colors.reset}`);
  console.log(`  ID:     ${id}`);
  console.log(`  Name:   ${name}`);
  console.log(`  URL:    ${url}`);
  console.log(`  Status: ${getColorForPhase(phase)}${phase}${colors.reset}`);
  
  // Get deployment status
  const deploymentId = execSync(`doctl apps list-deployments ${appId} --format ID --no-header | head -n1`, { encoding: 'utf8' }).trim();
  
  if (deploymentId) {
    console.log(`\n${colors.bright}Latest deployment (${deploymentId}):${colors.reset}`);
    
    try {
      const deploymentDetails = execSync(`doctl apps get-deployment ${appId} ${deploymentId} --format Phase,Progress,Created,Updated --no-header`, { encoding: 'utf8' });
      const [deployPhase, progress, created, updated] = deploymentDetails.trim().split(/\s+/);
      
      console.log(`  Status:   ${getColorForPhase(deployPhase)}${deployPhase}${colors.reset}`);
      console.log(`  Progress: ${progress || 'N/A'}`);
      console.log(`  Created:  ${created}`);
      console.log(`  Updated:  ${updated}`);
      
      // Show deployment logs if there's an error
      if (deployPhase === 'ERROR') {
        console.log(`\n${colors.bright}${colors.red}Deployment logs (showing errors):${colors.reset}`);
        
        try {
          const logs = execSync(`doctl apps logs ${appId} --deployment ${deploymentId}`, { encoding: 'utf8' });
          
          // Extract and print error lines
          const errorLines = logs.split('\n').filter(line => 
            line.toLowerCase().includes('error') || 
            line.toLowerCase().includes('failed') ||
            line.toLowerCase().includes('exception')
          );
          
          if (errorLines.length > 0) {
            errorLines.forEach(line => console.log(`  ${colors.red}${line}${colors.reset}`));
          } else {
            console.log(`  ${colors.yellow}No specific error lines found. View full logs with:${colors.reset}`);
            console.log(`  ${colors.cyan}doctl apps logs ${appId} --deployment ${deploymentId}${colors.reset}`);
          }
        } catch (err) {
          console.log(`  ${colors.yellow}Could not fetch logs: ${err.message}${colors.reset}`);
        }
        
        // Provide troubleshooting suggestions
        console.log(`\n${colors.bright}Troubleshooting suggestions:${colors.reset}`);
        console.log(`  1. Verify package manager configuration in package.json`);
        console.log(`  2. Ensure next.config.js has 'output: "standalone"' setting`);
        console.log(`  3. Check that environment variables are properly configured`);
        console.log(`  4. Make sure the Dockerfile uses the correct Node.js version (22.x)`);
      }
    } catch (err) {
      console.log(`  ${colors.yellow}Could not fetch deployment details: ${err.message}${colors.reset}`);
    }
  } else {
    console.log(`\n${colors.yellow}No deployments found for this app.${colors.reset}`);
  }
  
  // Show commands for further investigation
  console.log(`\n${colors.bright}Useful commands:${colors.reset}`);
  console.log(`  ${colors.cyan}doctl apps logs ${appId}${colors.reset} - View app logs`);
  console.log(`  ${colors.cyan}doctl apps logs ${appId} --follow${colors.reset} - Follow logs in real-time`);
  console.log(`  ${colors.cyan}doctl apps get-deployment ${appId} DEPLOYMENT_ID${colors.reset} - View deployment details`);
  
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
