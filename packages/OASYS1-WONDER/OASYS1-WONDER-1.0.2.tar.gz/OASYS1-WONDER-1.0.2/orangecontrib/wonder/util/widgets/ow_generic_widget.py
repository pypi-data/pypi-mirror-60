import sys, numpy, os

from oasys.widgets import widget

from orangewidget import gui as orangegui
from orangewidget.settings import Setting

from PyQt5.QtWidgets import QApplication, QSizePolicy
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QDoubleValidator, QValidator

from orangecontrib.wonder.util.gui.gui_utility import ConfirmDialog, gui, ShowTextDialog, OW_IS_DEVELOP
from orangecontrib.wonder.controller.fit.fit_parameter import FitParameter, Boundary
from orangecontrib.wonder.controller.fit.fit_parameter import PARAM_HWMAX, PARAM_HWMIN

class QMinValueValidator(QDoubleValidator):

    def __init__(self, min_value, max_value=None, min_accepted=True, parent=None):
        super().__init__(parent)
        self.__min_value = min_value
        self.__max_value = max_value
        self.__min_accepted = min_accepted

    def validate(self, string, pos):
        try:
            value = float(string)
        except:
            return (QValidator.Invalid, string, pos)

        good = True
        if not self.__min_accepted              : good = value > self.__min_value
        if good and self.__min_accepted         : good = value >= self.__min_value
        if good and not self.__max_value is None: good = value <= self.__max_value

        if good:
            return (QValidator.Acceptable, string, pos)
        else:
            return (QValidator.Invalid, string, pos)

class QMaxValueValidator(QDoubleValidator):

    def __init__(self, max_value, min_value=None, max_accepted=True, parent=None):
        super(QDoubleValidator, self).__init__(parent)
        self.__max_value = max_value
        self.__min_value = min_value
        self.__max_accepted = max_accepted

    def validate(self, string, pos):
        try:
            value = float(string)
        except:
            return (QValidator.Invalid, string, pos)

        good = True
        if not self.__max_accepted              : good = value < self.__max_value
        if good and self.__max_accepted         : good = value <= self.__max_value
        if good and not self.__min_value is None: good = value >= self.__min_value

        if good:
            return (QValidator.Acceptable, string, pos)
        else:
            return (QValidator.Invalid, string, pos)

class OWGenericWidget(widget.OWWidget):

    want_main_area=1

    is_automatic_run = Setting(True)

    error_id = 0
    warning_id = 0
    info_id = 0

    MAX_WIDTH = 1320
    MAX_WIDTH_NO_MAIN = 510
    MAX_HEIGHT = 700

    CONTROL_AREA_WIDTH = 505
    TABS_AREA_HEIGHT = 560

    fit_global_parameters = None
    parameter_functions = {}

    IS_DEVELOP = OW_IS_DEVELOP

    def __init__(self, show_automatic_box=True):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()

        if self.want_main_area:
            max_width = self.MAX_WIDTH
        else:
            max_width = self.MAX_WIDTH_NO_MAIN

        self.setGeometry(QRect(round(geom.width()*0.01),
                               round(geom.height()*0.01),
                               round(min(geom.width()*0.95, max_width)),
                               round(min(geom.height()*0.95, self.MAX_HEIGHT))))

        self.setMinimumWidth(self.geometry().width()/2)
        self.setMinimumHeight(self.geometry().height()/2)
        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        self.general_options_box = gui.widgetBox(self.controlArea, "General Options", addSpace=True, orientation="horizontal")

        if show_automatic_box :
            orangegui.checkBox(self.general_options_box, self, 'is_automatic_run', 'Automatic')

        gui.button(self.general_options_box, self, "Reset Fields", callback=self.callResetSettings)
        gui.button(self.general_options_box, self, "Show Available Parameters", callback=self.show_available_parameters)

    @classmethod
    def fix_flag(cls, flag):
        if type(flag) == bool: flag=1 if flag==True else 0

        return flag

    def create_box(self, parent_box, var, label=None, disable_function=False, add_callback=False, label_width=40, min_value=None, min_accepted=True, max_value=None, max_accepted=True, trim=50):
        OWGenericWidget.create_box_in_widget(self, parent_box, var, label, disable_function, add_callback, label_width, min_value, min_accepted, max_value, max_accepted, trim)

    @classmethod
    def create_box_in_widget(cls, widget, parent_box, var, label=None, disable_function=False, add_callback=False, label_width=40, min_value=None, min_accepted=True, max_value=None, max_accepted=True, trim=50):
        box = gui.widgetBox(parent_box, "", orientation="horizontal", width=widget.CONTROL_AREA_WIDTH - trim, height=25)

        box_value_width = 100 - (label_width-40)

        box_label = gui.widgetBox(box, "", orientation="horizontal", width=label_width, height=25)
        box_value =  gui.widgetBox(box, "", orientation="horizontal", width=box_value_width, height=25)
        box_fixed = gui.widgetBox(box, "", orientation="horizontal", height=25)
        box_min_max = gui.widgetBox(box, "", orientation="horizontal", height=30)
        box_function = gui.widgetBox(box, "", orientation="horizontal", height=25)
        box_function_value = gui.widgetBox(box, "", orientation="horizontal", height=25)

        gui.widgetLabel(box_label, var if label is None else label)
        if add_callback: le_var = gui.lineEdit(box_value, widget, var, " ", labelWidth=0, valueType=float, validator=QDoubleValidator(), callback=getattr(widget, "callback_" + var))
        else: le_var = gui.lineEdit(box_value, widget, var, " ", labelWidth=0, valueType=float, validator=QDoubleValidator())

        def set_flags():
            fixed = getattr(widget, var + "_fixed") == 1
            function = getattr(widget, var + "_function") == 1
            if disable_function:
                function = False
                setattr(widget, var + "_function", 0)

            if function:
                setattr(widget, var + "_fixed", 0)

                box_min_max.setVisible(False)
                box_fixed.setVisible(False)
                le_var.setVisible(False)
                box_value.setFixedWidth(5)
                box_function.setVisible(True)
                box_function_value.setVisible(True)
            elif fixed:
                setattr(widget, var + "_function", 0)

                box_min_max.setVisible(False)
                box_fixed.setVisible(True)
                le_var.setVisible(True)
                box_value.setFixedWidth(box_value_width)
                box_function.setVisible(False)
                box_function_value.setVisible(False)
            else:
                setattr(widget, var + "_fixed", 0)
                setattr(widget, var + "_function", 0)

                box_min_max.setVisible(True)
                box_fixed.setVisible(True)
                le_var.setVisible(True)
                box_value.setFixedWidth(box_value_width)
                box_function.setVisible(True)
                box_function_value.setVisible(False)

            if add_callback: getattr(widget, "callback_" + var)()

        widget.parameter_functions[var] = set_flags

        orangegui.checkBox(box_fixed, widget, var + "_fixed", "fix", callback=set_flags)

        def set_min():
            setattr(widget, var + "_has_min", 1)
            if add_callback: getattr(widget, "callback_" + var)()

        def set_max():
            setattr(widget, var + "_has_max", 1)
            if add_callback: getattr(widget, "callback_" + var)()

        min_validator = QMinValueValidator(min_value, max_value, min_accepted) if not min_value is None else (QDoubleValidator() if max_value is None else QMaxValueValidator(max_value, min_value, True))
        max_validator = QMaxValueValidator(max_value, min_value, max_accepted) if not max_value is None else (QDoubleValidator() if min_value is None else QMinValueValidator(min_value, max_value, True))

        if add_callback:
            cb_min = orangegui.checkBox(box_min_max, widget, var + "_has_min", "min", callback=getattr(widget, "callback_" + var))
            gui.lineEdit(box_min_max, widget, var + "_min", " ", labelWidth=0, valueType=float, validator=min_validator, callback=set_min)
            cb_max = orangegui.checkBox(box_min_max, widget, var + "_has_max", "max", callback=getattr(widget, "callback_" + var))
            gui.lineEdit(box_min_max, widget, var + "_max", " ", labelWidth=0, valueType=float, validator=max_validator, callback=set_max)

            cb = orangegui.checkBox(box_function, widget, var + "_function", "f(x)", callback=set_flags)
            cb.setEnabled(not disable_function)

            gui.lineEdit(box_function_value, widget, var + "_function_value", "expression", valueType=str, callback=getattr(widget, "callback_" + var))
        else:
            cb_min = orangegui.checkBox(box_min_max, widget, var + "_has_min", "min")
            gui.lineEdit(box_min_max, widget, var + "_min", " ", labelWidth=0, valueType=float, validator=min_validator, callback=set_min)
            cb_max = orangegui.checkBox(box_min_max, widget, var + "_has_max", "max")
            gui.lineEdit(box_min_max, widget, var + "_max", " ", labelWidth=0, valueType=float, validator=max_validator, callback=set_max)

            cb = orangegui.checkBox(box_function, widget, var + "_function", "f(x)", callback=set_flags)
            cb.setEnabled(not disable_function)

            gui.lineEdit(box_function_value, widget, var + "_function_value", "expression", valueType=str)

        if not min_value is None:
            setattr(widget, var + "_has_min", 1)
            setattr(widget, var + "_min", min_value)
            cb_min.setEnabled(False)

        if not max_value is None:
            setattr(widget, var + "_has_max", 1)
            setattr(widget, var + "_max", max_value)
            cb_max.setEnabled(False)

        set_flags()

    def populate_parameter(self, parameter_name, parameter_prefix, parameter_suffix = ""):
        return self.populate_parameter_in_widget(self, parameter_name, parameter_prefix, parameter_suffix)
    
    @classmethod
    def populate_parameter_in_widget(cls, widget, parameter_name, parameter_prefix, parameter_suffix = ""):
        if hasattr(widget, parameter_name + "_function") and getattr(widget, parameter_name + "_function") == 1:
            return FitParameter(parameter_name=parameter_prefix + parameter_name + parameter_suffix, function=True, function_value=getattr(widget, parameter_name + "_function_value"))
        elif getattr(widget, parameter_name + "_fixed") == 1:
            return FitParameter(parameter_name=parameter_prefix + parameter_name + parameter_suffix, value=getattr(widget, parameter_name), fixed=True)
        else:
            boundary = None

            min_value = PARAM_HWMIN
            max_value = PARAM_HWMAX

            if getattr(widget, parameter_name + "_has_min") == 1: min_value = getattr(widget, parameter_name + "_min")
            if getattr(widget, parameter_name + "_has_max") == 1: max_value = getattr(widget, parameter_name + "_max")

            if min_value != PARAM_HWMIN or max_value != PARAM_HWMAX:
                boundary = Boundary(min_value=min_value, max_value=max_value)

            return FitParameter(parameter_name=parameter_prefix + parameter_name, value=getattr(widget, parameter_name), boundary=boundary)

    def populate_fields(self, var, parameter, value_only=True):
        self.populate_fields_in_widget(self, var, parameter, value_only)
        
    @classmethod
    def populate_fields_in_widget(cls, widget, var, parameter, value_only=True):

        setattr(widget, var, round(parameter.value, 8) if not parameter.value is None else 0.0)

        if not value_only:
            setattr(widget, var + "_function", 1 if parameter.function else 0)
            setattr(widget, var + "_function_value", parameter.function_value if parameter.function else "")
            setattr(widget, var + "_fixed", 1 if parameter.fixed else 0)

            if parameter.is_variable():
                if not parameter.boundary is None:
                    if parameter.boundary.min_value != PARAM_HWMIN:
                        setattr(widget, var + "_has_min", 1)
                        setattr(widget, var + "_min", round(parameter.boundary.min_value, 6))
                    else:
                        setattr(widget, var + "_has_min", 0)
                        setattr(widget, var + "_min", 0.0)

                    if parameter.boundary.max_value != PARAM_HWMAX:
                        setattr(widget, var + "_has_max", 1)
                        setattr(widget, var + "_max", round(parameter.boundary.max_value, 6))
                    else:
                        setattr(widget, var + "_has_max", 0)
                        setattr(widget, var + "_max", 0.0)

        widget.parameter_functions[var]()

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass

    def show_available_parameters(self):
        ShowTextDialog.show_text("Available Parameters", "" if self.fit_global_parameters is None else self.fit_global_parameters.get_available_parameters(), parent=self)
