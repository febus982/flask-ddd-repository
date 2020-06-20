from flask import Flask
from flask_ddd_repository.exceptions import ModelNotFoundException
from flask_ddd_repository.repository import SQLAlchemyRepository
from pytest import raises


class TestSQLAlchemyRepository:
    def test_find_one_fails_when_no_results(self, app: Flask, Model):
        repo = SQLAlchemyRepository(Model)
        with raises(ModelNotFoundException):
            with app.test_request_context():
                repo.find_one(22)
