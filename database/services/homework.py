from database.repositories import HomeworkRepository


class HomeworkService:
    def __init__(self, repo: HomeworkRepository) -> None:
        self.repo = repo
