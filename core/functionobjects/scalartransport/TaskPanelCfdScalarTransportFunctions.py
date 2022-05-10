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

import FreeCAD
import os
import os.path
import CfdTools
from CfdTools import getQuantity, setQuantity
if FreeCAD.GuiUp:
    import FreeCADGui


class TaskPanelCfdScalarTransportFunctions:
    """
    Task panel for adding solver scalar transport function objects
    """
    def __init__(self, obj):
        self.obj = obj
        self.analysis_obj = CfdTools.getActiveAnalysis()

        ui_path = os.path.join(os.path.dirname(__file__), "../../gui/TaskPanelCfdScalarTransportFunctions.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.load()
        self.updateUI()

    def load(self):
        self.form.inputScalarFieldName.setText(self.obj.FieldName)
        if self.obj.DiffusivityFixed:
            self.form.radioUniformDiffusivity.toggle()
        else:
            self.form.radioViscousDiffusivity.toggle()
        setQuantity(self.form.inputDiffusivity, self.obj.DiffusivityFixedValue)

        setQuantity(self.form.inputInjectionPointx, self.obj.InjectionPoint.x)
        setQuantity(self.form.inputInjectionPointy, self.obj.InjectionPoint.y)
        setQuantity(self.form.inputInjectionPointz, self.obj.InjectionPoint.z)

        setQuantity(self.form.inputInjectionRate, self.obj.InjectionRate)

    def updateUI(self):
        pass

    def accept(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()

        FreeCADGui.doCommand("\nfo = FreeCAD.ActiveDocument.{}".format(self.obj.Name))
        # Type
        FreeCADGui.doCommand("fo.FieldName "
                             "= '{}'".format(self.form.inputScalarFieldName.text()))
        FreeCADGui.doCommand("fo.DiffusivityFixed "
                             "= {}".format(self.form.radioUniformDiffusivity.isChecked()))
        FreeCADGui.doCommand("fo.DiffusivityFixedValue "
                             "= '{}'".format(getQuantity(self.form.inputDiffusivity)))

        FreeCADGui.doCommand("fo.InjectionPoint.x "
                             "= '{}'".format(self.form.inputInjectionPointx.property("quantity").Value))
        FreeCADGui.doCommand("fo.InjectionPoint.y "
                             "= '{}'".format(self.form.inputInjectionPointy.property("quantity").Value))
        FreeCADGui.doCommand("fo.InjectionPoint.z "
                             "= '{}'".format(self.form.inputInjectionPointz.property("quantity").Value))
        FreeCADGui.doCommand("fo.InjectionRate "
                             "= '{}'".format(getQuantity(self.form.inputInjectionRate)))

        # Finalise
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")

    def reject(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
