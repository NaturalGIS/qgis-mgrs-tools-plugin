# -*- coding: utf-8 -*-

# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.


import os

from PyQt4.QtCore import Qt, QCoreApplication, QUrl
from PyQt4.QtGui import QIcon, QAction, QDesktopServices, QMessageBox

from qgis.core import QgsApplication

from mgrstools.maptool import MGRSMapTool
from mgrstools.gui.mgrsdock import MgrsDockWidget

try:
    from processing.core.Processing import Processing
    from mgrstools.processingprovider.mgrsprovider import MgrsProvider
    processingOk = True
except:
    raise
    processingOk = False

pluginPath = os.path.dirname(__file__)


class MGRSToolsPlugin:

    def __init__(self, iface):
        self.iface = iface
        try:
            from tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, 'MGRS tools')
        except:
            pass

        if processingOk:
            self.provider = MgrsProvider()


    def initGui(self):
        self.mapTool = MGRSMapTool(self.iface.mapCanvas())
        self.iface.mapCanvas().mapToolSet.connect(self.unsetTool)

        self.toolAction = QAction(QIcon(os.path.join(pluginPath, 'icons', 'mgrs.svg')),
                                  self.tr('MGRS map tool'),
                                  self.iface.mainWindow())
        self.toolAction.setCheckable(True)
        self.iface.addToolBarIcon(self.toolAction)
        self.iface.addPluginToMenu(self.tr('MGRS'), self.toolAction)
        self.toolAction.triggered.connect(self.setTool)

        zoomToIcon = QIcon(':/images/themes/default/mActionZoomIn.svg')
        self.zoomToAction = QAction(zoomToIcon,
                                    self.tr('Zoom to MGRS coordinate'),
                                    self.iface.mainWindow())
        self.iface.addPluginToMenu(self.tr('MGRS'), self.zoomToAction)
        self.zoomToAction.triggered.connect(self.zoomTo)

        self.actionHelp = QAction(
            QgsApplication.getThemeIcon('/mActionHelpContents.svg'),
            self.tr('Help'),
            self.iface.mainWindow())
        self.actionHelp.setWhatsThis(
            self.tr('MGRS Tools documentation'))
        self.actionHelp.setObjectName('actionMGRSHelp')
        self.iface.addPluginToMenu(self.tr('MGRS'), self.actionHelp)
        self.actionHelp.triggered.connect(self.showHelp)

        self.mgrsDock = MgrsDockWidget(self.iface.mapCanvas(), self.iface.mainWindow())
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.mgrsDock)
        self.mgrsDock.hide()

        if processingOk:
            Processing.addProvider(self.provider)

    def zoomTo(self):
        self.mgrsDock.show()

    def unsetTool(self, tool):
        try:
            if not isinstance(tool, MGRSMapTool):
                self.toolAction.setChecked(False)
        except:
            # Ignore exceptions thrown when unloading plugin, since map
            # tool class might not exist already
            pass

    def setTool(self):
        self.toolAction.setChecked(True)
        self.iface.mapCanvas().setMapTool(self.mapTool)

    def showHelp(self):
        if not QDesktopServices.openUrl(
                QUrl('file://{}'.format(os.path.join(pluginPath, 'docs', 'html', 'index.html')))):
            QMessageBox.warning(None,
                                self.tr('Error'),
                                self.tr('Can not open help URL in browser'))

    def unload(self):
        self.iface.mapCanvas().unsetMapTool(self.mapTool)
        self.iface.removeDockWidget(self.mgrsDock)
        self.mgrsDock = None
        self.iface.removeToolBarIcon(self.toolAction)
        self.iface.removePluginMenu(self.tr('MGRS'), self.toolAction)
        self.iface.removePluginMenu(self.tr('MGRS'), self.zoomToAction)

        if processingOk:
            Processing.removeProvider(self.provider)

        try:
            from tests import testerplugin
            from qgistester.tests import removeTestModule
            removeTestModule(testerplugin, 'MGRS tools')
        except:
            pass

    def tr(self, text):
        return QCoreApplication.translate('MGRS tools', text)
