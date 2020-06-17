class Factory:
    def __init__(self, model_class):
        self._model_class = model_class

    def create(self, values: dict):
        """
        Factory method to create a model object after input validation

        :param values: Key-value dictionary for model values
        :return: The model instance object
        """
        model = self._model_class()

        for key, value in values.items():
            if hasattr(model, key):
                setattr(model, key, value)

        return model
