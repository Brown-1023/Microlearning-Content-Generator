# Docker Build Script for Microlearning Backend (Windows PowerShell)
# Supports multiple build configurations

param(
    [Parameter(HelpMessage="Build type: development|production|test")]
    [ValidateSet("development", "dev", "production", "prod", "test")]
    [string]$Type = "development",
    
    [Parameter(HelpMessage="Image name")]
    [string]$Name = "microlearning-backend",
    
    [Parameter(HelpMessage="Image tag/version")]
    [string]$Version = "latest",
    
    [Parameter(HelpMessage="Push to registry after build")]
    [switch]$Push,
    
    [Parameter(HelpMessage="Registry URL (e.g., gcr.io/project-id)")]
    [string]$Registry = "",
    
    [Parameter(HelpMessage="Show help")]
    [switch]$Help
)

# Color functions
function Write-Info { Write-Host "ℹ  $args" -ForegroundColor Blue }
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }

# Show usage
if ($Help) {
    Write-Host @"
Docker Build Script for Microlearning Backend

Usage: .\build-docker.ps1 [OPTIONS]

Options:
    -Type TYPE        Build type: development|production|test (default: development)
    -Name NAME        Image name (default: microlearning-backend)  
    -Version VERSION  Image tag/version (default: latest)
    -Push            Push to registry after build
    -Registry REG    Registry URL (e.g., gcr.io/project-id)
    -Help            Show this help message

Examples:
    .\build-docker.ps1                                    # Build development image
    .\build-docker.ps1 -Type production -Version 1.0.0    # Build production v1.0.0
    .\build-docker.ps1 -Type production -Push -Registry gcr.io/myproject  # Build and push
"@
    exit 0
}

# Normalize build type
$BuildType = switch ($Type) {
    { $_ -in "development", "dev" } { "development"; break }
    { $_ -in "production", "prod" } { "production"; break }
    "test" { "test"; break }
    default { "development" }
}

# Set Dockerfile based on build type
$Dockerfile = switch ($BuildType) {
    "development" {
        Write-Info "Building DEVELOPMENT image"
        "Dockerfile"
    }
    "production" {
        Write-Info "Building PRODUCTION image (optimized, secure)"
        "Dockerfile.production"
    }
    "test" {
        Write-Info "Building TEST image"
        $Version = "test"
        "Dockerfile"
    }
}

# Check if Dockerfile exists
if (-not (Test-Path $Dockerfile)) {
    Write-Error "Dockerfile not found: $Dockerfile"
    exit 1
}

# Check if .env file exists for development builds
if ($BuildType -eq "development" -and -not (Test-Path ".env")) {
    Write-Warning ".env file not found. Creating from template..."
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Success "Created .env file. Please update with your API keys."
    }
}

# Build image
Write-Info "Building Docker image..."
Write-Info "Image: ${Name}:${Version}"
Write-Info "Dockerfile: ${Dockerfile}"

$buildDate = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$buildArgs = @(
    "build",
    "-t", "${Name}:${Version}",
    "-f", $Dockerfile,
    "--build-arg", "BUILD_DATE=$buildDate",
    "--build-arg", "VERSION=$Version",
    "."
)

$buildProcess = Start-Process -FilePath "docker" -ArgumentList $buildArgs -PassThru -Wait -NoNewWindow
if ($buildProcess.ExitCode -eq 0) {
    Write-Success "Build successful!"
    
    # Show image info
    Write-Host ""
    Write-Info "Image details:"
    docker images "${Name}:${Version}" --format "table {{.Repository}}`t{{.Tag}}`t{{.Size}}`t{{.CreatedAt}}"
} else {
    Write-Error "Build failed!"
    exit 1
}

# Push to registry if requested
if ($Push) {
    if ([string]::IsNullOrWhiteSpace($Registry)) {
        Write-Error "Registry URL not specified. Use -Registry option."
        exit 1
    }
    
    Write-Info "Tagging image for registry..."
    $FullTag = "${Registry}/${Name}:${Version}"
    docker tag "${Name}:${Version}" $FullTag
    
    Write-Info "Pushing to registry: ${FullTag}"
    docker push $FullTag
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Push successful!"
    } else {
        Write-Error "Push failed!"
        exit 1
    }
}

# Provide run instructions
Write-Host ""
Write-Success "Build complete!"
Write-Host ""
Write-Host "To run the container:"
Write-Host ""

if ($BuildType -eq "production") {
    Write-Host @"
  docker run -d ``
    --name $Name ``
    -p 4000:4000 ``
    --env-file .env ``
    --memory='1g' ``
    --cpus='1.0' ``
    --restart unless-stopped ``
    ${Name}:${Version}
"@
} else {
    Write-Host @"
  docker run -d ``
    --name $Name-dev ``
    -p 4000:4000 ``
    --env-file .env ``
    -v ${PWD}:/app ``
    ${Name}:${Version}
"@
}

Write-Host ""
Write-Host "Or use: docker-compose up"
