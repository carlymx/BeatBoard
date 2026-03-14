"""Unit tests for ProjectPackager."""

import json
import zipfile
from pathlib import Path

import pytest

from beatboard.core.beat import Beat
from beatboard.core.project import Project
from beatboard.core.project_packager import ProjectPackager


class TestProjectPackager:
    def test_detect_format_json(self, tmp_path):
        json_file = tmp_path / "test.bbp"
        json_file.write_text('{"test": "data"}', encoding="utf-8")
        
        assert ProjectPackager.detect_format(json_file) == "json"

    def test_detect_format_zip(self, tmp_path):
        zip_file = tmp_path / "test.bbp"
        with zipfile.ZipFile(zip_file, "w") as zf:
            zf.writestr("test.txt", "content")
        
        assert ProjectPackager.detect_format(zip_file) == "zip"

    def test_pack_unpack_roundtrip(self, tmp_path):
        project = Project(name="Test Project")
        beat = Beat(title="Test Beat", content="Some content")
        project.add_beat(beat)
        
        zip_file = tmp_path / "test.bbp"
        ProjectPackager.pack(project, zip_file)
        
        assert zip_file.exists()
        
        loaded_project = ProjectPackager.unpack(zip_file)
        
        assert loaded_project.name == "Test Project"
        assert len(loaded_project.beats) == 1
        assert loaded_project.beats[0].title == "Test Beat"
        assert loaded_project.beats[0].content == "Some content"

    def test_load_project_json_format(self, tmp_path):
        json_file = tmp_path / "test.bbp"
        data = {
            "version": "1.0",
            "project": {
                "id": "project-id",
                "name": "JSON Project",
                "created_at": "2024-01-01T00:00:00",
                "modified_at": "2024-01-01T00:00:00",
            },
            "canvas": {"zoom": 1.0, "pan_x": 0, "pan_y": 0},
            "beats": [],
            "connections": [],
            "metadata": {},
        }
        json_file.write_text(json.dumps(data), encoding="utf-8")
        
        project = ProjectPackager.load_project(json_file)
        
        assert project.name == "JSON Project"

    def test_load_project_zip_format(self, tmp_path):
        zip_file = tmp_path / "test.bbp"
        data = {
            "version": "1.0",
            "project": {
                "id": "project-id",
                "name": "ZIP Project",
                "created_at": "2024-01-01T00:00:00",
                "modified_at": "2024-01-01T00:00:00",
            },
            "canvas": {"zoom": 1.0, "pan_x": 0, "pan_y": 0},
            "beats": [],
            "connections": [],
            "metadata": {},
        }
        
        with zipfile.ZipFile(zip_file, "w") as zf:
            zf.writestr("project.json", json.dumps(data))
        
        project = ProjectPackager.load_project(zip_file)
        
        assert project.name == "ZIP Project"

    def test_save_project_creates_zip(self, tmp_path):
        project = Project(name="Save Test")
        
        file_path = tmp_path / "save_test.bbp"
        ProjectPackager.save_project(project, file_path)
        
        with zipfile.ZipFile(file_path, "r") as zf:
            assert "project.json" in zf.namelist()
