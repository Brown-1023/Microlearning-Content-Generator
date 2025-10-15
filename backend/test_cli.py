"""
Simple CLI script for local runs as per Milestone 1 requirements.
Tests the pipeline locally without starting the web server.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import pipeline
from pipeline import ContentPipeline
from validators import validate_content


def test_generation(content_type="MCQ", generator="gemini", num_questions=1):
    """Test the pipeline with sample input."""
    
    sample_text = """
    The cardiovascular system consists of the heart, blood vessels, and blood. 
    The heart is a muscular pump that circulates blood throughout the body. 
    Blood vessels include arteries, veins, and capillaries. 
    Arteries carry oxygenated blood away from the heart, while veins return 
    deoxygenated blood to the heart.
    """
    
    print("=" * 60)
    print("Testing Content Generation Pipeline")
    print("=" * 60)
    print(f"Content Type: {content_type}")
    print(f"Generator: {generator}")
    print(f"Questions: {num_questions}")
    print("-" * 60)
    
    # Initialize pipeline
    pipeline = ContentPipeline()
    
    # Run generation
    print("\nRunning pipeline...")
    result = pipeline.run(
        content_type=content_type,
        generator_model=generator,
        input_text=sample_text,
        num_questions=num_questions,
        focus_areas="anatomy and function"
    )
    
    # Display results
    if result.get("success"):
        print("[SUCCESS] Content generated and validated!")
        print(f"\nMetadata:")
        print(f"  - Model IDs: {result['metadata'].get('model_ids', {})}")
        print(f"  - Latencies: {result['metadata'].get('latencies', {})}")
        print(f"  - Total time: {result['metadata'].get('total_time', 0):.2f}s")
        print(f"  - Formatter retries: {result['metadata'].get('formatter_retries', 0)}")
        
        print(f"\nOutput (first 500 chars):")
        print("-" * 40)
        output = result.get("output", "")
        print(output[:500] + "..." if len(output) > 500 else output)
        
        # Save output
        output_file = f"test_output_{content_type.lower()}.txt"
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"\nFull output saved to: {output_file}")
        
    else:
        print("[FAILED] Generation failed!")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        
        if result.get("validation_errors"):
            print(f"\nValidation Errors ({len(result['validation_errors'])}):")
            for err in result['validation_errors'][:5]:
                print(f"  - Line {err.get('line', 'N/A')}: {err.get('message')}")
        
        if result.get("partial_output"):
            print("\nPartial output available (first 300 chars):")
            print("-" * 40)
            partial = result.get("partial_output", "")
            print(partial[:300] + "..." if len(partial) > 300 else partial)
    
    print("\n" + "=" * 60)
    return result.get("success", False)


def validate_file(file_path, content_type):
    """Validate an existing file."""
    print("=" * 60)
    print("Validating File")
    print("=" * 60)
    print(f"File: {file_path}")
    print(f"Type: {content_type}")
    print("-" * 60)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        is_valid, errors = validate_content(content, content_type)
        
        if is_valid:
            print("[VALID] File passes validation!")
        else:
            print(f"[INVALID] File has {len(errors)} validation errors:")
            for err in errors[:10]:
                print(f"  Line {err.line_number}: {err.message}")
        
        return is_valid
        
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Test the microlearning content generation pipeline locally"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate content')
    gen_parser.add_argument(
        '--type',
        choices=['MCQ', 'NMCQ'],
        default='MCQ',
        help='Content type to generate'
    )
    gen_parser.add_argument(
        '--model',
        choices=['claude', 'gemini'],
        default='claude',
        help='Generator model to use'
    )
    gen_parser.add_argument(
        '--questions',
        type=int,
        default=1,
        help='Number of questions to generate'
    )
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate a file')
    val_parser.add_argument('file', help='File to validate')
    val_parser.add_argument(
        '--type',
        choices=['MCQ', 'NMCQ'],
        required=True,
        help='Content type'
    )
    
    # Test command (run all tests)
    test_parser = subparsers.add_parser('test', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        success = test_generation(
            content_type=args.type,
            generator=args.model,
            num_questions=args.questions
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'validate':
        success = validate_file(args.file, args.type)
        sys.exit(0 if success else 1)
    
    elif args.command == 'test':
        print("Running all tests...")
        
        # Test MCQ generation
        mcq_success = test_generation("MCQ", "gemini", 1)
        
        print("\n" * 2)
        
        # Test NMCQ generation
        nmcq_success = test_generation("NMCQ", "gemini", 1)
        
        if mcq_success and nmcq_success:
            print("\n[SUCCESS] All tests passed!")
            sys.exit(0)
        else:
            print("\n[FAILED] Some tests failed!")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
