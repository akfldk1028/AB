"""Simple logging test"""
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'test_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)

def test_logging():
    """Test all logging levels"""
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    # Test with structured data
    test_data = {
        "user": "test_user",
        "action": "login",
        "status": "success"
    }
    logger.info(f"Structured data test: {test_data}")
    
    # Test exception logging
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.exception("Exception occurred during division")
    
    print("\n[SUCCESS] All logging tests completed successfully!")
    print(f"[INFO] Check the log file: test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

if __name__ == "__main__":
    print("Starting logging test...\n")
    test_logging()