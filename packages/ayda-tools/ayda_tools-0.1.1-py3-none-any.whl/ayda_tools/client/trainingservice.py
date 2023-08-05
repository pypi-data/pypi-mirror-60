from .connection import ServerConnection
from .callbacks import create_all_result_callbacks
from .resultservice import ResultService
from .. import config

from ..interfaces import JobInfo
from ..parsing import create_object


class TrainingService:
    def __init__(self, connection: ServerConnection, result_service: ResultService):
        self.result_service = result_service
        self.connection = connection

    def train_job(self, job: JobInfo, pretrained_model_path: str = ""):

        model = create_object(job.model_parameter)
        training_data = create_object(job.training_data)

        base_path = config.AYDA_DATA_PATH

        training_data._base_path = base_path

        train_options = job.train_options
        model.train(
            training_data,
            model_dir="/media",
            callbacks=create_all_result_callbacks(
                "/media/model{}",
                job.obj_ref,
                connection=self.connection,
                result_service=self.result_service,
            ),
            pretrained_model_name=pretrained_model_path,
            epochs=train_options.epochs,
            epoch_size=train_options.epoch_size,
            timeout_secs=train_options.timeout_secs,
            validation_size=train_options.validation_size,
        )
