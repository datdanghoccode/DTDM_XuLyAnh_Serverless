"""
Bootstrap / Placeholder AWS Lambda Handler.
Phục vụ khởi tạo hạ tầng Terraform trước khi mã nguồn chính thức (src/lambda_function.py)
được Kỹ sư Phần mềm (Trần Ngọc Lâm) tích hợp.
"""

import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

def lambda_handler(event, context):
    logger.info("Bootstrap Lambda Handler invoked.")
    logger.info("Environment Configuration:")
    logger.info(f"  - ENVIRONMENT: {os.getenv('ENVIRONMENT')}")
    logger.info(f"  - INPUT_BUCKET: {os.getenv('INPUT_BUCKET')}")
    logger.info(f"  - OUTPUT_BUCKET: {os.getenv('OUTPUT_BUCKET')}")
    logger.info(f"  - METADATA_TABLE: {os.getenv('METADATA_TABLE')}")
    logger.info(f"  - DLQ_URL: {os.getenv('DLQ_URL')}")
    
    # In event nhận được từ S3
    logger.info(f"Received event: {json.dumps(event)}")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Infrastructure bootstrap handler executed successfully.",
            "status": "ready_for_src_integration"
        })
    }
