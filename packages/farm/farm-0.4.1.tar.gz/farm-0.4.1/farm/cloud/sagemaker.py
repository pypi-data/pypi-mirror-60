from sagemaker.estimator import EstimatorBase, Estimator
from farm.train import Trainer


class SageMakerTrainer(EstimatorBase):
    def __init__(self, role, train_instance_type, checkpoint_s3_uri, train_use_spot_instances=False, **kwargs):
        self.trainer = Trainer(**kwargs)




estimator = Estimator(
    entry_point="a_train.py",
    role="",

)