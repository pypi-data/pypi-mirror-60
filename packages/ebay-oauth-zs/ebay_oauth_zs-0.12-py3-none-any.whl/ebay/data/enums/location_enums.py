from model_utils import Choices

LocationTypeEnum = Choices(
    ("WAREHOUSE", "Склад"), ("STORE", "Магазин"), ("BOTH", "Магазин и склад"),
)

StatusEnum = Choices(("DISABLED", "Неактивировано"), ("ENABLED", "Активировано"),)
