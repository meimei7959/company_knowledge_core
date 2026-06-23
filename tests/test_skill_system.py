import unittest

from scripts.validate_skill_system import validate


class SkillSystemTest(unittest.TestCase):
    def test_production_skills_are_packaged_and_bound_to_roles(self) -> None:
        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()

