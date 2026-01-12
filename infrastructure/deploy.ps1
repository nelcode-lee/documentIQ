# PowerShell script to deploy Azure resources using Bicep
# Usage: .\deploy.ps1 -ResourceGroupName "rg-rag-system" -Location "uksouth"

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "uksouth",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$ApplicationName = "rag-system"
)

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed. Please install it from https://aka.ms/installazurecliwindows"
    exit 1
}

# Check if logged in to Azure
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in to Azure. Please run 'az login'"
    exit 1
}

Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green

# Create resource group if it doesn't exist
$rgExists = az group exists --name $ResourceGroupName | ConvertFrom-Json
if (-not $rgExists) {
    Write-Host "Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
    az group create --name $ResourceGroupName --location $Location
} else {
    Write-Host "Resource group already exists: $ResourceGroupName" -ForegroundColor Green
}

# Deploy Bicep template
Write-Host "Deploying Bicep template..." -ForegroundColor Yellow
$deploymentName = "deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file "main.bicep" `
    --parameters "azuredeploy.parameters.json" `
    --parameters applicationName=$ApplicationName location=$Location environment=$Environment `
    --name $deploymentName

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "Getting deployment outputs..." -ForegroundColor Yellow
    
    $outputs = az deployment group show `
        --resource-group $ResourceGroupName `
        --name $deploymentName `
        --query "properties.outputs" | ConvertFrom-Json
    
    Write-Host "`n=== Deployment Outputs ===" -ForegroundColor Cyan
    Write-Host "OpenAI Endpoint: $($outputs.openAiEndpoint.value)" -ForegroundColor White
    Write-Host "Search Endpoint: $($outputs.searchEndpoint.value)" -ForegroundColor White
    Write-Host "Storage Account: $($outputs.storageAccountName.value)" -ForegroundColor White
    
    Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Get OpenAI API keys:" -ForegroundColor Yellow
    Write-Host "   az cognitiveservices account keys list --name $($outputs.openAiAccountName.value) --resource-group $ResourceGroupName" -ForegroundColor Gray
    
    Write-Host "`n2. Get Search API keys:" -ForegroundColor Yellow
    Write-Host "   az search admin-key show --service-name $($outputs.searchServiceName.value) --resource-group $ResourceGroupName" -ForegroundColor Gray
    
    Write-Host "`n3. Update your .env files with these values" -ForegroundColor Yellow
} else {
    Write-Error "Deployment failed!"
    exit 1
}
