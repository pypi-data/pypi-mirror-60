import wget
url = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/essential-v4/pretrained-yolov3.h5'
filename = wget.download(url)
print (filename)
from imageai.Detection.Custom import DetectionModelTrainer

def create_model():
    trainer = DetectionModelTrainer()
    trainer.setModelTypeAsYOLOv3()
    trainer.setDataDirectory(data_directory="Incision")
    trainer.setTrainConfig(object_names_array=["incision"], batch_size=4, num_experiments=100, train_from_pretrained_model="pretrained-yolov3.h5")
    trainer.trainModel()

