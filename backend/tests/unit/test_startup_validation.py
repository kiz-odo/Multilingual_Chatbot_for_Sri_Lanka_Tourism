"""
Unit tests for startup validation (backend/app/core/startup_validation.py).

Report logic is pure. The validator's sync checks read settings
deterministically; the async path runs against the test MongoDB/Redis.
"""

import pytest

from backend.app.core.startup_validation import (
    ValidationResult,
    ValidationSeverity,
    StartupValidationReport,
    StartupValidator,
    validate_startup_environment,
)


def _result(name, passed, severity):
    return ValidationResult(name=name, passed=passed, severity=severity, message=name)


class TestReport:
    def test_counts_and_flags(self):
        report = StartupValidationReport()
        report.add_result(_result("a", True, ValidationSeverity.INFO))
        report.add_result(_result("b", False, ValidationSeverity.CRITICAL))
        report.add_result(_result("c", False, ValidationSeverity.WARNING))

        assert report.passed_count == 1
        assert report.failed_count == 2
        assert report.has_critical_failures is True
        assert report.has_warnings is True

    def test_clean_report_has_no_failures(self):
        report = StartupValidationReport()
        report.add_result(_result("a", True, ValidationSeverity.CRITICAL))
        assert report.has_critical_failures is False
        assert report.has_warnings is False

    def test_summary_is_readable(self):
        report = StartupValidationReport()
        report.add_result(_result("SECRET_KEY", True, ValidationSeverity.CRITICAL))
        report.add_result(
            ValidationResult("MONGODB", False, ValidationSeverity.CRITICAL, "down", details="start it")
        )
        summary = report.get_summary()
        assert "STARTUP VALIDATION REPORT" in summary
        assert "SECRET_KEY" in summary
        assert "start it" in summary  # details are shown for failed checks


class TestSyncValidators:
    def test_secret_key_passes_in_debug(self):
        # Test env runs with DEBUG=true, so an insecure key is tolerated.
        v = StartupValidator()
        v._validate_secret_key()
        results = {r.name: r for r in v.report.results}
        assert "SECRET_KEY" in results
        assert results["SECRET_KEY"].passed is True

    def test_environment_mode_recorded(self):
        v = StartupValidator()
        v._validate_environment_mode()
        assert any(r.name == "ENVIRONMENT_MODE" for r in v.report.results)

    def test_required_settings_present(self):
        v = StartupValidator()
        v._validate_required_settings()
        names = {r.name for r in v.report.results}
        assert {"MONGODB_URL", "REDIS_URL", "DATABASE_NAME"} <= names
        # All required settings have defaults, so all should pass
        assert all(r.passed for r in v.report.results)

    def test_api_keys_and_security_run(self):
        v = StartupValidator()
        v._validate_api_keys()
        v._validate_security_settings()
        assert len(v.report.results) > 0


class TestAsyncValidation:
    async def test_validate_all_populates_report(self):
        report = await StartupValidator().validate_all()
        assert len(report.results) > 0
        # MongoDB is up in the test environment
        mongo = [r for r in report.results if "MONGO" in r.name.upper()]
        assert mongo and mongo[0].passed is True

    async def test_validate_startup_environment_returns_bool(self):
        # DEBUG=true means this never raises SystemExit
        result = await validate_startup_environment()
        assert isinstance(result, bool)
