"""Run all module tests in app/src"""

import subprocess
import sys

# Files with test code
test_files = [
    'app/src/color.py',
    'app/src/position.py',
    'app/src/rectangle.py',
    'app/src/size.py',
    'app/src/chest.py',
    'app/src/player.py',
    'app/src/game.py',
    'app/src/input_handler.py',
    'app/src/room_interaction_handler.py',
]

def run_tests():
    """Run all test files and report results."""
    from logging import AppLogger

    AppLogger.i("=" * 60)
    AppLogger.i("Running All Module Tests")
    AppLogger.i("=" * 60)

    passed = []
    failed = []

    for test_file in test_files:
        AppLogger.i(f"\nTesting {test_file}...")
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and "✓" in result.stdout + result.stderr:
                AppLogger.i(f"  ✓ {test_file} passed")
                passed.append(test_file)
            else:
                AppLogger.w(f"  ✗ {test_file} failed")
                failed.append(test_file)
                if result.stderr:
                    AppLogger.e(f"    Error: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            AppLogger.w(f"  ✗ {test_file} timed out")
            failed.append(test_file)
        except Exception as e:
            AppLogger.e(f"  ✗ {test_file} error: {e}")
            failed.append(test_file)

    # Summary
    AppLogger.i("\n" + "=" * 60)
    AppLogger.i(f"Test Summary: {len(passed)} passed, {len(failed)} failed")
    AppLogger.i("=" * 60)

    if passed:
        AppLogger.i(f"Passed ({len(passed)}): {', '.join(passed)}")

    if failed:
        AppLogger.w(f"Failed ({len(failed)}): {', '.join(failed)}")
        return 1

    AppLogger.i("\n✓ All tests passed!")
    return 0

if __name__ == '__main__':
    sys.exit(run_tests())
