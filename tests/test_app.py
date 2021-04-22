import io
from pathlib import Path
import pytest
from flask import session

from app import app

root = Path(__file__).parent.parent


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def small_file():
    with open(root / "tests/test_data/data_with_header.xlsx", "rb") as f:
        data = f.read()

    yield data


@pytest.fixture
def big_file():
    with open(root / "tests/test_data/henrys_big_frame.xls", "rb") as f:
        data = f.read()

    yield data


def test_upload_page(client):
    assert client.get("/") is not None


class TestFileFlow:
    @pytest.mark.skip(reason="Takes too long")
    def test_handle_upload_big_file(self, client, small_file, big_file):

        for file in [small_file, big_file]:
            data = {"data": (io.BytesIO(file), "test_file.xlsx")}
            response = client.post("/api/handle-upload", data=data)

            assert response.status_code == 200

    def test_transfer_of_data_between_upload_and_download(self, client, small_file, big_file):

        for file in [small_file, big_file]:
            data = {"data": (io.BytesIO(file), "test_file.xlsx")}

            _ = client.post("/api/handle-upload", data=data)

            assert session.get("data") is not None
            download_response = client.get("/api/download-results")

            assert download_response.status_code == 200
