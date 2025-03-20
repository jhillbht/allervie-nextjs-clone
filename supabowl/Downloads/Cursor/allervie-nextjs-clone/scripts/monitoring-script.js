#!/usr/bin/env node
/**
 * Allervie Dashboard Deployment Monitor
 * 
 * This script monitors the status of a DigitalOcean App Platform deployment
 * and provides detailed diagnostics and troubleshooting suggestions.
 * 
 * Usage:
 *   node monitoring-script.js [APP_ID]
 * 
 * If APP_ID is not provided, it will attempt to use the most recent app.
 */

const { execSync } = require('child_process');

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

console.log(`${colors.bright}${colors.blue}Allervie Dashboard Deployment Monitor${colors.reset}\n`);

// Check if doctl is installed
function checkDoctlInstalled() {
  try {
    execSync('doctl version', { stdio: 'ignore' });
    return true;
  } catch (error) {
    console.error(`${colors.red}Error: doctl is not installed or not in PATH.${colors.reset}`);
    console.error(`Please install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/`);
    return false;
  }
}

// Check if authenticated with DigitalOcean
function checkAuthenticated() {
  try {
    execSync('doctl account get', { stdio: 'ignore' });
    return true;
  } catch (error) {
    console.error(`${colors.red}Error: Not authenticated with DigitalOcean.${colors.reset}`);
    console.error(`Please run 'doctl auth init' to authenticate.`);
    return false;
  }
}

// Get the App ID from arguments or fetch most recent app
function getAppId(args) {
  if (args.length > 2) {
    return args[2];
  }
  
  try {
    console.log(`${colors.cyan}No App ID provided. Fetching most recent app...${colors.reset}`);
    const output = execSync('doctl apps list --format ID,Spec.Name --no-header | grep "allervie-analytics-dashboard" | head -n 1', { encoding: 'utf8' });
    const appId = output.trim().split(/\s+/)[0];
    
    if (!appId) {
      console.error(`${colors.red}No apps found matching 'allervie-analytics-dashboard'.${colors.reset}`);
      return null;
    }
    
    return appId;
  } catch (error) {
    console.error(`${colors.red}Error fetching apps: ${error.message}${colors.reset}`);
    return null;
  }
}

// Get app details
function getAppDetails(appId) {
  try {
    const output = execSync(`doctl apps get ${appId} --format ID,Spec.Name,DefaultIngress,ActiveDeployment.ID,ActiveDeployment.Phase,ActiveDeployment.Progress.SuccessSteps,ActiveDeployment.Progress.TotalSteps,ActiveDeployment.Progress.ErrorSteps --no-header`, { encoding: 'utf8' });
    const [id, name, url, deploymentId, phase, successSteps, totalSteps, errorSteps] = output.trim().split(/\s+/);
    
    return {
      id,
      name,
      url,
      deployment: {
        id: deploymentId,
        phase,
        progress: {
          success: parseInt(successSteps || 0),
          total: parseInt(totalSteps || 0),
          error: parseInt(errorSteps || 0),
        }
      }
    };
  } catch (error) {
    console.error(`${colors.red}Error fetching app details: ${error.message}${colors.reset}`);
    return null;
  }
}

// Get deployment logs
function getDeploymentLogs(appId, deploymentId, component = null) {
  try {
    let command = `doctl apps logs ${appId} --deployment ${deploymentId}`;
    if (component) {
      command += ` --component ${component}`;
    }
    
    const output = execSync(command, { encoding: 'utf8' });
    return output;
  } catch (error) {
    console.error(`${colors.red}Error fetching deployment logs: ${error.message}${colors.reset}`);
    return null;
  }
}

// Get components and their status
function getComponentStatus(appId) {
  try {
    const output = execSync(`doctl apps list-deployments ${appId} --format ID,Phase,CreatedAt --no-header | head -n 1`, { encoding: 'utf8' });
    const [deploymentId] = output.trim().split(/\s+/);
    
    const componentsOutput = execSync(`doctl apps get-deployment ${appId} ${deploymentId} --format "Components"`, { encoding: 'utf8' });
    
    // This is a bit crude, but it works for extracting component names and statuses
    const components = [];
    const regex = /Name:\s+(\w+)[\s\S]*?Status:\s+(\w+)/g;
    let match;
    
    while ((match = regex.exec(componentsOutput)) !== null) {
      components.push({
        name: match[1],
        status: match[2]
      });
    }
    
    return components;
  } catch (error) {
    console.error(`${colors.red}Error fetching component status: ${error.message}${colors.reset}`);
    return [];
  }
}

// Analyze build failures
function analyzeBuildFailure(logs) {
  const issues = [];
  
  // Check for pnpm installation issues
  if (logs.includes('EEXIST: file already exists') && logs.includes('pnpm')) {
    issues.push({
      issue: 'pnpm installation conflict',
      description: 'The buildpack already installs pnpm, but your build command is trying to install it again.',
      solution: 'Remove "npm install -g pnpm" from your build command. Use just "pnpm install && pnpm build" instead.'
    });
  }
  
  // Check for static directory issues
  if (logs.includes('Directory \'app/static\' does not exist')) {
    issues.push({
      issue: 'Missing static directory',
      description: 'The application is trying to access a static directory that doesn\'t exist in the deployed environment.',
      solution: 'Modify your main.py to create the directory with os.makedirs("app/static", exist_ok=True) or use a Dockerfile that creates it.'
    });
  }
  
  // Check for environment variable issues
  if (logs.includes('process.env') && logs.includes('undefined')) {
    issues.push({
      issue: 'Missing environment variables',
      description: 'Required environment variables are not defined in your app configuration.',
      solution: 'Check the environment variables defined in your .do/app.yaml and ensure they are correctly set in the DigitalOcean console.'
    });
  }
  
  // Check for dependency issues
  if (logs.includes('ModuleNotFoundError') || logs.includes('ImportError')) {
    issues.push({
      issue: 'Missing dependencies',
      description: 'Modules are missing or not correctly installed.',
      solution: 'Ensure all dependencies are listed in package.json and check for compatibility issues.'
    });
  }
  
  // Check for port configuration issues
  if (logs.includes('address already in use') || logs.includes('port is already in use')) {
    issues.push({
      issue: 'Port conflict',
      description: 'The application is trying to use a port that is already in use.',
      solution: 'Make sure your application uses the PORT environment variable (process.env.PORT).'
    });
  }
  
  return issues;
}

// Display app status with nice formatting
function displayAppStatus(app) {
  console.log('\n' + '='.repeat(60));
  console.log(`${colors.bright}${colors.blue}Allervie Dashboard Deployment Status${colors.reset}`);
  console.log('='.repeat(60) + '\n');
  
  console.log(`${colors.bright}App Details:${colors.reset}`);
  console.log(`  Name:      ${colors.green}${app.name}${colors.reset}`);
  console.log(`  ID:        ${app.id}`);
  console.log(`  URL:       ${colors.cyan}${app.url}${colors.reset}`);
  console.log(`  Phase:     ${getPhaseColor(app.deployment.phase)}${app.deployment.phase}${colors.reset}`);
  
  const progress = app.deployment.progress;
  const progressPercent = progress.total ? Math.round((progress.success / progress.total) * 100) : 0;
  
  console.log(`  Progress:  ${progressPercent}% (${progress.success}/${progress.total} steps)`);
  
  if (progress.error > 0) {
    console.log(`  ${colors.red}Errors:     ${progress.error} steps failed${colors.reset}`);
  }
  
  console.log('\n' + '-'.repeat(60));
}

// Get status color based on phase
function getPhaseColor(phase) {
  switch (phase) {
    case 'ACTIVE':
      return colors.green;
    case 'PENDING':
    case 'BUILDING':
    case 'DEPLOYING':
      return colors.yellow;
    case 'ERROR':
    case 'FAILED':
      return colors.red;
    default:
      return colors.reset;
  }
}

// Get status color based on component status
function getStatusColor(status) {
  switch (status) {
    case 'ACTIVE':
    case 'RUNNING':
    case 'DEPLOYED':
      return colors.green;
    case 'PENDING':
    case 'BUILDING':
    case 'DEPLOYING':
      return colors.yellow;
    case 'ERROR':
    case 'FAILED':
      return colors.red;
    default:
      return colors.reset;
  }
}

// Display components status
function displayComponentsStatus(components) {
  console.log(`${colors.bright}Components:${colors.reset}`);
  
  if (components.length === 0) {
    console.log(`  ${colors.yellow}No components found${colors.reset}`);
    return;
  }
  
  components.forEach(component => {
    console.log(`  ${component.name}: ${getStatusColor(component.status)}${component.status}${colors.reset}`);
  });
  
  console.log('\n' + '-'.repeat(60));
}

// Check health endpoint
async function checkHealthEndpoint(url) {
  try {
    console.log(`${colors.yellow}Checking health endpoint at https://${url}/api/health...${colors.reset}`);
    const response = execSync(`curl -s https://${url}/api/health`, { encoding: 'utf8' });
    
    try {
      const healthData = JSON.parse(response);
      console.log(`\n${colors.bright}Health Check Result:${colors.reset}`);
      console.log(`  Status:      ${healthData.status === 'healthy' ? colors.green + healthData.status : colors.yellow + healthData.status}${colors.reset}`);
      console.log(`  Environment: ${healthData.environment}`);
      console.log(`  Version:     ${healthData.version}`);
      console.log(`  Timestamp:   ${healthData.timestamp}`);
      
      if (healthData.config && healthData.config.missingVariables && healthData.config.missingVariables.length > 0) {
        console.log(`\n  ${colors.yellow}Missing Environment Variables:${colors.reset}`);
        healthData.config.missingVariables.forEach(variable => {
          console.log(`    - ${variable}`);
        });
      }
    } catch (error) {
      console.log(`\n${colors.yellow}Could not parse health check response as JSON:${colors.reset}`);
      console.log(`  ${response.substring(0, 100)}...`);
    }
  } catch (error) {
    console.error(`${colors.red}Health check failed: ${error.message}${colors.reset}`);
  }
  
  console.log('\n' + '-'.repeat(60));
}

// Check components and suggest fixes for issues
async function checkComponentsAndSuggestFixes(appId, components) {
  if (components.length === 0) return;
  
  const failedComponents = components.filter(c => 
    c.status === 'ERROR' || c.status === 'FAILED');
  
  if (failedComponents.length === 0) {
    console.log(`${colors.green}All components are running successfully.${colors.reset}`);
    return;
  }
  
  console.log(`${colors.bright}${colors.red}Failed Components Analysis:${colors.reset}\n`);
  
  for (const component of failedComponents) {
    console.log(`${colors.bright}Component: ${colors.red}${component.name}${colors.reset}`);
    
    // Get the deployment logs for this component
    const deploymentId = getAppDetails(appId).deployment.id;
    const logs = getDeploymentLogs(appId, deploymentId, component.name);
    
    if (!logs) {
      console.log(`  ${colors.yellow}Unable to fetch logs for this component${colors.reset}`);
      continue;
    }
    
    // Analyze build failures
    const issues = analyzeBuildFailure(logs);
    
    if (issues.length === 0) {
      console.log(`  ${colors.yellow}No specific issues identified. Check the logs manually.${colors.reset}`);
      console.log(`  Run: ${colors.cyan}doctl apps logs ${appId} --component ${component.name}${colors.reset}`);
    } else {
      issues.forEach(issue => {
        console.log(`  ${colors.red}Issue: ${issue.issue}${colors.reset}`);
        console.log(`  ${colors.dim}${issue.description}${colors.reset}`);
        console.log(`  ${colors.green}Solution: ${issue.solution}${colors.reset}\n`);
      });
    }
    
    // Always show a snippet of the logs
    console.log(`${colors.bright}Log Snippet:${colors.reset}`);
    
    // Get the last few lines of logs, focusing on errors
    const logLines = logs.split('\n');
    const errorLines = logLines.filter(line => 
      line.toLowerCase().includes('error') || 
      line.toLowerCase().includes('exception') ||
      line.toLowerCase().includes('failed')
    );
    
    if (errorLines.length > 0) {
      errorLines.slice(-10).forEach(line => {
        console.log(`  ${colors.red}${line}${colors.reset}`);
      });
    } else {
      logLines.slice(-10).forEach(line => {
        console.log(`  ${line}`);
      });
    }
    
    console.log('\n' + '-'.repeat(60));
  }
}

// Main function
async function main() {
  // Check prerequisites
  if (!checkDoctlInstalled() || !checkAuthenticated()) {
    return;
  }
  
  // Get App ID
  const appId = getAppId(process.argv);
  if (!appId) {
    return;
  }
  
  console.log(`${colors.cyan}Analyzing app with ID: ${appId}${colors.reset}`);
  
  // Get app details
  const app = getAppDetails(appId);
  if (!app) {
    return;
  }
  
  // Display app status
  displayAppStatus(app);
  
  // Get components status
  const components = getComponentStatus(appId);
  displayComponentsStatus(components);
  
  // Check health endpoint if app is active
  if (app.deployment.phase === 'ACTIVE' && app.url) {
    await checkHealthEndpoint(app.url);
  }
  
  // Check components and suggest fixes
  await checkComponentsAndSuggestFixes(appId, components);
  
  // Show monitoring options
  console.log(`${colors.bright}Monitoring Options:${colors.reset}`);
  console.log(`  1. View detailed logs:               ${colors.cyan}doctl apps logs ${appId}${colors.reset}`);
  console.log(`  2. Get component logs:               ${colors.cyan}doctl apps logs ${appId} --component [component-name]${colors.reset}`);
  console.log(`  3. View deployment details:          ${colors.cyan}doctl apps get-deployment ${appId} ${app.deployment.id}${colors.reset}`);
  console.log(`  4. Run this monitor again:           ${colors.cyan}node monitoring-script.js ${appId}${colors.reset}`);
  
  console.log('\n' + '='.repeat(60));
}

// Run the main function
main().catch(error => {
  console.error(`${colors.red}Unhandled error: ${error.message}${colors.reset}`);
});
