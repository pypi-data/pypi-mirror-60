from imageai.Detection.Custom import DetectionModelTrainer
#!wget https://github.com/OlafenwaMoses/ImageAI/releases/download/essential-v4/pretrained-yolov3.h5

#trainer.setTrainConfig(object_names_array=["incision"], batch_size=4, num_experiments=100, train_from_pretrained_model="Incision/models/pretrained-yolov3.h5")
from imageai.Detection.Custom import CustomObjectDetection
detector = CustomObjectDetection()
detector.setModelTypeAsYOLOv3()
from PIL import Image

detector.setModelPath("Incision/models/detection_model-ex-018--loss-0005.172.h5")
detector.setJsonPath("Incision/json/detection_config.json")
detector.loadModel()

class incision:
    def __init__(self,name_pic):
        self.new_pic = new_pic
        

    def object_detection(self):
        print(" The uploaded pic by the user is:")
        pic = Image.open(self.new_pic)
        display(pic)
        # detector.setJsonPath("Incision/json/detection_config.json")
        print ("image displayed")
        detections_1 = detector.detectObjectsFromImage(input_image=pic, output_image_path="detected.jpg")
        print ("image detected")
        detection = 0
        for x in detections_1:
            detection = x['percentage_probability']
        # print(detection)
        if detection >= 60:
            print("\n\n The image uploaded is correct and has correctly identified the incision")
        else:
            print(" The image uploaded does not recognize an incision. Please upload again")

#if __name__ == '__main__':
#   incision(sys.argv[1])
