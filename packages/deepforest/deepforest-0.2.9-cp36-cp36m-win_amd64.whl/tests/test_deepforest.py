#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `deepforest` package."""
import os
import sys
import pytest
import keras
import glob
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from deepforest import deepforest
from deepforest import preprocess
from deepforest import utilities
from deepforest import tfrecords
from deepforest import get_data

#download latest release
@pytest.fixture()
def download_release():
    print("running fixtures")
    utilities.use_release()    
    
@pytest.fixture()
def annotations():
    annotations = utilities.xml_to_annotations(get_data("OSBS_029.xml"))
    #Point at the jpg version for tfrecords
    annotations.image_path = annotations.image_path.str.replace(".tif",".jpg")
    
    annotations_file = get_data("testfile_deepforest.csv")
    annotations.to_csv(annotations_file,index=False,header=False)
    
    return annotations_file

@pytest.fixture()
def prepare_tfdataset(annotations):    
    records_created = tfrecords.create_tfrecords(annotations_file=annotations, class_file="tests/data/classes.csv", image_min_side=800, backbone_model="resnet50", size=100, savedir="tests/data/")
    assert os.path.exists("tests/data/testfile_deepforest_0.tfrecord")
    return records_created

def test_deepforest():
    model = deepforest.deepforest(weights=None)
    assert model.weights is None

def test_use_release(download_release):
    test_model = deepforest.deepforest() 
    test_model.use_release()
    
    #Check for release tag
    assert isinstance(test_model.__release_version__, str)
    
    #Assert is model instance    
    assert isinstance(test_model.model,keras.models.Model)
    
    assert test_model.config["weights"] == test_model.weights 
    assert test_model.config["weights"] is not "None"
    
@pytest.fixture()
def release_model(download_release):
    test_model = deepforest.deepforest() 
    test_model.use_release()
    
    #Check for release tag
    assert isinstance(test_model.__release_version__, str)
    
    #Assert is model instance    
    assert isinstance(test_model.model,keras.models.Model)
    
    return test_model

def test_predict_image(download_release):
    #Load model
    test_model = deepforest.deepforest(weights=get_data("NEON.h5"))    
    assert isinstance(test_model.model,keras.models.Model)
    
    #Predict test image and return boxes
    boxes = test_model.predict_image(image_path=get_data("OSBS_029.tif"), show=False, return_plot = False)
    
    #Returns a 6 column numpy array, xmin, ymin, xmax, ymax, score, label
    assert boxes.shape[1] == 6

@pytest.fixture()
def test_train(annotations):
    test_model = deepforest.deepforest()
    test_model.config["epochs"] = 1
    test_model.config["save-snapshot"] = False
    test_model.config["steps"] = 1
    test_model.train(annotations=annotations, input_type="fit_generator")
    
    return test_model

def test_predict_generator(release_model, annotations):
    boxes = release_model.predict_generator(annotations=annotations)
    assert boxes.shape[1] == 7
    
#Test random transform
def test_random_transform(annotations):
    test_model = deepforest.deepforest()
    test_model.config["random_transform"] = True
    arg_list = utilities.format_args(annotations, test_model.config)
    assert "--random-transform" in arg_list

def test_predict_tile(release_model):
    raster_path = get_data("OSBS_029.tif")
    image = release_model.predict_tile(raster_path,patch_size=300,patch_overlap=0.5,return_plot=True)
        
def test_retrain_release(annotations, release_model):
    release_model.config["epochs"] = 1
    release_model.config["save-snapshot"] = False
    release_model.config["steps"] = 1
    
    assert release_model.config["weights"] == release_model.weights
    
    #test that it gets passed to retinanet
    arg_list = utilities.format_args(annotations, release_model.config, images_per_epoch=1)
    strs = ["--weights" == x for x in arg_list]
    index = np.where(strs)[0][0] + 1
    arg_list[index] == release_model.weights