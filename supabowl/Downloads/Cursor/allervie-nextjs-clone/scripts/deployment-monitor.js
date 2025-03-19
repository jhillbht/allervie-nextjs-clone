#!/usr/bin/env node
/**
 * Allervie Dashboard Deployment Monitor
 * 
 * This script monitors the status of a DigitalOcean App Platform deployment
 * and provides detailed diagnostics.
 * 
 * Usage:
 *   node deployment-monitor.js [APP_ID]
 */

const { execSync } = require('child_process');

// Terminal colors for better output
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
  white: '\x1b[37m',
};

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

// Get the App ID, either from arguments or by listing apps
function getAppId(args) {
  if (args.length > 2) {
    return args[2];
  }
  
  try {
    console.log(`${colors.cyan}No App ID provided. Fetching most recent app...${colors.reset}`);
    const output = execSync('doctl apps list --format ID --no-header', { encoding: 'utf8' });
    const appIds = output.trim().split('\n');
    
    if (appIds.length === 0 || !appIds[0]) {
      console.error(`${colors.red}No apps found in your account.${colors.reset}`);
      return null;
    }
    
    return appIds[0];
  } catch (error) {
    console.error(`${colors.red}Error fetching apps: ${error.message}${colors.reset}`);
    return null;
  }
}

// Get app details
function getAppDetails(appId) {
  try {
    const output = execSync(`doctl apps get ${appId} -o json`, { encoding: 'utf8' });
    const appData = JSON.parse(output)[0];
    
    return {
      id: appData.id,
      name: appData.spec.name,
      url: appData.default_ingress,
      activeDeployment: appData.active_deployment ? {
        id: appData.active_deployment.id,
        phase: appData.active_deployment.phase
      } : null,
      inProgressDeployment: appData.in_progress_deployment ? {
        id: appData.in_progress_deployment.id,
        phase: appData.in_progress_deployment.phase
      } : null,
      services: appData.spec.services || []
    };
  } catch (error) {
    console.error(`${colors.red}Error fetching app details: ${error.message}${colors.reset}`);
    return null;
  }
}

// Get all deployments for an app
function listDeployments(appId) {
  try {
    const output = execSync(`doctl apps list-deployments ${appId} --format ID,Phase,Cause --no-header`, { encoding: 'utf8' });
    return output.trim().split('\n').map(line => {
      const [id, phase, ...causeParts] = line.trim().split(/\s+/);
      return {
        id,
        phase,
        cause: causeParts.join(' ')
      };
    });
  } catch (error) {
    console.error(`${colors.red}Error listing deployments: ${error.message}${colors.reset}`);
    return [];
  }
}

// Get detailed deployment information
function getDeploymentDetails(appId, deploymentId) {
  try {
    const output = execSync(`doctl apps get-deployment ${appId} ${deploymentId} -o json`, { encoding: 'utf8' });
    return JSON.parse(output)[0];
  } catch (error) {
    console.error(`${colors.red}Error fetching deployment details: ${error.message}${colors.reset}`);
    return null;
  }
}

// Get logs for a component
function getComponentLogs(appId, componentName, deploymentId = null) {
  try {
    let command = `doctl apps logs ${appId} ${componentName}`;
    if (deploymentId) {
      command += ` --deployment ${deploymentId}`;
    }
    command += ` --follow false`;
    
    return execSync(command, { encoding: 'utf8' });
  } catch (error) {
    return `Error fetching logs: ${error.message}`;
  }
}

// Analyze common deployment issues
function analyzeDeploymentIssues(deploymentData) {
  const issues = [];
  
  // Check for errors in steps
  if (deploymentData && deploymentData.progress && deploymentData.progress.steps) {
    // Look for error steps
    deploymentData.progress.steps.forEach(step => {
      if (step.status === 'ERROR') {
        if (step.reason) {
          issues.push({
            type: 'step_error',
            step: step.name,
            code: step.reason.code,
            message: step.reason.message
          });
        }
        
        // Check nested steps
        if (step.steps) {
          step.steps.forEach(subStep => {
            if (subStep.status === 'ERROR') {
              if (subStep.reason) {
                issues.push({
                  type: 'sub_step_error',
                  step: `${step.name}.${subStep.name}`,
                  component: subStep.component_name,
                  code: subStep.reason.code,
                  message: subStep.reason.message
                });
              }
              
              // Check further nested steps
              if (subStep.steps) {
                subStep.steps.forEach(nestedStep => {
                  if (nestedStep.status === 'ERROR' && nestedStep.reason) {
                    issues.push({
                      type: 'nested_step_error',
                      step: `${step.name}.${subStep.name}.${nestedStep.name}`,
                      component: nestedStep.component_name,
                      code: nestedStep.reason.code,
                      message: nestedStep.reason.message
                    });
                  }
                });
              }
            }
          });
        }
      }
    });
  }
  
  return issues;
}

// Display app information
function displayAppInfo(app) {
  console.log(`\n${colors.bright}${colors.blue}Allervie Dashboard Deployment Status${colors.reset}`);
  console.log('='.repeat(60));
  
  console.log(`\n${colors.bright}App Information:${colors.reset}`);
  console.log(`  Name:        ${colors.green}${app.name}${colors.reset}`);
  console.log(`  App ID:      ${app.id}`);
  console.log(`  URL:         ${colors.cyan}${app.url}${colors.reset}`);
  
  if (app.activeDeployment) {
    console.log(`  Active Deployment: ${getStatusColor(app.activeDeployment.phase)}${app.activeDeployment.phase}${colors.reset} (ID: ${app.activeDeployment.id})`);
  } else {
    console.log(`  Active Deployment: ${colors.yellow}None${colors.reset}`);
  }
  
  if (app.inProgressDeployment) {
    console.log(`  In-Progress Deployment: ${getStatusColor(app.inProgressDeployment.phase)}${app.inProgressDeployment.phase}${colors.reset} (ID: ${app.inProgressDeployment.id})`);
  }
  
  console.log(`\n${colors.bright}Services:${colors.reset}`);
  
  app.services.forEach(service => {
    console.log(`  - ${service.name}`);
    console.log(`    GitHub: ${service.github ? service.github.repo : 'N/A'}`);
    console.log(`    HTTP Port: ${service.http_port}`);
    if (service.dockerfile_path) {
      console.log(`    Dockerfile: ${service.dockerfile_path}`);
    }
    if (service.build_command) {
      console.log(`    Build Command: ${service.build_command}`);
    }
    console.log();
  });
  
  console.log('-'.repeat(60));
}

// Display deployment details
function displayDeploymentDetails(deployment) {
  if (!deployment) {
    console.log(`${colors.yellow}No deployment data available.${colors.reset}`);
    return;
  }
  
  console.log(`\n${colors.bright}Deployment Details:${colors.reset}`);
  console.log(`  ID:       ${deployment.id}`);
  console.log(`  Phase:    ${getStatusColor(deployment.phase)}${deployment.phase}${colors.reset}`);
  console.log(`  Cause:    ${deployment.cause}`);
  console.log(`  Created:  ${deployment.created_at}`);
  console.log(`  Updated:  ${deployment.updated_at}`);
  
  if (deployment.progress) {
    const progress = deployment.progress;
    const total = progress.total_steps || 0;
    const success = progress.success_steps || 0;
    const errors = progress.error_steps || 0;
    const pending = progress.pending_steps || 0;
    const running = progress.running_steps || 0;
    
    const completedPercent = total > 0 ? Math.round((success / total) * 100) : 0;
    
    console.log(`\n${colors.bright}Deployment Progress:${colors.reset}`);
    console.log(`  ${completedPercent}% Complete (${success}/${total} steps)`);
    
    if (errors > 0) {
      console.log(`  ${colors.red}Errors: ${errors} steps failed${colors.reset}`);
    }
    
    if (pending > 0) {
      console.log(`  ${colors.yellow}Pending: ${pending} steps waiting${colors.reset}`);
    }
    
    if (running > 0) {
      console.log(`  ${colors.cyan}Running: ${running} steps in progress${colors.reset}`);
    }
  }
  
  console.log('-'.repeat(60));
}

// Display deployment issues
function displayDeploymentIssues(issues) {
  if (issues.length === 0) {
    console.log(`${colors.green}No issues detected with this deployment.${colors.reset}`);
    return;
  }
  
  console.log(`\n${colors.bright}${colors.red}Deployment Issues (${issues.length}):${colors.reset}`);
  
  issues.forEach((issue, index) => {
    console.log(`\n${colors.bright}Issue #${index + 1}:${colors.reset}`);
    console.log(`  Step:      ${issue.step}`);
    if (issue.component) {
      console.log(`  Component: ${issue.component}`);
    }
    console.log(`  Error:     ${colors.red}${issue.code}${colors.reset}`);
    console.log(`  Message:   ${colors.red}${issue.message}${colors.reset}`);
    
    // Suggest fixes based on error code
    console.log(`\n  ${colors.bright}Suggested Fix:${colors.reset}`);
    
    switch (issue.code) {
      case 'DeployContainerExitNonZero':
        console.log(`  ${colors.green}Your container exited unexpectedly. This often means there's an issue with your run command or environment variables.${colors.reset}`);
        console.log(`  - Check if the application is configured to listen on the correct PORT`);
        console.log(`  - Verify that all required environment variables are set`);
        console.log(`  - Try simplifying your run command to debug the issue`);
        console.log(`  - For Next.js apps, ensure you're using a standard npm start command`);
        break;
        
      case 'BuildpackBuildFailed':
        console.log(`  ${colors.green}Your build process failed. Common causes include:${colors.reset}`);
        console.log(`  - Incompatible package manager commands (try using npm instead of pnpm/yarn)`);
        console.log(`  - Missing dependencies or incorrect build scripts in package.json`);
        console.log(`  - Environment variables not available during build time`);
        console.log(`  - Node.js version compatibility issues`);
        break;
        
      case 'PreviousBuildReused':
        console.log(`  ${colors.green}This is usually not an error. The previous build artifact was reused for efficiency.${colors.reset}`);
        break;
        
      default:
        console.log(`  ${colors.green}This is an uncommon error. Check the DigitalOcean logs for more details.${colors.reset}`);
        console.log(`  - You can view detailed logs with: doctl apps logs ${issue.component}`);
    }
  });
  
  console.log('-'.repeat(60));
}

// Get status color based on phase
function getStatusColor(phase) {
  switch (phase) {
    case 'ACTIVE':
    case 'SUCCESS':
      return colors.green;
    case 'PENDING':
    case 'BUILDING':
    case 'DEPLOYING':
    case 'RUNNING':
      return colors.yellow;
    case 'ERROR':
    case 'FAILED':
      return colors.red;
    default:
      return colors.reset;
  }
}

// Suggestions based on deployment state
function suggestActions(app, deploymentIssues) {
  console.log(`\n${colors.bright}${colors.blue}Suggested Actions:${colors.reset}`);
  
  if (app.inProgressDeployment) {
    console.log(`  ${colors.yellow}Deployment is still in progress. Wait for it to complete.${colors.reset}`);
    console.log(`  Monitor with: doctl apps get-deployment ${app.id} ${app.inProgressDeployment.id}`);
    return;
  }
  
  if (deploymentIssues.length > 0) {
    console.log(`  1. Fix the identified issues in your application configuration`);
    console.log(`  2. Update your app.yaml file with the necessary changes`);
    console.log(`  3. Update the app with: doctl apps update ${app.id} --spec .do/app.yaml`);
    console.log(`  4. Create a new deployment: doctl apps create-deployment ${app.id}`);
    
    // Specific suggestions based on issue types
    const containerIssues = deploymentIssues.filter(i => i.code === 'DeployContainerExitNonZero');
    const buildIssues = deploymentIssues.filter(i => i.code === 'BuildpackBuildFailed');
    
    if (containerIssues.length > 0) {
      console.log(`\n  ${colors.bright}For container exit issues:${colors.reset}`);
      console.log(`  - Try changing the build command from pnpm to npm in app.yaml`);
      console.log(`  - Update run_command to: npm start`);
      console.log(`  - Verify the next.config.js port configuration matches app.yaml`);
    }
    
    if (buildIssues.length > 0) {
      console.log(`\n  ${colors.bright}For build failures:${colors.reset}`);
      console.log(`  - Consider simplifying your build approach`);
      console.log(`  - Ensure build-time environment variables are properly set`);
      console.log(`  - Check that your package.json has the correct build script`);
    }
  } else {
    console.log(`  ${colors.green}No issues detected. Your deployment appears to be healthy.${colors.reset}`);
    console.log(`  You can visit your application at: ${app.url}`);
  }
  
  console.log(`\n  ${colors.bright}Useful commands:${colors.reset}`);
  console.log(`  View logs: doctl apps logs ${app.id}`);
  console.log(`  Component logs: doctl apps logs ${app.id} [component-name]`);
  console.log(`  Update app: doctl apps update ${app.id} --spec .do/app.yaml`);
  console.log(`  Create deployment: doctl apps create-deployment ${app.id}`);
  
  console.log('-'.repeat(60));
}

// Main function
async function main() {
  console.log(`${colors.bright}${colors.blue}Allervie Dashboard Deployment Monitor${colors.reset}`);
  console.log(`Starting monitoring process...`);
  
  // Check prerequisites
  if (!checkDoctlInstalled() || !checkAuthenticated()) {
    return;
  }
  
  // Get App ID
  const appId = getAppId(process.argv);
  if (!appId) {
    return;
  }
  
  console.log(`${colors.cyan}Monitoring app with ID: ${appId}${colors.reset}`);
  
  // Get app details
  const app = getAppDetails(appId);
  if (!app) {
    return;
  }
  
  // Display app information
  displayAppInfo(app);
  
  // Get deployment details
  let deploymentId = app.inProgressDeployment ? app.inProgressDeployment.id : 
                    (app.activeDeployment ? app.activeDeployment.id : null);
                    
  if (!deploymentId) {
    const deployments = listDeployments(appId);
    if (deployments.length > 0) {
      deploymentId = deployments[0].id;
    }
  }
  
  if (deploymentId) {
    const deployment = getDeploymentDetails(appId, deploymentId);
    
    if (deployment) {
      displayDeploymentDetails(deployment);
      
      // Analyze deployment issues
      const issues = analyzeDeploymentIssues(deployment);
      displayDeploymentIssues(issues);
      
      // Suggest actions
      suggestActions(app, issues);
    }
  } else {
    console.log(`${colors.yellow}No deployments found for this app.${colors.reset}`);
  }
  
  console.log(`\n${colors.bright}${colors.blue}Monitoring complete.${colors.reset}`);
}

// Run the main function
main().catch(error => {
  console.error(`${colors.red}An unexpected error occurred: ${error.message}${colors.reset}`);
});
