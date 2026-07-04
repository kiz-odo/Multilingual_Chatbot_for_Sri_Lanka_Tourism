"""
Unit tests for SafetyService (backend/app/services/safety_service.py).

Focuses on deterministic logic; DB-backed paths use the test MongoDB and
clean up after themselves.
"""

import pytest

from backend.app.services.safety_service import SafetyService
from backend.app.models.safety import Location


@pytest.fixture
def service():
    return SafetyService()


class TestDistance:
    def test_same_point_is_zero(self, service):
        assert service._calculate_distance(6.9271, 79.8612, 6.9271, 79.8612) == pytest.approx(0.0, abs=1e-6)

    def test_colombo_to_kandy_distance(self, service):
        # Colombo (6.9271, 79.8612) -> Kandy (7.2906, 80.6337) is ~94 km
        d = service._calculate_distance(6.9271, 79.8612, 7.2906, 80.6337)
        assert 85 < d < 105

    def test_distance_is_symmetric(self, service):
        a = service._calculate_distance(6.9, 79.8, 7.3, 80.6)
        b = service._calculate_distance(7.3, 80.6, 6.9, 79.8)
        assert a == pytest.approx(b)


class TestStaticData:
    async def test_emergency_numbers(self, service):
        numbers = await service.get_emergency_numbers()
        assert numbers["police"] == "119"
        assert numbers["ambulance"] == "110"
        assert "tourist_police" in numbers

    async def test_medical_phrases_sinhala(self, service):
        phrases = await service.get_medical_phrases("si")
        assert "help" in phrases and "doctor" in phrases

    async def test_medical_phrases_tamil(self, service):
        phrases = await service.get_medical_phrases("ta")
        assert "hospital" in phrases

    async def test_medical_phrases_english(self, service):
        phrases = await service.get_medical_phrases("en")
        assert phrases["help"] == "Help!"

    async def test_medical_phrases_unknown_falls_back_to_english(self, service):
        phrases = await service.get_medical_phrases("xx")
        assert phrases["help"] == "Help!"


class TestEmbassy:
    async def test_find_nearest_embassy_unknown_user(self, service):
        # No such user -> service returns an empty dict
        result = await service.find_nearest_embassy(
            "000000000000000000000000",
            Location(latitude=6.9271, longitude=79.8612),
        )
        assert result == {}


class TestSafetyScore:
    async def test_generates_default_score_for_new_city(self, service):
        score = await service.get_safety_score("UnitTestCity_XYZ")
        try:
            assert score.city == "UnitTestCity_XYZ"
            assert score.safety_score == 75.0
            assert len(score.safety_tips) > 0
        finally:
            await score.delete()
