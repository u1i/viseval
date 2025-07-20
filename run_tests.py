#!/usr/bin/env python3
"""
Script to run Glimpse tests using models and tests defined in YAML files.
"""

import argparse
import subprocess
import sys
import yaml
import os
import json
import datetime

def load_yaml(file_path):
    """Load YAML file and return its contents."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def get_model_by_name(models_data, model_name):
    """Find a model by its name in the models data."""
    for model in models_data['models']:
        if model['name'] == model_name:
            return model
    return None

def get_test_by_id(tests_data, test_id):
    """Get a test by its ID (1-based index) in the tests data."""
    try:
        # Convert test_id to 0-based index
        index = int(test_id) - 1
        if index < 0 or index >= len(tests_data['tests']):
            print(f"Error: Test ID {test_id} is out of range. Available tests: 1-{len(tests_data['tests'])}")
            sys.exit(1)
        return tests_data['tests'][index]
    except ValueError:
        print(f"Error: Test ID must be a number")
        sys.exit(1)

def run_glimpse(model_openrouter, prompt, temperature=0.3):
    """Run Glimpse with the specified model, prompt, and temperature."""
    # Assuming asean.jpg is the image file to analyze
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asean.jpg")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        sys.exit(1)
    
    cmd = [
        "glimpse.py",
        image_path,
        "-m", model_openrouter,
        "-t", str(temperature),
        "-p", prompt
    ]
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running Glimpse: {result.stderr}")
            sys.exit(1)
        return result.stdout
    except Exception as e:
        print(f"Error executing Glimpse: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Run Glimpse tests with specified models.')
    parser.add_argument('-m', '--model', help='Model name from models.yaml')
    parser.add_argument('-t', '--test', help='Test ID from tests.yaml (1-based)')
    parser.add_argument('-a', '--all-models', action='store_true', help='Run the specified test with all models')
    parser.add_argument('-o', '--output', help='Output file path for structured log (JSON format)')
    args = parser.parse_args()
    
    # If no arguments provided, exit without doing anything
    if not args.test or (not args.model and not args.all_models):
        parser.print_help()
        sys.exit(0)
    
    # Load YAML files
    models_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.yaml")
    tests_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests.yaml")
    
    models_data = load_yaml(models_file)
    tests_data = load_yaml(tests_file)
    
    # Get test
    test = get_test_by_id(tests_data, args.test)
    
    # Initialize log data structure if output file is specified
    if args.output:
        # Create initial log data structure
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "test_id": args.test,
            "test_description": test['description'],
            "prompt": test['prompt'],
            "temperature": 0.3,  # Hardcoded temperature value
            "results": []
        }
        
        # Create log file immediately with initial structure
        try:
            with open(args.output, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"Created log file: {args.output}")
        except Exception as e:
            print(f"Error creating log file {args.output}: {e}")
            sys.exit(1)
    
    if args.all_models:
        # Run the test with all models
        print(f"Running test {args.test} with all models")
        print(f"Test description: {test['description']}")
        print(f"Prompt: {test['prompt']}")
        print("\n" + "-"*80)
        
        for model in models_data['models']:
            print(f"\nRunning with model: {model['name']} ({model['openrouter_model']})")
            
            try:
                # Run Glimpse
                result = run_glimpse(model['openrouter_model'], test['prompt'])
                
                # Print result
                print("\nResult:")
                print(result)
                
                # Add to log data and append to file if output file is specified
                if args.output:
                    result_entry = {
                        "model_name": model['name'],
                        "model_id": model['openrouter_model'],
                        "temperature": 0.3,  # Hardcoded temperature value
                        "success": True,
                        "result": result
                    }
                    
                    # Append to the log file
                    try:
                        # Read existing data
                        with open(args.output, 'r') as f:
                            log_data = json.load(f)
                        
                        # Append new result
                        log_data["results"].append(result_entry)
                        
                        # Write updated data back
                        with open(args.output, 'w') as f:
                            json.dump(log_data, f, indent=2)
                            
                        print(f"Appended result for {model['name']} to log file")
                    except Exception as e:
                        print(f"Error updating log file with result for {model['name']}: {e}")
            except Exception as e:
                error_msg = str(e)
                print(f"Error with model {model['name']}: {error_msg}")
                
                # Add error to log data and append to file if output file is specified
                if args.output:
                    error_entry = {
                        "model_name": model['name'],
                        "model_id": model['openrouter_model'],
                        "temperature": 0.3,  # Hardcoded temperature value
                        "success": False,
                        "error": error_msg
                    }
                    
                    # Append to the log file
                    try:
                        # Read existing data
                        with open(args.output, 'r') as f:
                            log_data = json.load(f)
                        
                        # Append new error
                        log_data["results"].append(error_entry)
                        
                        # Write updated data back
                        with open(args.output, 'w') as f:
                            json.dump(log_data, f, indent=2)
                            
                        print(f"Appended error for {model['name']} to log file")
                    except Exception as e:
                        print(f"Error updating log file with error for {model['name']}: {e}")
            
            print("\n" + "-"*80)
    else:
        # Get model
        model = get_model_by_name(models_data, args.model)
        if not model:
            print(f"Error: Model '{args.model}' not found in models.yaml")
            sys.exit(1)
        
        # Print info
        print(f"Running test {args.test} with model {args.model}")
        print(f"Model: {model['openrouter_model']}")
        print(f"Test description: {test['description']}")
        print(f"Prompt: {test['prompt']}")
        
        try:
            # Run Glimpse
            result = run_glimpse(model['openrouter_model'], test['prompt'])
            
            # Print result
            print("\nResult:")
            print(result)
            
            # Add to log data and append to file if output file is specified
            if args.output:
                result_entry = {
                    "model_name": model['name'],
                    "model_id": model['openrouter_model'],
                    "temperature": 0.3,  # Hardcoded temperature value
                    "success": True,
                    "result": result
                }
                
                # Append to the log file
                try:
                    # Read existing data
                    with open(args.output, 'r') as f:
                        log_data = json.load(f)
                    
                    # Append new result
                    log_data["results"].append(result_entry)
                    
                    # Write updated data back
                    with open(args.output, 'w') as f:
                        json.dump(log_data, f, indent=2)
                        
                    print(f"Appended result for {model['name']} to log file")
                except Exception as e:
                    print(f"Error updating log file with result for {model['name']}: {e}")
        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            
            # Add error to log data and append to file if output file is specified
            if args.output:
                error_entry = {
                    "model_name": model['name'],
                    "model_id": model['openrouter_model'],
                    "temperature": 0.3,  # Hardcoded temperature value
                    "success": False,
                    "error": error_msg
                }
                
                # Append to the log file
                try:
                    # Read existing data
                    with open(args.output, 'r') as f:
                        log_data = json.load(f)
                    
                    # Append new error
                    log_data["results"].append(error_entry)
                    
                    # Write updated data back
                    with open(args.output, 'w') as f:
                        json.dump(log_data, f, indent=2)
                        
                    print(f"Appended error for {model['name']} to log file")
                except Exception as e:
                    print(f"Error updating log file with error for {model['name']}: {e}")
    
    # No need to write log data at the end since we're appending as we go
    if args.output:
        print(f"\nAll results have been written to {args.output}")

if __name__ == "__main__":
    main()
