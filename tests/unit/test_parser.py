"""Tests for OpenAPI parser."""

from pathlib import Path

import pytest

from api_governor.parser import OpenAPIParseError, OpenAPIParser


class TestOpenAPIParser:
    """Tests for OpenAPIParser class."""

    def test_parse_valid_spec(self, tmp_path: Path) -> None:
        """Test parsing a valid OpenAPI spec."""
        spec_content = """
openapi: 3.0.3
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: OK
"""
        spec_file = tmp_path / "openapi.yaml"
        spec_file.write_text(spec_content)

        parser = OpenAPIParser(spec_file)
        spec = parser.parse()

        assert spec["openapi"] == "3.0.3"
        assert spec["info"]["title"] == "Test API"
        assert "/users" in spec["paths"]

    def test_parse_missing_file(self, tmp_path: Path) -> None:
        """Test parsing a non-existent file."""
        parser = OpenAPIParser(tmp_path / "nonexistent.yaml")

        with pytest.raises(OpenAPIParseError, match="not found"):
            parser.parse()

    def test_get_operations(self, tmp_path: Path) -> None:
        """Test extracting operations from spec."""
        spec_content = """
openapi: 3.0.3
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: OK
    post:
      summary: Create user
      responses:
        '201':
          description: Created
"""
        spec_file = tmp_path / "openapi.yaml"
        spec_file.write_text(spec_content)

        parser = OpenAPIParser(spec_file)
        parser.parse()
        operations = parser.get_operations()

        assert len(operations) == 2
        paths_methods = [(p, m) for p, m, _ in operations]
        assert ("/users", "get") in paths_methods
        assert ("/users", "post") in paths_methods

    def test_validate_refs_valid(self, tmp_path: Path) -> None:
        """Test ref validation with valid refs."""
        spec_content = """
openapi: 3.0.3
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get:
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
"""
        spec_file = tmp_path / "openapi.yaml"
        spec_file.write_text(spec_content)

        parser = OpenAPIParser(spec_file)
        parser.parse()
        errors = parser.validate_refs()

        assert len(errors) == 0

    def test_validate_refs_invalid(self, tmp_path: Path) -> None:
        """Test ref validation with invalid refs."""
        spec_content = """
openapi: 3.0.3
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get:
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NonExistent'
"""
        spec_file = tmp_path / "openapi.yaml"
        spec_file.write_text(spec_content)

        parser = OpenAPIParser(spec_file)
        parser.parse()
        errors = parser.validate_refs()

        assert len(errors) == 1
        assert "NonExistent" in errors[0]
