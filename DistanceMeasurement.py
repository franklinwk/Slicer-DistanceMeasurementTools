# -*- coding: utf-8 -*-
from __main__ import vtk, qt, ctk, slicer
import math

class DistanceMeasurement:
  def __init__(self, parent):
    parent.title = "Measurements"
    parent.categories = ["Utilities"]
    parent.contributors = ["Franklin King"]
    
    parent.helpText = """
    Add help text
    """
    parent.acknowledgementText = """
""" 
    # module build directory is not the current directory when running the python script, hence why the usual method of finding resources didn't work ASAP
    self.parent = parent

#
# qLeapMotionIntegratorWidget
#
class DistanceMeasurementWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    self.lastCommandId = 0
    self.timeoutCounter = 0
    if not parent:
      self.setup()
      self.parent.show()
  
  def setup(self):
    # Point Distance
    pointDistanceButton = ctk.ctkCollapsibleButton()
    pointDistanceButton.text = "Distance Between Two Points"
    self.layout.addWidget(pointDistanceButton)

    pointDistanceLayout = qt.QFormLayout(pointDistanceButton)  
  
    self.transformSelector1 = slicer.qMRMLNodeComboBox()
    self.transformSelector1.nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.transformSelector1.selectNodeUponCreation = False
    self.transformSelector1.noneEnabled = False
    self.transformSelector1.addEnabled = True
    self.transformSelector1.showHidden = False
    self.transformSelector1.setMRMLScene( slicer.mrmlScene )
    self.transformSelector1.setToolTip( "Pick Transform 1" )
    pointDistanceLayout.addRow("Point 1:", self.transformSelector1)
    
    self.transformSelector2 = slicer.qMRMLNodeComboBox()
    self.transformSelector2.nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.transformSelector2.selectNodeUponCreation = False
    self.transformSelector2.noneEnabled = False
    self.transformSelector2.addEnabled = True
    self.transformSelector2.showHidden = False
    self.transformSelector2.setMRMLScene( slicer.mrmlScene )
    self.transformSelector2.setToolTip( "Pick Transform 1" )
    pointDistanceLayout.addRow("Point 2:", self.transformSelector2)    

    self.distanceLabel = qt.QLabel("N/A")
    pointDistanceLayout.addRow("Distance: ", self.distanceLabel)    

    self.startButton = qt.QPushButton("Start")
    pointDistanceLayout.addRow(self.startButton)
    self.stopButton = qt.QPushButton("Stop")
    pointDistanceLayout.addRow(self.stopButton)
    self.startButton.connect('clicked(bool)', self.start)
    self.stopButton.connect('clicked(bool)', self.stop)
    
    self.timer = qt.QTimer()
    self.timer.timeout.connect(self.updateMeasurement)    
    
    # Angle Measurement
    
    angleButton = ctk.ctkCollapsibleButton()
    angleButton.text = "Angle Between Vector and Plane"
    self.layout.addWidget(angleButton)

    angleLayout = qt.QFormLayout(angleButton)         
    
    self.referenceVector = ctk.ctkCoordinatesWidget()
    self.referenceVector.coordinates = "0.0, 0.0, 1.0"
    angleLayout.addRow("Reference Vector: ", self.referenceVector)
    
    self.trackerSelector = slicer.qMRMLNodeComboBox()
    self.trackerSelector.nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.trackerSelector.addEnabled = True
    self.trackerSelector.noneEnabled = False
    self.trackerSelector.setMRMLScene( slicer.mrmlScene )
    angleLayout.addRow("Tracker Transform: ", self.trackerSelector)    
    
    self.planeNormal = ctk.ctkCoordinatesWidget()
    self.planeNormal.coordinates = "0.0, 0.0, -1.0"
    angleLayout.addRow("Plane Normal: ", self.planeNormal)

    self.angleLabel = qt.QLabel("N/A")
    angleLayout.addRow("Angle: ", self.angleLabel)
    
    self.startButtonAngle = qt.QPushButton("Start")
    angleLayout.addRow(self.startButtonAngle)
    self.stopButtonAngle = qt.QPushButton("Stop")
    angleLayout.addRow(self.stopButtonAngle)
    self.startButtonAngle.connect('clicked(bool)', self.startAngle)
    self.stopButtonAngle.connect('clicked(bool)', self.stopAngle)
    
    self.layout.addStretch(1)
    
    self.angleTimer = qt.QTimer()
    self.angleTimer.timeout.connect(self.updateAngleMeasurement)        
    
  def start(self):
    self.timer.start(100)
    
  def stop(self):
    self.timer.stop()
    
  def updateMeasurement(self):
    transform1 = self.transformSelector1.currentNode()
    transform2 = self.transformSelector2.currentNode()
    
    if transform1 and transform2:
      matrix1 = vtk.vtkMatrix4x4()
      matrix2 = vtk.vtkMatrix4x4()
      transform1.GetMatrixTransformToWorld(matrix1)
      transform2.GetMatrixTransformToWorld(matrix2)
      p1 = [matrix1.GetElement(0,3), matrix1.GetElement(1,3), matrix1.GetElement(2,3)]
      p2 = [matrix2.GetElement(0,3), matrix2.GetElement(1,3), matrix2.GetElement(2,3)]
      d = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(p1,p2))
      
      self.distanceLabel.setText(str(d) + "mm")

      
  def startAngle(self):
    self.angleTimer.start(100)
    
  def stopAngle(self):
    self.angleTimer.stop()
    
  def updateAngleMeasurement(self):
    reference = map(float, self.referenceVector.coordinates.split(","))
    normal = map(float, self.planeNormal.coordinates.split(","))
    normNormal = vtk.vtkMath.Norm(normal)
    normalizedNormal = [normal[0] / normNormal, normal[1] / normNormal, normal[2] / normNormal]
    tracker = self.trackerSelector.currentNode()
    
    if tracker:
      vector = (tracker.GetMatrixTransformToParent().MultiplyFloatPoint(reference + [0]))[:-1]
      vectorNormal = vtk.vtkMath.Norm(vector)
      normalizedVector = [vector[0] / vectorNormal, vector[1] / vectorNormal, vector[2] / vectorNormal]
    
      angle = abs(normalizedNormal[0]*normalizedVector[0] + normalizedNormal[1]*normalizedVector[1] + normalizedNormal[2]*normalizedVector[2]) /\
      (math.sqrt(normalizedNormal[0]**2 + normalizedNormal[1]**2 + normalizedNormal[2]**2) * math.sqrt(normalizedVector[0]**2 + normalizedVector[1]**2 + normalizedVector[2]**2))
      
      angle = math.degrees(math.asin(angle))
      
      self.angleLabel.setText(str(angle) + " degrees")

  
class DistanceMeasurementLogic:
  def __init__(self):
    pass
 
  


