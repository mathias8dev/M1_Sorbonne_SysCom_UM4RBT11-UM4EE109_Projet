import sys
import os
import traceback
import atexit
from datetime import datetime
from typing import Optional


class AppLogger:
    """A Timber-inspired logging library for Python with file logging support

    The logger automatically closes the log file on application exit using atexit.
    You can also manually close it by calling AppLogger.shutdown().

    Usage:
        AppLogger.d('Debug message')
        AppLogger.v('Verbose message')
        AppLogger.i('Info message')
        AppLogger.w('Warning message')
        AppLogger.e('Error message')

        # With custom tag
        AppLogger.d('Debug message', tag='MyTag')

        # With exception
        try:
            ...
        except Exception as e:
            AppLogger.e('Error occurred', error=e)

        # Configure file logging
        AppLogger.set_log_file('app.log')
        AppLogger.set_file_logging_enabled(False)  # Disable file logging

        # Manual cleanup (optional, happens automatically on exit)
        AppLogger.shutdown()
    """

    _enabled = True  # Enable by default (can check for debug mode)
    _max_tag_length = 40
    _file_logging_enabled = True  # Enable file logging by default
    _log_file_path: Optional[str] = None
    _log_file_handle = None
    
    @classmethod
    def set_enabled(cls, enabled: bool) -> None:
        """Enable or disable logging"""
        cls._enabled = enabled

    @classmethod
    def set_max_tag_length(cls, length: int) -> None:
        """Set maximum tag length (default: 40)"""
        cls._max_tag_length = length

    @classmethod
    def set_file_logging_enabled(cls, enabled: bool) -> None:
        """Enable or disable file logging (default: enabled)"""
        cls._file_logging_enabled = enabled
        if not enabled:
            cls._close_log_file()

    @classmethod
    def set_log_file(cls, file_path: str) -> None:
        """Set the log file path. Creates the file and parent directories if they don't exist.

        Args:
            file_path: Path to the log file (absolute or relative)
        """
        cls._close_log_file()
        cls._log_file_path = file_path

        # Create parent directories if they don't exist
        log_dir = os.path.dirname(file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Initialize the log file
        cls._open_log_file()

    @classmethod
    def get_log_file_path(cls) -> Optional[str]:
        """Get the current log file path"""
        return cls._log_file_path

    @classmethod
    def _open_log_file(cls) -> None:
        """Open the log file for writing"""
        if cls._log_file_path and cls._file_logging_enabled:
            try:
                cls._log_file_handle = open(cls._log_file_path, 'a', encoding='utf-8')
                # Register cleanup on exit
                atexit.register(cls._close_log_file)
            except Exception as e:
                print(f"Failed to open log file {cls._log_file_path}: {e}", file=sys.stderr)

    @classmethod
    def _close_log_file(cls) -> None:
        """Close the log file if it's open"""
        if cls._log_file_handle:
            try:
                cls._log_file_handle.close()
            except Exception:
                pass
            finally:
                cls._log_file_handle = None

    @classmethod
    def _ensure_log_file_open(cls) -> None:
        """Ensure the log file is open and ready for writing"""
        if cls._file_logging_enabled and cls._log_file_path and not cls._log_file_handle:
            cls._open_log_file()
    
    @classmethod
    def d(cls, message: str, tag: Optional[str] = None) -> None:
        """Debug log"""
        cls._log('D', message, tag=tag)
    
    @classmethod
    def v(cls, message: str, tag: Optional[str] = None) -> None:
        """Verbose log"""
        cls._log('V', message, tag=tag)
    
    @classmethod
    def i(cls, message: str, tag: Optional[str] = None) -> None:
        """Info log"""
        cls._log('I', message, tag=tag)
    
    @classmethod
    def w(cls, message: str, tag: Optional[str] = None) -> None:
        """Warning log"""
        cls._log('W', message, tag=tag)
    
    @classmethod
    def e(cls, message: str, tag: Optional[str] = None, 
          error: Optional[Exception] = None) -> None:
        """Error log"""
        cls._log('E', message, tag=tag, error=error)
    
    @classmethod
    def log(cls, level: str, message: str, tag: Optional[str] = None,
            error: Optional[Exception] = None) -> None:
        """Generic log method"""
        cls._log(level, message, tag=tag, error=error)
    
    @classmethod
    def _log(cls, level: str, message: str, tag: Optional[str] = None,
             error: Optional[Exception] = None) -> None:
        """Internal logging method"""
        if not cls._enabled:
            return

        actual_tag = tag if tag else cls._get_tag()
        timestamp = datetime.now().isoformat()

        buffer = [f'[{timestamp}] [{level}/{actual_tag}] {message}']

        if error is not None:
            buffer.append(f'  Error: {error}')
            # Get traceback if available
            if hasattr(error, '__traceback__') and error.__traceback__:
                tb_lines = traceback.format_tb(error.__traceback__)
                formatted_tb = cls._format_traceback(tb_lines)
                buffer.append(f'  StackTrace:\n{formatted_tb}')

        log_output = '\n'.join(buffer)

        # Output to console
        print(log_output, file=sys.stderr if level == 'E' else sys.stdout)

        # Output to file if enabled
        if cls._file_logging_enabled:
            cls._write_to_file(log_output)
    
    @classmethod
    def _get_tag(cls) -> str:
        """Extract tag from stack trace"""
        try:
            # Get the current stack
            stack = traceback.extract_stack()
            
            # Skip the last few frames (this method, _log, and the public method)
            # Look for the first frame that's not part of this AppLogger class
            for frame in reversed(stack[:-3]):  # Skip last 3 frames
                filename = frame.filename
                
                # Skip frames from this AppLogger class
                if 'AppLogger' in filename or frame.name in ['_log', 'd', 'v', 'i', 'w', 'e', 'log']:
                    continue
                
                # Extract tag from frame
                tag = cls._extract_tag_from_frame(frame)
                if tag:
                    return cls._truncate_tag(tag)
        
        except Exception:
            # If anything goes wrong, return a default tag
            return 'AppLogger'
        
        return 'Unknown'
    
    @classmethod
    def _extract_tag_from_frame(cls, frame: traceback.FrameSummary) -> str:
        """Extract tag from a single stack frame"""
        try:
            # Use the function/method name
            name = frame.name
            
            # If it's a method call, try to extract the class name
            # This is limited in Python without more context
            if name == '<module>':
                # Use filename without extension
                import os
                return os.path.splitext(os.path.basename(frame.filename))[0]
            
            return name
        
        except Exception:
            return ''
    
    @classmethod
    def _truncate_tag(cls, tag: str) -> str:
        """Truncate tag to maximum length"""
        if len(tag) <= cls._max_tag_length:
            return tag
        return tag[:cls._max_tag_length]
    
    @classmethod
    def _format_traceback(cls, tb_lines: list) -> str:
        """Format traceback for better readability"""
        # Limit to first 10 frames
        limited = tb_lines[:10]
        return ''.join(f'    {line}' for line in limited)

    @classmethod
    def _write_to_file(cls, log_output: str) -> None:
        """Write log output to file"""
        cls._ensure_log_file_open()

        if cls._log_file_handle:
            try:
                cls._log_file_handle.write(log_output + '\n')
                cls._log_file_handle.flush()  # Ensure immediate write
            except Exception as e:
                print(f"Failed to write to log file: {e}", file=sys.stderr)

    @classmethod
    def shutdown(cls) -> None:
        """Shutdown the logger and close the log file.

        This method should be called before application exit to ensure
        all logs are written and the file is properly closed.
        """
        cls._close_log_file()


# Example usage
if __name__ == '__main__':
    # Configure file logging
    AppLogger.set_log_file('test.log')

    # Basic logging
    AppLogger.d('This is a debug message')
    AppLogger.v('This is a verbose message')
    AppLogger.i('This is an info message')
    AppLogger.w('This is a warning message')

    # With custom tag
    AppLogger.i('Custom tagged message', tag='MyCustomTag')

    # With error
    try:
        result = 1 / 0
    except Exception as e:
        AppLogger.e('An error occurred', error=e)

    # Disable console logging
    AppLogger.set_enabled(False)
    AppLogger.d('This will not be printed')

    # Re-enable
    AppLogger.set_enabled(True)
    AppLogger.i('Logging re-enabled')

    # Disable file logging
    AppLogger.set_file_logging_enabled(False)
    AppLogger.i('This will only show in console')

    print(f"\nLogs written to: {AppLogger.get_log_file_path()}")