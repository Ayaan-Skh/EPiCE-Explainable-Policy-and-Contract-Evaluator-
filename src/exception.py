import sys
from src.logger import logging
import traceback


# This function builds a detailed error message. It accepts either the `sys` module
# (so callers can pass `sys` to get the active traceback) or an exception object.
def error_message_detail(error, error_detail=None):
    # Determine traceback object safely
    try:
        if error_detail is not None and hasattr(error_detail, "exc_info"):
            _, _, exc_tb = error_detail.exc_info()
        else:
            # Fallback to current exception info
            _, _, exc_tb = sys.exc_info()

        if exc_tb is not None:
            file_name = exc_tb.tb_frame.f_code.co_filename
            line_number = exc_tb.tb_lineno
        else:
            # If no traceback available, use unknown placeholders
            file_name = "<unknown>"
            line_number = 0

    except Exception:
        # As a last resort, populate with minimal info
        file_name = "<unknown>"
        line_number = 0

    error_message = 'The error occured in the file:{file_name} in the line:{line_number} and it says:{error_message}'
    return error_message.format(file_name=file_name, line_number=line_number, error_message=str(error))



class CustomException(Exception):
    def __init__(self, error_message, error_details=None):
        # Initialize the base Exception class with the error message
        super().__init__(error_message)
        # Generate a detailed error message using the error_message_detail function
        self.error_message = error_message_detail(error=error_message, error_detail=error_details)

    def __str__(self):
        return self.error_message


if __name__ == "__main__":
    try:
        a = 1 / 0
    except Exception as e:
        logging.info("Divide by zero error")
        raise CustomException(e, sys) from e
            