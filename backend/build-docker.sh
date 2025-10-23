#!/bin/bash

# Docker Build Script for Microlearning Backend
# Supports multiple build configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BUILD_TYPE="development"
IMAGE_NAME="microlearning-backend"
TAG="latest"
DOCKERFILE="Dockerfile"
PUSH_TO_REGISTRY=false
REGISTRY=""

# Function to print colored output
print_info() { echo -e "${BLUE}ℹ ${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# Show usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -t, --type TYPE        Build type: development|production|test (default: development)
    -n, --name NAME        Image name (default: microlearning-backend)
    -v, --version VERSION  Image tag/version (default: latest)
    -p, --push            Push to registry after build
    -r, --registry REG    Registry URL (e.g., gcr.io/project-id)
    -h, --help            Show this help message

Examples:
    $0                                    # Build development image
    $0 --type production --version 1.0.0  # Build production v1.0.0
    $0 -t production -p -r gcr.io/myproject  # Build and push to GCR
EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -v|--version)
            TAG="$2"
            shift 2
            ;;
        -p|--push)
            PUSH_TO_REGISTRY=true
            shift
            ;;
        -r|--registry)
            REGISTRY="$2"
            PUSH_TO_REGISTRY=true
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Set Dockerfile based on build type
case $BUILD_TYPE in
    development|dev)
        DOCKERFILE="Dockerfile"
        print_info "Building DEVELOPMENT image"
        ;;
    production|prod)
        DOCKERFILE="Dockerfile.production"
        print_info "Building PRODUCTION image (optimized, secure)"
        ;;
    test)
        DOCKERFILE="Dockerfile"
        TAG="test"
        print_info "Building TEST image"
        ;;
    *)
        print_error "Invalid build type: $BUILD_TYPE"
        usage
        ;;
esac

# Check if Dockerfile exists
if [ ! -f "$DOCKERFILE" ]; then
    print_error "Dockerfile not found: $DOCKERFILE"
    exit 1
fi

# Check if .env file exists for development builds
if [ "$BUILD_TYPE" = "development" ] && [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        print_success "Created .env file. Please update with your API keys."
    fi
fi

# Build image
print_info "Building Docker image..."
print_info "Image: ${IMAGE_NAME}:${TAG}"
print_info "Dockerfile: ${DOCKERFILE}"

docker build \
    -t "${IMAGE_NAME}:${TAG}" \
    -f "${DOCKERFILE}" \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VERSION="${TAG}" \
    .

if [ $? -eq 0 ]; then
    print_success "Build successful!"
    
    # Show image info
    echo ""
    print_info "Image details:"
    docker images "${IMAGE_NAME}:${TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
else
    print_error "Build failed!"
    exit 1
fi

# Push to registry if requested
if [ "$PUSH_TO_REGISTRY" = true ]; then
    if [ -z "$REGISTRY" ]; then
        print_error "Registry URL not specified. Use -r option."
        exit 1
    fi
    
    print_info "Tagging image for registry..."
    FULL_TAG="${REGISTRY}/${IMAGE_NAME}:${TAG}"
    docker tag "${IMAGE_NAME}:${TAG}" "${FULL_TAG}"
    
    print_info "Pushing to registry: ${FULL_TAG}"
    docker push "${FULL_TAG}"
    
    if [ $? -eq 0 ]; then
        print_success "Push successful!"
    else
        print_error "Push failed!"
        exit 1
    fi
fi

# Provide run instructions
echo ""
print_success "Build complete!"
echo ""
echo "To run the container:"
echo ""
if [ "$BUILD_TYPE" = "production" ]; then
    echo "  docker run -d \\"
    echo "    --name ${IMAGE_NAME} \\"
    echo "    -p 4000:4000 \\"
    echo "    --env-file .env \\"
    echo "    --memory='1g' \\"
    echo "    --cpus='1.0' \\"
    echo "    --restart unless-stopped \\"
    echo "    ${IMAGE_NAME}:${TAG}"
else
    echo "  docker run -d \\"
    echo "    --name ${IMAGE_NAME}-dev \\"
    echo "    -p 4000:4000 \\"
    echo "    --env-file .env \\"
    echo "    -v \$(pwd):/app \\"
    echo "    ${IMAGE_NAME}:${TAG}"
fi
echo ""
echo "Or use: docker-compose up"
