import unittest


class SmokeTest(unittest.TestCase):
    def test_import_backend_package(self) -> None:
        import backend  # noqa: F401


if __name__ == "__main__":
    unittest.main()
