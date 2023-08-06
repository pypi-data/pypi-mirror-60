# DeepFit
DeepFit is an open source package for creating novel methods that help all the stake holders better manage Patient Engagement. It leverages research technology like Data Shapley, Multi-Accuracy and cPCA from Stanford Artificial Intelligence Labs (**SAIL**)

![DeepFit](/Docs/DeepFit_updated.png)

* [Getting Started](#getting-started)
* [Programming Guide](#programming-guide)
* [vLife](www.virtusa.com/vlife)
* [License](license)

### Getting Started
Please Install DeepFit package using 
```
!pip install deepfitv
```

### Programming Guide

**Incision Object Declaration**
```
deepfitv.incision.Incision(<path of image>)
```

To identify incision image object detection run the object detection function run 
```
deepfitv.incision.Incision(<path of image>).object_detection()
```

To classify the incisin image into less than 30 or post 30 days of surgery run 
```
deepfitv.incision.Incision(<path of image>).classify_image()
```

### License
Coming Soon


