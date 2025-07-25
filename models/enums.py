from enum import Enum


class DisplayMethodEnum(str,Enum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"

class ResponseMethodEnum(str,Enum):
    BINARY = "binary"
    GRADIENT = "gradient"

class ImageListColumn(str,Enum):
    LEARNING = "learning_image_list"
    EXPERIMENT = "experiment_image_list"
