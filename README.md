# VisEval - Visual Evaluation Tool

VisEval is a tool for evaluating and comparing different AI models on visual analysis tasks using [Glimpse](https://github.com/u1i/glimpse).

## Overview

This project provides a structured way to run visual evaluation tests across multiple AI models. It uses YAML configuration files to define tests and models, making it easy to add new tests or models.

## Files

- `tests.yaml`: Contains test definitions with prompts and descriptions
- `models.yaml`: Contains model definitions with their OpenRouter identifiers
- `run_tests.py`: Python script to run tests with specified models
- `asean.jpg`: Sample image for testing (ASEAN countries infographic)
- `data.csv`: Ground truth data for the ASEAN countries infographic

## Example

The project includes a sample image (`asean.jpg`) which is an infographic of ASEAN countries with various statistics. The tests in `tests.yaml` are designed to evaluate how well different AI models can extract structured data from this infographic.

### Sample Data (data.csv)

```csv
Country,GDP,GDP_Per_Capita,Education_Spending_Pct,Military_Spending_Pct,Population
Brunei,$16B,$35.0K,4.4%,3.0%,460K
Cambodia,$50B,$2.9K,3.0%,2.1%,17.4M
Indonesia,$1.4T,$5.0K,1.3%,0.7%,284.4M
Laos,$16B,$2.1K,1.2%,0.2%,7.8M
Malaysia,$445B,$13.1K,3.6%,0.9%,33.9M
Myanmar,$65B,$1.2K,2.0%,3.8%,55.2M
Philippines,$498B,$4.4K,3.6%,1.2%,114.4M
Singapore,$565B,$92.9K,2.2%,2.7%,6.1M
Thailand,$546B,$7.8K,2.5%,1.2%,70.3M
Timor-Leste,$2B,$1.5K,3.0%,1.3%,1.4M
Vietnam,$491B,$4.8K,2.2%,1.8%,102.2M
```

The tests evaluate how accurately AI models can extract this data from the infographic and format it according to specific requirements.

## Requirements

- Python 3.x
- PyYAML
- [Glimpse](https://github.com/u1i/glimpse) - A tool for visual analysis using AI models

## Usage

### Run a specific test with a specific model:

```bash
./run_tests.py -m <model_name> -t <test_id>
```

Example:
```bash
./run_tests.py -m gemma3_27b -t 1
```

### Run a specific test with all models:

```bash
./run_tests.py -a -t <test_id>
```

Example:
```bash
./run_tests.py -a -t 1
```

### Save results to a structured log file:

```bash
./run_tests.py -m <model_name> -t <test_id> -o <output_file.json>
```

Example:
```bash
./run_tests.py -a -t 1 -o results.json
```

When using the `-o` option:
- The log file is created immediately when the script starts
- Results are appended to the log file as each model completes
- Temperature (hardcoded to 0.3) is included in the log data
- The log file is in JSON format with the following structure:

```json
{
  "timestamp": "2025-07-20T11:39:30.139921",
  "test_id": "3",
  "test_description": "CSV conversion with specific columns and alphabetical sorting",
  "prompt": "Turn this infographic into a CSV...",
  "temperature": 0.3,
  "results": [
    {
      "model_name": "model1",
      "model_id": "provider/model-name",
      "temperature": 0.3,
      "success": true,
      "result": "...output..."
    },
    ...
  ]
}
```

## Adding New Tests

Add new tests to `tests.yaml` following the existing format:

```yaml
tests:
  - prompt: "Your test prompt here"
    description: "Description of what the test does"
```

## Adding New Models

Add new models to `models.yaml` following the existing format:

```yaml
models:
  - name: model_name_without_spaces_or_slashes
    openrouter_model: provider/model-name
```

## Credits

This project uses [Glimpse](https://github.com/u1i/glimpse), a tool for visual analysis using AI models.
