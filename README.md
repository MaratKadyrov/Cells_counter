# Cells counting in the Fuchs-Rosenthal Counting Chamber using CV (Faster RCNN model)

At the moment, many laboratories and industries involved in cell technologies are faced with the need for quantitative control of cells during the process of their cultivation. Cellular technologies are widely used in pharmaceutical production. They are used, for example, to produce insulin, interferon, various vaccines, hormones, antibodies, etc.

In this project, Chinese hamster ovary cells are counted. As cells grow and develop, they divide, consume nutrients, and produce metabolites. One of the very important parameters of cell culture growth is their viability. To evaluate it in the conditions of pharmaceutical production, it is necessary to take daily cell samples and count them. Several methods are used for counting, the first and simplest is sampling, its further staining and manual counting using a microscope in a counting chamber.

<img src="https://github.com/MaratKadyrov/Cells_counter/blob/main/presentation/cells_example.png" width="200" height="200">

A more modern option is the use of counters, these are automatic systems that require specific and rather expensive consumables.

To gather the dataset, we went to the cell technology laboratory at the RTU MIREA Technopark, a sample of the culture suspension was provided by JSC Generium. More than 250 photos were taken, but only 68 were of sufficient quality for marking.

Markup result:
   - Cells total 4584
   - Living cells 4102
   - Dead cells 482

After finishing the markup, we moved on to choosing a model from 3 options. These are YOLO, UNET and FasterRCNN.
The result of YOLO was not so good. For UNET - there are a large number of scientific articles on the topic of its application to medical and biological data, and in principle the model should have coped well with the task, but in our case it showed a worse result than RCNN. But on the pretrained RCNN, the results were immediately quite good.

Thus our choice is the Faster RCNN model. At the beginning, the model poorly recognized even living cells, but closer to the thousandth epoch, the model recognizes not only living but also dead cells. Since the classes were not balanced, we artificially increased the number of dead cells.

Learning process:

<img src="https://github.com/MaratKadyrov/Cells_counter/blob/main/presentation/learning_process.png" width="400" height="400">

The model was implemented as a site in Flask, using JavaScript published on Google Cloud.

You can see how the site works below:

![Output sample](https://github.com/MaratKadyrov/Cells_counter/blob/main/presentation/Cells.gif)
