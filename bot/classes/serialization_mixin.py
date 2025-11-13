from typing import Self


class SerializationMixin:
    def __init__(self):
        super().__init__()
        if not (model := getattr(self, 'model')):
            raise AttributeError(
                f"Class {self.__class__.__name__} must define 'model' class attribute"
            )
        self.model = model

    def to_model(self):
        return self.model(
            **{k: v for k, v in self.__dict__.items() if k in self.model.__table__.columns}
        )

    @classmethod
    def from_model(cls, model) -> None | Self:
        if model is None:
            return None
        return cls(
            **{k: v for k, v in model.__dict__.items() if k in cls.__init__.__annotations__.keys()}
        )
