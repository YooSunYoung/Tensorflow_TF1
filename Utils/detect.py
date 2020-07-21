import os
import cv2
import numpy as np
import tensorflow as tf
from Models.models import PolypDetectionModel
import logging
from Models.dataset import PolypDataset
from Models.models import GenerateGrid


def get_single_image(image_path="../data/028.jpg"):
    imgs = cv2.imread(image_path, cv2.IMREAD_COLOR)
    imgs = cv2.resize(imgs, (227, 227))
    imgs = imgs.reshape((227, 227, 3))
    # BGR to RGB
    img_shape = imgs.shape
    imRGB = np.zeros((img_shape[0], img_shape[1], img_shape[2]), dtype=float)
    for i in range(imgs.shape[0]):
        for j in range(imgs.shape[1]):
            imRGB[i, j, 0] = imgs[i, j, 2]
            imRGB[i, j, 1] = imgs[i, j, 1]
            imRGB[i, j, 2] = imgs[i, j, 0]
    imRGB = imRGB/255.0
    imRGB = np.array([imRGB])
    return imgs, imRGB


def get_prediction(checkpoint_path, image):
    p = PolypDetectionModel()
    with tf.Graph().as_default():
        X = tf.placeholder(tf.float32, [None, 227, 227, 3], name="imGRBNormalize")
        output_0 = p.get_model(X, training=False)
        init = tf.global_variables_initializer()
        saver = tf.train.Saver()
        with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as sess:
            sess.run(init)
            saver.restore(sess, checkpoint_path)
            predictions = sess.run(output_0, feed_dict={X: image})
    return predictions


#    init = tf.global_variables_initializer()
#    global_step = tf.contrib.framework.get_or_create_global_step()
#    summary_op = tf.summary.merge_all()
#    with tf.Graph().as_default():
#        p = PolypDetectionModel(training=False)
#        X = tf.placeholder(tf.float32, [None, 227, 227, 3], name="imGRBNormalize")
#        model = p.get_model(X, training=False)
#        saver = tf.train.Saver()
#        with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as sess:
#            sess.run(init)
#            saver.restore(sess, checkpoint_path)
#            predictions = sess.run(model, feed_dict={X: image})
#            return predictions


def draw_outputs(input_img_path, outputs, class_names):
    img = cv2.imread(input_img_path, cv2.IMREAD_COLOR)
    boxes, objectness, classes, nums = outputs
    boxes, objectness, classes, nums = boxes[0], objectness[0], classes[0], nums[0]
    wh = np.flip(img.shape[0:2])
    for i in range(1):
        x1y1 = tuple((np.array(boxes[i][0:2]) * wh).astype(np.int32))
        x2y2 = tuple((np.array(boxes[i][2:4]) * wh).astype(np.int32))
        if x2y2[0] <= 0 or x2y2[1] <= 0:
            img = cv2.putText(img, "No Polyp".format(objectness[i]),
                              (20, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
            return img
        img = cv2.rectangle(img, x1y1, x2y2, (255, 0, 0), 2)
        img = cv2.putText(img, '{} {:.4f}'.format(
            class_names[int(classes[i])], objectness[i]),
            x1y1, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
    return img


def save_output(input_img_path, predictions, output_img_path):
    boxes, scores, classes, nums = predictions

    #objdetect = predictions[:, :, :, :, 0]
    #bndboxes = predictions[:, :, :, :, 1:]
    objdetect = predictions[1]
    bndboxes = predictions[0]

    max_pred = -100
    max_h = -1
    max_w = -1
    max_b = -1
    for h in range(0, objdetect.shape[1]):
        for w in range(0, objdetect.shape[2]):
            print(str(objdetect[0, h, w]))
            for b, pred in enumerate(objdetect[0, h, w]):
                if pred > max_pred:
                    max_pred = pred
                    max_h = h
                    max_w = w
                    max_b = b

    bndbox2 = {}
    grid_size = 67.5
    c_x = bndboxes[0, max_h, max_w, max_b, 0] * grid_size + grid_size*max_w
    c_y = bndboxes[0, max_h, max_w, max_b, 1] * grid_size + grid_size*max_h
    t_w = bndboxes[0, max_h, max_w, max_b, 2] * grid_size
    t_h = bndboxes[0, max_h, max_w, max_b, 3] * grid_size
    c_x_scale = int(c_x)
    c_y_scale = int(c_y)
    bndbox2['xmin'] = int(c_x - t_w / 2.0)
    bndbox2['xmax'] = int(c_x + t_w / 2.0)
    bndbox2['ymin'] = int(c_y - t_h / 2.0)
    bndbox2['ymax'] = int(c_y + t_h / 2.0)

    im = cv2.imread(input_img_path, cv2.IMREAD_COLOR)
    x1y1 = (bndbox2['xmin'], bndbox2['ymin'])
    x2y2 = (bndbox2['xmax'], bndbox2['ymax'])
    cv2.rectangle(im, x1y1, x2y2, (0, 255, 0), 2)
    im = cv2.putText(im, '{} {:.4f}'.format(
        "Polyp", max_pred),
                     x1y1, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
    cv2.imwrite(output_img_path, im)

    print('max_h: ' + str(max_h))
    print('max_w: ' + str(max_w))
    print('objdetect.shape: ' + str(objdetect.shape))
    print('bndboxes: ' + str(bndboxes[0, max_h, max_w]))
    print('bndbox2: ' + str([bndbox2['xmin'], bndbox2['ymin'], bndbox2['xmax'], bndbox2['ymax']]))


if __name__=="__main__":
    checkpoint_dir = "../results/model-400"
    image_path = "../data/028.jpg"
    image, img_rgb = get_single_image(image_path=image_path)
    predictions = get_prediction(checkpoint_dir, img_rgb)
    class_names = ["Polyp"]
    boxes, scores, classes, nums = predictions
    logging.info('detections:')
    for i in range(nums[0]):
        logging.info('\t{}, {}, {}'.format(class_names[int(classes[0][i])],
                                           np.array(scores[0][i]),
                                           np.array(boxes[0][i])))
    img = draw_outputs(input_img_path=image_path, outputs=predictions, class_names=["Polyp"])
    cv2.imwrite("output.jpg", img)
    #save_output("../data/028.jpg", predictions, "output.jpg")