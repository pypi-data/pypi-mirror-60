__version__ = "1.0"

from .distillation import BasicTrainer
from .distillation import BasicDistiller
from .distillation import GeneralDistiller
from .distillation import BasicMultiTeacherDistiller
from .distillation import BasicMultiTaskDistiller

from .distillation import TrainingConfig, DistillationConfig

from .presets import FEATURES
from .presets import ADAPTOR_KEYS
from .presets import KD_LOSS_MAP, MATCH_LOSS_MAP, PROJ_MAP
from .presets import WEIGHT_SCHEDULER, TEMPERATURE_SCHEDULER
from .presets import register_new

Distillers = {
    'Basic': BasicDistiller,
    'General': GeneralDistiller,
    'BasicMultiTeacher': BasicMultiTeacherDistiller,
    'BasicMultiTask': BasicMultiTaskDistiller,
    'BasicTrain': BasicTrainer
}