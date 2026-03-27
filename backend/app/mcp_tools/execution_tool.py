import subprocess
import re
import time
from utils.logger import logger
from schemas.response_schema import ExecutionResult, TestCaseResult

class ExecutionTool:
    def _parse_pytest_verbose(self, output: str) -> list[TestCaseResult]:
        """Parse pytest -v output to extract individual test case results."""
        test_cases = []
        # Match lines like: test_file.py::test_name PASSED  [ 50%]
        # or: test_file.py::TestClass::test_name FAILED  [100%]
        pattern = re.compile(
            r'^(.*?::[\w_]+)\s+(PASSED|FAILED|ERROR|SKIPPED)',
            re.MULTILINE
        )
        for match in pattern.finditer(output):
            full_name = match.group(1).strip()
            status = match.group(2).lower()
            # Extract just the test name (last part after ::)
            name = full_name.split("::")[-1] if "::" in full_name else full_name
            test_cases.append(TestCaseResult(
                name=name,
                status=status,
                duration="—",
                error_message=""
            ))

        # Parse durations from the short test summary or timing lines
        # e.g. "1 passed in 0.45s"
        duration_pattern = re.compile(r'=+\s*(.*?)\s+in\s+([\d.]+)s\s*=+')
        dur_match = duration_pattern.search(output)
        total_duration = dur_match.group(2) + "s" if dur_match else None
        if total_duration and len(test_cases) == 1:
            test_cases[0].duration = total_duration

        # Try to extract individual durations from --durations output
        dur_line_pattern = re.compile(
            r'([\d.]+)s\s+(call|setup|teardown)\s+(.*?)$',
            re.MULTILINE
        )
        dur_map: dict[str, str] = {}
        for dur_match in dur_line_pattern.finditer(output):
            dur_val = dur_match.group(1) + "s"
            test_id = dur_match.group(3).strip()
            test_name = test_id.split("::")[-1] if "::" in test_id else test_id
            if dur_match.group(2) == "call":
                dur_map[test_name] = dur_val
        for tc in test_cases:
            if tc.name in dur_map:
                tc.duration = dur_map[tc.name]

        # Parse FAILURES section to extract error messages
        failures_pattern = re.compile(
            r'_{3,}\s+([\w_:]+)\s+_{3,}\n(.*?)(?=\n_{3,}|\n={3,})',
            re.DOTALL
        )
        for fail_match in failures_pattern.finditer(output):
            failed_name = fail_match.group(1).split("::")[-1]
            error_text = fail_match.group(2).strip()
            # Trim to last ~300 chars if too long
            if len(error_text) > 300:
                error_text = "..." + error_text[-300:]
            for tc in test_cases:
                if tc.name == failed_name and tc.status == "failed":
                    tc.error_message = error_text
                    break

        return test_cases

    def run_command(self, command: str, timeout: int = 300) -> ExecutionResult:
        try:
            logger.info(f"Executing command: {command}")
            start_time = time.time()

            # Add verbose flag for detailed per-test output
            if "-v" not in command:
                command = command.replace("pytest", "pytest -v", 1)

            # Simple subprocess execution
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(timeout=timeout)
            end_time = time.time()
            execution_time = f"{round(end_time - start_time, 2)}s"
            full_output = stdout + "\n" + stderr

            # Parse individual test case results from verbose output
            test_cases = self._parse_pytest_verbose(full_output)

            if test_cases:
                passed = sum(1 for tc in test_cases if tc.status == "passed")
                failed = sum(1 for tc in test_cases if tc.status in ("failed", "error"))
                tests_run = len(test_cases)
            else:
                # Fallback: no parseable test lines
                passed = 1 if process.returncode == 0 else 0
                failed = 0 if process.returncode == 0 else 1
                tests_run = 1
                test_cases = [TestCaseResult(
                    name="test_suite",
                    status="passed" if process.returncode == 0 else "failed",
                    duration=execution_time,
                    error_message="" if process.returncode == 0 else "Test execution failed. See logs."
                )]

            return ExecutionResult(
                tests_run=tests_run,
                passed=passed,
                failed=failed,
                execution_time=execution_time,
                test_cases=test_cases,
                logs=full_output
            )
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return ExecutionResult(
                tests_run=1,
                passed=0,
                failed=1,
                execution_time="0s",
                test_cases=[TestCaseResult(
                    name="test_suite",
                    status="error",
                    duration="0s",
                    error_message=str(e)
                )],
                logs=str(e)
            )

execution_tool = ExecutionTool()
