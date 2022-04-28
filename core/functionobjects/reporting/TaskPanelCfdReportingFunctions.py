# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2022 Jonathan Bergh <bergh.jonathan@gmail.com>          *
# *   Copyright (c) 2022 Oliver Oxtoby <oliveroxtoby@gmail.com>             *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import os
import os.path
import FreeCAD
from FreeCAD import Units
import CfdTools
from CfdTools import getQuantity, setQuantity, indexOrDefault
from core.functionobjects.reporting import CfdReportingFunctions
if FreeCAD.GuiUp:
    import FreeCADGui


class TaskPanelCfdReportingFunctions:
    """
    Task panel for adding solver function objects
    """
    def __init__(self, obj):
        self.obj = obj
        self.analysis_obj = CfdTools.getActiveAnalysis()
        self.physics_obj = CfdTools.getPhysicsModel(self.analysis_obj)

        ui_path = os.path.join(os.path.dirname(__file__), "../../gui/TaskPanelCfdReportingFunctions.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        # Function Object types
        self.form.comboFunctionObjectType.addItems(CfdReportingFunctions.OBJECT_NAMES)
        self.form.comboFunctionObjectType.currentIndexChanged.connect(self.comboFunctionObjectTypeChanged)

        self.form.inputReferencePressure.setToolTip("Reference pressure")
        self.form.inputWriteFields.setToolTip("Write output fields")
        self.form.inputCentreOfRotationx.setToolTip("Centre of rotation vector for moments")

        self.form.inputLiftDirectionx.setToolTip("Lift direction vector")
        self.form.inputDragDirectionx.setToolTip("Drag direction vector")
        self.form.inputPitchAxisx.setToolTip("Pitch axis for moment coefficient")
        self.form.inputMagnitudeUInf.setToolTip("Velocity magnitude reference")
        self.form.inputReferenceDensity.setToolTip("Density reference")
        self.form.inputLengthRef.setToolTip("Length reference")
        self.form.inputAreaRef.setToolTip("Area reference")

        self.form.inputNBins.setToolTip("Number of bins")
        self.form.inputDirectionx.setToolTip("Binning direction")
        self.form.inputCumulative.setToolTip("Cumulative")
        self.form.cb_patch_list.setToolTip("Patch (BC) group to monitor")

        self.list_of_bcs = [bc.Label for bc in CfdTools.getCfdBoundaryGroup(self.analysis_obj)]
        self.form.cb_patch_list.addItems(self.list_of_bcs)

        self.load()
        self.updateUI()

    def load(self):
        bi = indexOrDefault(CfdReportingFunctions.OBJECT_NAMES, self.obj.ReportingFunctionType, 0)
        self.form.comboFunctionObjectType.setCurrentIndex(bi)
        self.comboFunctionObjectTypeChanged()
        
        if self.obj.Patch:
            index = self.list_of_bcs.index(self.obj.Patch.Label)
            self.form.cb_patch_list.setCurrentIndex(index)

        setQuantity(self.form.inputReferenceDensity, self.obj.ReferenceDensity)
        setQuantity(self.form.inputReferencePressure, self.obj.ReferencePressure)
        self.form.inputWriteFields.setChecked(self.obj.WriteFields)

        setQuantity(self.form.inputCentreOfRotationx, Units.Quantity(self.obj.CentreOfRotation.x, Units.Length))
        setQuantity(self.form.inputCentreOfRotationy, Units.Quantity(self.obj.CentreOfRotation.y, Units.Length))
        setQuantity(self.form.inputCentreOfRotationz, Units.Quantity(self.obj.CentreOfRotation.z, Units.Length))

        setQuantity(self.form.inputLiftDirectionx, self.obj.Lift.x)
        setQuantity(self.form.inputLiftDirectiony, self.obj.Lift.y)
        setQuantity(self.form.inputLiftDirectionz, self.obj.Lift.z)

        setQuantity(self.form.inputDragDirectionx, self.obj.Drag.x)
        setQuantity(self.form.inputDragDirectiony, self.obj.Drag.y)
        setQuantity(self.form.inputDragDirectionz, self.obj.Drag.z)

        setQuantity(self.form.inputPitchAxisx, self.obj.Pitch.x)
        setQuantity(self.form.inputPitchAxisy, self.obj.Pitch.y)
        setQuantity(self.form.inputPitchAxisz, self.obj.Pitch.z)

        setQuantity(self.form.inputMagnitudeUInf, self.obj.MagnitudeUInf)
        setQuantity(self.form.inputLengthRef, self.obj.LengthRef)
        setQuantity(self.form.inputAreaRef, self.obj.AreaRef)

        self.form.inputNBins.setValue(self.obj.NBins)
        setQuantity(self.form.inputDirectionx, self.obj.Direction.x)
        setQuantity(self.form.inputDirectiony, self.obj.Direction.y)
        setQuantity(self.form.inputDirectionz, self.obj.Direction.z)
        self.form.inputCumulative.setChecked(self.obj.Cumulative)

        self.form.inputFieldName.setText(self.obj.SampleFieldName)
        setQuantity(self.form.inputProbeLocx, Units.Quantity(self.obj.ProbePosition.x, Units.Length))
        setQuantity(self.form.inputProbeLocy, Units.Quantity(self.obj.ProbePosition.y, Units.Length))
        setQuantity(self.form.inputProbeLocz, Units.Quantity(self.obj.ProbePosition.z, Units.Length))

    def updateUI(self):
        # Function object type
        type_index = self.form.comboFunctionObjectType.currentIndex()
        self.form.stackedWidget.setCurrentIndex(CfdReportingFunctions.FUNCTIONS_UI[type_index])
        if type_index < len(CfdReportingFunctions.FORCES_UI):
            field_name_frame_enabled = CfdReportingFunctions.FORCES_UI[type_index][0]
            coefficient_frame_enabled = CfdReportingFunctions.FORCES_UI[type_index][1]
            spatial_bin_frame_enabled = CfdReportingFunctions.FORCES_UI[type_index][2]
            self.form.fieldNamesFrame.setVisible(field_name_frame_enabled)
            self.form.coefficientFrame.setVisible(coefficient_frame_enabled)
            self.form.spatialFrame.setVisible(spatial_bin_frame_enabled)

        if self.physics_obj.Flow == 'Incompressible':
            self.form.inputReferenceDensity.setVisible(False)
            self.form.labelRefDensity.setVisible(False)
        else:
            self.form.inputReferenceDensity.setVisible(True)
            self.form.labelRefDensity.setVisible(True)

    def comboFunctionObjectTypeChanged(self):
        index = self.form.comboFunctionObjectType.currentIndex()
        self.form.functionObjectDescription.setText(CfdReportingFunctions.OBJECT_DESCRIPTIONS[index])
        self.updateUI()

    def accept(self):
        FreeCADGui.Selection.removeObserver(self)

        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()

        FreeCADGui.doCommand("\nfo = FreeCAD.ActiveDocument.{}".format(self.obj.Name))
        # Type
        index = self.form.comboFunctionObjectType.currentIndex()
        FreeCADGui.doCommand("fo.ReportingFunctionType = '{}'".format(
                                 CfdReportingFunctions.OBJECT_NAMES[self.form.comboFunctionObjectType.currentIndex()]))

        bcs = CfdTools.getCfdBoundaryGroup(self.analysis_obj)
        FreeCADGui.doCommand("fo.Patch "
                             "= FreeCAD.ActiveDocument.{}".format(bcs[self.form.cb_patch_list.currentIndex()].Name))

        # Force object
        FreeCADGui.doCommand("fo.ReferenceDensity "
                             "= '{}'".format(getQuantity(self.form.inputReferenceDensity)))
        FreeCADGui.doCommand("fo.ReferencePressure "
                             "= '{}'".format(getQuantity(self.form.inputReferencePressure)))
        FreeCADGui.doCommand("fo.WriteFields "
                             "= {}".format(self.form.inputWriteFields.isChecked()))
        FreeCADGui.doCommand("fo.CentreOfRotation.x "
                             "= {}".format(self.form.inputCentreOfRotationx.property("quantity").Value))
        FreeCADGui.doCommand("fo.CentreOfRotation.y "
                             "= {}".format(self.form.inputCentreOfRotationy.property("quantity").Value))
        FreeCADGui.doCommand("fo.CentreOfRotation.z "
                             "= {}".format(self.form.inputCentreOfRotationz.property("quantity").Value))

        # # Coefficient object
        FreeCADGui.doCommand("fo.Lift.x "
                             "= {}".format(self.form.inputLiftDirectionx.property("quantity").Value))
        FreeCADGui.doCommand("fo.Lift.y "
                             "= {}".format(self.form.inputLiftDirectiony.property("quantity").Value))
        FreeCADGui.doCommand("fo.Lift.z "
                             "= {}".format(self.form.inputLiftDirectionz.property("quantity").Value))
        FreeCADGui.doCommand("fo.Drag.x "
                             "= {}".format(self.form.inputDragDirectionx.property("quantity").Value))
        FreeCADGui.doCommand("fo.Drag.y "
                             "= {}".format(self.form.inputDragDirectiony.property("quantity").Value))
        FreeCADGui.doCommand("fo.Drag.z "
                             "= {}".format(self.form.inputDragDirectionz.property("quantity").Value))
        FreeCADGui.doCommand("fo.Pitch.x "
                             "= {}".format(self.form.inputPitchAxisx.property("quantity").Value))
        FreeCADGui.doCommand("fo.Pitch.y "
                             "= {}".format(self.form.inputPitchAxisy.property("quantity").Value))
        FreeCADGui.doCommand("fo.Pitch.z "
                             "= {}".format(self.form.inputPitchAxisz.property("quantity").Value))
        FreeCADGui.doCommand("fo.MagnitudeUInf "
                             "= '{}'".format(getQuantity(self.form.inputMagnitudeUInf)))
        FreeCADGui.doCommand("fo.LengthRef "
                             "= '{}'".format(getQuantity(self.form.inputLengthRef)))
        FreeCADGui.doCommand("fo.AreaRef "
                             "= '{}'".format(getQuantity(self.form.inputAreaRef)))

        # # Spatial binning
        FreeCADGui.doCommand("fo.NBins "
                             "= {}".format(self.form.inputNBins.value()))
        FreeCADGui.doCommand("fo.Direction.x "
                             "= '{}'".format(self.form.inputDirectionx.property("quantity").Value))
        FreeCADGui.doCommand("fo.Direction.y "
                             "= '{}'".format(self.form.inputDirectiony.property("quantity").Value))
        FreeCADGui.doCommand("fo.Direction.z "
                             "= '{}'".format(self.form.inputDirectionz.property("quantity").Value))
        FreeCADGui.doCommand("fo.Cumulative "
                             "= {}".format(self.form.inputCumulative.isChecked()))

        # Probe info
        FreeCADGui.doCommand("fo.SampleFieldName "
                             "= '{}'".format(self.form.inputFieldName.text()))
        FreeCADGui.doCommand("fo.ProbePosition.x "
                             "= {}".format(self.form.inputProbeLocx.property("quantity").Value))
        FreeCADGui.doCommand("fo.ProbePosition.y "
                             "= {}".format(self.form.inputProbeLocy.property("quantity").Value))
        FreeCADGui.doCommand("fo.ProbePosition.z "
                             "= {}".format(self.form.inputProbeLocz.property("quantity").Value))

        # Finalise
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")

    def reject(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True