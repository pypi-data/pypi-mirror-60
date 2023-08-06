#Data : 2019-12-13
#Author : Fengyuan Zhang (Franklin)
#Email : franklinzhang@foxmail.com
#Description : this engine aims to convert BMI component to OpenGMS service package

import sys
import numpy as np
import json
import os
import importlib
import uuid
import random
import shutil
import zipfile
import tempfile
from .mdl_python import ModelClass, Category, LocalAttribute, ModelDatasetItem, ModelEvent, ModelParameter, ModelState, ModelStateTransition, RequriementConfig, SoftwareConfig

def zipDir(dirpath, outFullName):
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        fpath = path.replace(dirpath, '')
        if fpath != "":
            zip.write(path, fpath)
        for filename in filenames:
            zip.write(os.path.join(path, filename),os.path.join(fpath, filename))
    zip.close()

def getDirAndCopyFile(sourcePath,targetPath):
    if not os.path.exists(sourcePath):
        return
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)
    for fileName in os.listdir(sourcePath):
        absourcePath = os.path.join(sourcePath, fileName)
        abstargetPath = os.path.join(targetPath, fileName)
        if os.path.isdir(absourcePath):
            if not os.path.exists(targetPath):
                os.makedirs(abstargetPath)
            else:
                getDirAndCopyFile(absourcePath,abstargetPath)
        if os.path.isfile(absourcePath):
            rbf = open(absourcePath,"rb")
            wbf = open(abstargetPath,"wb")
            while True:
                content = rbf.readline(1024*1024)
                if len(content)==0:
                    break
                wbf.write(content)
                wbf.flush()
            rbf.close()
            wbf.close()

def copyFileOrDir(fullpath, target):
    if os.path.isdir(fullpath):
        getDirAndCopyFile(fullpath, target)
    else:
        shutil.copyfile(fullpath, target)
        
class BMIOpenGMSEngine():
    @staticmethod
    def convertBMI2OpenGMS(bmiComponent, componentName, supplement = None):
        #! import model component
        filename = bmiComponent
        model = componentName
        workdir = os.path.dirname(filename)
        os.chdir(workdir)
        filename = os.path.basename(filename)
        modulename = filename

        if supplement:
            f = open(supplement, "r")
            supplement = json.load(f)
            f.close()
        else:
            supplement = {}

        if os.path.isdir(filename):
            BmiModel = importlib.import_module(modulename)
            modulename = filename
        else:
            modulename = os.path.splitext(modulename)[0]
            BmiModel = importlib.import_module(modulename)

        bmi_model = getattr(BmiModel, model)()

        #! check model component, must have (part of) BMI functions (depend on what OpenGMS need)
        if not hasattr(bmi_model, "get_component_name"):
            print("This model component don't follow BMI standard : get_component_name")
            exit()

        if not hasattr(bmi_model, "get_input_var_names"):
            print("This model component don't follow BMI standard : get_input_var_names")
            exit()

        if not hasattr(bmi_model, "get_value"):
            print("This model component don't follow BMI standard : get_value")
            exit()

        if not hasattr(bmi_model, "set_value"):
            print("This model component don't follow BMI standard : set_value")
            exit()
            
        if not hasattr(bmi_model, "update"):
            print("This model component don't follow BMI standard : update")
            exit()
            
        if not hasattr(bmi_model, "initialize"):
            print("This model component don't follow BMI standard : initialize")
            exit()

        if not hasattr(bmi_model, "finalize"):
            print("This model component don't follow BMI standard : finalize")
            exit()

        #! start to organize MDL
        modelName = bmi_model.get_component_name()

        bmi_mdl = ModelClass(modelName, str(uuid.uuid4()), "SimpleCalculation")

        attr = bmi_mdl.getModelAttribute()
        wiki = "http://www.opengms.com.cn"
        keywords = []
        description = modelName

        if supplement and supplement["AttibuteSet"]:
            if supplement["AttibuteSet"]["Description"]:
                description = supplement["AttibuteSet"]["Description"]
            
            if supplement["AttibuteSet"]["Wiki"]:
                wiki = supplement["AttibuteSet"]["Wiki"]

            if supplement["AttibuteSet"]["Keywords"]:
                keywords = supplement["AttibuteSet"]["keywords"]

        localAttr_EN = LocalAttribute("EN", modelName, wiki, keywords, description)
        attr.addLocalAttributeInfo(localAttr_EN)

        if supplement and supplement["AttibuteSet"] and supplement["AttibuteSet"]["Category"] and supplement["AttibuteSet"]["Category"]["Principle"] and supplement["AttibuteSet"]["Category"]["Path"]:
            cate = Category(supplement["AttibuteSet"]["Category"]["Principle"], supplement["AttibuteSet"]["Category"]["Path"])
        else:
            cate = Category("BMIModel", "[Unknown]")

        attr.addCategoryInfo(cate)

        behavior = bmi_mdl.getBehavior()

        init_tmp = ModelDatasetItem("InitFile", "external", "Init file template", str(uuid.uuid4()))
        behavior.addModelDatasetItem(init_tmp)

        ipts = bmi_model.get_input_var_names()
        for ipt in ipts:
            unknown_tmp = ModelDatasetItem(modelName + "_Unknown", "external", modelName + " template", uuid.uuid4())
            behavior.addModelDatasetItem(init_tmp)

        state1 = ModelState(str(uuid.uuid4()), "BMIRUNNING", "basic", "BMI running state")
        event_init = ModelEvent("Init", "response", "initialized file", "InitFile", "initialized file", True)
        state1.events.append(event_init)

        ipts = bmi_model.get_input_var_names()
        for ipt in ipts:
            event = ModelEvent("INPUT_" + ipt, "response", "input " + ipt, modelName + "_Unknown", "input of " + ipt, False)
            state1.events.append(event)

        opts = bmi_model.get_output_var_names()
        for opt in opts:
            event = ModelEvent("OUTPUT_" + opt, "noresponse", "output " + opt, modelName + "_Unknown", "output of " + opt, False)
            state1.events.append(event)

        behavior.addModelState(state1)

        runtime = bmi_mdl.getRuntime()

        runtime.setBaseDirectory("$(ModelServicePath)\\")
        runtime.setEntry("bmi_" + model + ".py")

        version = "1.0.0.0"
        if supplement and supplement["Runtime"]:
            if supplement["Runtime"]["Version"]:
                version = supplement["Runtime"]["Version"]
            if supplement["Runtime"]["HardwareConfigures"]:
                for hc in supplement["Runtime"]["HardwareConfigures"]:
                    runtime.addHardwareRequirement(RequriementConfig(hc["key"], hc["value"]))
            if supplement["Runtime"]["SoftwareConfigures"]:
                for sc in supplement["Runtime"]["SoftwareConfigures"]:
                    runtime.addSoftwareRequirement(SoftwareConfig(sc["key"], sc["value"], sc["platform"]))
            if supplement["Runtime"]["Assemblies"]:
                for ab in supplement["Runtime"]["Assemblies"]:
                    runtime.addModelAssembly(RequriementConfig(ab["key"], ab["value"]))
            
        runtime.setVersion(version)
        runtime.addHardwareRequirement(RequriementConfig("Main Frequency", "1.0"))
        runtime.addHardwareRequirement(RequriementConfig("Memory Size", "1024MB"))


        #! generate working directories
        # tmpdirs = random.sample('zyxwvutsrqponmlkjihgfedcba',6)
        # dirname = workdir + "/temp_"
        # for tmpdir in tmpdirs:
        #     dirname = dirname + tmpdir
        dirname = tempfile.TemporaryDirectory().name
        resourceDir = os.path.dirname(__file__) + "/resource"


        #! generate file tree
        os.mkdir(dirname)
        os.mkdir(dirname + "/model")
        os.mkdir(dirname + "/assembly")
        os.mkdir(dirname + "/testify")
        os.mkdir(dirname + "/supportive")
        shutil.copyfile(resourceDir + "/license.txt", dirname + "/license.txt")

        #! generate setup file
        ft = open(resourceDir + "/template/init.pyt", "r")
        content = ft.read()
        ft.close()

        content = content.replace("$(File)", modulename)
        content = content.replace("$(Class)", model)

        fm = open(dirname + "/model/bmi_" + model + ".py", "w")
        fm.write(content)
        fm.close()

        #! copy files
        fullpath = bmiComponent
        target = dirname + "/model/" + filename
        copyFileOrDir(fullpath, target)
        getDirAndCopyFile(resourceDir + "/bmi", dirname + "/model/bmi")
        shutil.copyfile(resourceDir + "/modeldatahandler.py", dirname + "/model/modeldatahandler.py")
        shutil.copyfile(resourceDir + "/modelservicecontext.py", dirname + "/model/modelservicecontext.py")

        if supplement and supplement["AdditionFiles"]:
            for afile in supplement["AdditionFiles"]:
                fullpath = afile
                target = dirname + "/model/" + os.path.basename(afile)
                copyFileOrDir(fullpath, target)

        #! generate MDL file
        bmi_mdl.formatToXMLFile(dirname + "/model/bmi_" + model + ".mdl")

        #! wrap and compress package
        # os.chdir(dirname)
        zipDir(dirname, os.path.dirname(bmiComponent) + "/bmi_" + model + ".zip")

        #! clear temp files
        shutil.rmtree(dirname, ignore_errors=True)