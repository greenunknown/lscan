# Copyright (C) 2018 - This notice is to be included in all relevant source files.
# "Brandon Goldbeck" <bpg@pdx.edu>
# “Anthony Namba” <anamba@pdx.edu>
# “Brandon Le” <lebran@pdx.edu>
# “Ann Peake” <peakean@pdx.edu>
# “Sohan Tamang” <sohan@pdx.edu>
# “An Huynh” <an35@pdx.edu>
# “Theron Anderson” <atheron@pdx.edu>
# This software is licensed under the MIT License. See LICENSE file for the full text.

from src.threading.base_job import BaseJob
from src.log_messages.log_type import LogType
from src.log_messages.log_message import LogMessage
from src.log_messages.output_model_message import OutputModelMessage
from src.model_conversion.ldraw_model import LDrawModel
from src.model_conversion.model_shipper import ModelShipper
from stl import Mesh
import numpy
import copy


class ConvertJob(BaseJob):
    """This job converts the input mesh into LDraw text and stores it in
    ModelShipper.output_file so it can be saved later.
    """
    def __init__(self, feedback_log):
        super().__init__(feedback_log)

    def do_job(self):
        self.put_feedback(LogMessage(LogType.DEBUG, "Starting conversion job"))

        self.is_running.wait()
        # Setting output model as input LDraw object
        model = None # LDraw model
        mesh = None # mesh in LDraw model
        children = None
        if not self.is_killed:
            ModelShipper.output_model = copy.deepcopy(ModelShipper.input_model)
            model = ModelShipper.output_model
            mesh = model.get_mesh()
            children = model.get_children()

        self.is_running.wait()
        if not self.is_killed:
            # Write out the model name.
            if model.get_name() != "":
                ModelShipper.output_file = ("0 " + "LScan auto generated part " + model.get_name() + "\n")
                ModelShipper.output_file += ("0 " + "Name: " + model.get_name() + "\n")

        self.is_running.wait()
        if not self.is_killed:
            # Write out the author name.
            if model.get_author() != "":
                ModelShipper.output_file += ("0 " + "Author: " + model.get_author() + "\n")

        self.is_running.wait()
        if not self.is_killed:
            # Write out the license
            if model.get_name() != "":
                ModelShipper.output_file += ("0 " + "!LICENSE " + model.get_license_info() + "\n")

        for i in range(len(mesh.normals)):
            # Write out line 3 types for main mesh
            self.is_running.wait()
            if self.is_killed:
                break
            # Export vertices information in ldraw format
            ModelShipper.output_file += ("3 4 " + str(mesh.v2[i][0])
                                         + " " + str(mesh.v2[i][1])
                                         + " " + str(mesh.v2[i][2])
                                         + " " + str(mesh.v1[i][0])
                                         + " " + str(mesh.v1[i][1])
                                         + " " + str(mesh.v1[i][2])
                                         + " " + str(mesh.v0[i][0])
                                         + " " + str(mesh.v0[i][1])
                                         + " " + str(mesh.v0[i][2])
                                         + "\n")

        for i in range(len(model.get_children())):
            # For each child mesh
            self.is_running.wait()
            if self.is_killed:
                break

            for j in range(len(children[i].normals)):
                # For each normal in this child mesh
                self.is_running.wait()
                if self.is_killed:
                    break
                # Export vertices information in ldraw format
                ModelShipper.output_file += ("3 4 " + str(mesh.v2[j][0])
                                             + " " + str(mesh.v2[j][1])
                                             + " " + str(mesh.v2[j][2])
                                             + " " + str(mesh.v1[j][0])
                                             + " " + str(mesh.v1[j][1])
                                             + " " + str(mesh.v1[j][2])
                                             + " " + str(mesh.v0[j][0])
                                             + " " + str(mesh.v0[j][1])
                                             + " " + str(mesh.v0[j][2])
                                             + "\n")

        self.is_running.wait()
        if not self.is_killed: # Job completed (not killed)
            fake_mesh = Mesh(numpy.zeros(3, dtype=Mesh.dtype),
                                  remove_empty_areas=False)
            fake_model = LDrawModel("", "", "", fake_mesh)
            self.put_feedback(LogMessage(LogType.DEBUG, "Finished conversion job"))

            self.put_feedback(OutputModelMessage(LogType.INFORMATION,
                                                 "Conversion Complete. Ready to Save.",
                                                 fake_model))
        else: # Job was killed
            #do any cleanup before exiting
            self.put_feedback(LogMessage(LogType.DEBUG,
                                         "Cancelled during conversion job"))

        self.is_done.set()  # Set this so thread manager knows job is done