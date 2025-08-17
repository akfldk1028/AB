# Test Suite for Claude CLI Multi-Agent A2A System

## Overview

This test suite provides comprehensive testing for the Claude CLI Multi-Agent A2A System, covering unit tests, integration tests, A2A protocol compliance, and performance testing.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_agents.py             # Unit tests for individual agents
├── test_task_manager.py       # Unit tests for task manager
├── test_a2a_protocol.py       # A2A protocol compliance tests
├── test_integration.py        # Integration and end-to-end tests
├── requirements.txt           # Test dependencies
└── README.md                  # This file
```

## Test Categories

### 1. Unit Tests (`test_agents.py`, `test_task_manager.py`)

Test individual components in isolation:

- **Agent Tests**: Test Claude CLI agent functionality
  - Initialization and configuration
  - Claude CLI subprocess execution
  - Error handling (timeouts, failures, file not found)
  - Response processing and formatting
  - Streaming capabilities

- **Task Manager Tests**: Test task management functionality
  - Task creation and validation
  - A2A message processing
  - Push notifications
  - Error handling and state management

### 2. A2A Protocol Tests (`test_a2a_protocol.py`)

Test compliance with A2A (Agent-to-Agent) protocol:

- Message structure validation
- Request/response format compliance
- JSON serialization/deserialization
- Error handling and validation
- Multi-part message support

### 3. Integration Tests (`test_integration.py`)

Test system-wide functionality:

- End-to-end A2A message flows
- Multi-agent coordination scenarios
- Error handling across components
- Performance under concurrent load
- Data integrity and consistency

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type a2a
```

### Advanced Usage

```bash
# Run with coverage report
python run_tests.py --coverage

# Run tests in parallel
python run_tests.py --parallel

# Verbose output
python run_tests.py --verbose

# Install dependencies and run tests
python run_tests.py --install-deps --coverage
```

### Direct Pytest Usage

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_agents.py
pytest tests/test_a2a_protocol.py

# Run tests with markers
pytest -m unit
pytest -m integration
pytest -m a2a

# Generate coverage report
pytest --cov=agents --cov=shared --cov-report=html

# Run tests in parallel
pytest -n auto
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

- Test discovery patterns
- Coverage reporting
- Asyncio mode configuration
- Warning filters
- Markers for test categorization

### Fixtures (`conftest.py`)

- **Agent Fixtures**: Pre-configured agent instances
- **Task Manager Fixtures**: Task managers with mocked dependencies
- **Mock Fixtures**: Mocked Claude CLI responses and processes
- **Sample Data Fixtures**: Test data for A2A messages and tasks

## Test Markers

Use pytest markers to run specific test categories:

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# A2A protocol tests only
pytest -m a2a

# Slow tests (for CI/CD optimization)
pytest -m "not slow"
```

## Coverage Reports

Test coverage is tracked for:

- `agents/` - All agent implementations
- `shared/` - Shared utilities and types

Coverage reports are generated in multiple formats:
- **HTML**: `htmlcov/index.html` (detailed browsable report)
- **Terminal**: Summary in console output
- **XML**: `coverage.xml` (for CI/CD integration)

## Mocking Strategy

### Claude CLI Subprocess Mocking

Tests mock the Claude CLI subprocess execution to:
- Control response content
- Simulate various error conditions
- Test timeout scenarios
- Avoid dependency on actual Claude CLI installation

```python
# Example mock usage
with patch('asyncio.create_subprocess_exec') as mock_subprocess:
    mock_process = Mock()
    mock_process.returncode = 0
    mock_process.communicate = AsyncMock(return_value=(b"Mock response", b""))
    mock_subprocess.return_value = mock_process
    
    result = await agent.invoke_claude_cli("test query", "session_id")
```

### Push Notification Mocking

Push notification services are mocked to test:
- Notification sending logic
- URL verification
- Error handling without external dependencies

## Performance Testing

Performance tests verify:

- **Concurrent Requests**: Multiple agents handling requests simultaneously
- **Streaming Performance**: Response streaming within time limits
- **Memory Usage**: No memory leaks during long-running tests
- **Response Times**: Acceptable latency for typical operations

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements.txt
      
      - name: Run tests
        run: python run_tests.py --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Test Data

### Sample A2A Messages

Tests use realistic A2A message structures:

```json
{
  "jsonrpc": "2.0",
  "id": "test_request_123",
  "method": "message/send",
  "params": {
    "message": {
      "messageId": "msg_001",
      "taskId": "task_001", 
      "contextId": "session_001",
      "parts": [
        {
          "kind": "text",
          "text": "Create a React component"
        }
      ]
    }
  }
}
```

### Mock Responses

Agents return structured responses for testing:

```python
{
    "is_task_complete": True,
    "require_user_input": False,
    "content": "Generated code or response"
}
```

## Adding New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test

```python
@pytest.mark.asyncio
async def test_new_functionality(frontend_agent, mock_process):
    """Test description"""
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_subprocess.return_value = mock_process
        
        result = await frontend_agent.invoke_async("test query", "session")
        
        assert result["is_task_complete"] is True
        assert "expected content" in result["content"]
```

### Test Markers

Add appropriate markers to new tests:

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_unit_functionality():
    """Unit test example"""
    pass

@pytest.mark.integration
@pytest.mark.slow
async def test_integration_scenario():
    """Integration test example"""
    pass
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Async Test Issues**: Use `@pytest.mark.asyncio` decorator
3. **Mock Not Working**: Check patch target paths
4. **Coverage Missing**: Verify coverage paths in configuration

### Debug Mode

Run tests with debug output:

```bash
# Maximum verbosity
pytest -vvv --tb=long

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb
```

### Test Environment

Ensure consistent test environment:

```bash
# Create virtual environment
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# or
test_env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements.txt
```

## Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Ensure good coverage** (aim for >90%)
3. **Add appropriate markers** for test categorization
4. **Update documentation** if adding new test patterns
5. **Run full test suite** before submitting changes

## Maintenance

### Regular Tasks

- **Update dependencies** in `tests/requirements.txt`
- **Review test coverage** and add tests for uncovered code
- **Performance benchmarks** to catch regressions
- **Clean up outdated tests** when refactoring code

### Monitoring

- **CI/CD integration** for automated testing
- **Coverage tracking** over time
- **Performance regression** detection
- **Test execution time** optimization