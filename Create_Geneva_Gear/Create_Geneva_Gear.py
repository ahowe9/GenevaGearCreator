# Variable Geneva Gear Add On
# Author: Aaron Howe
# Date: x/xx/2026
# Description: This script creates a solid model of a Geneva Gear that can be varried.
# Acknowledgements: I used this page https://www.instructables.com/Make-Geneva-Wheels-of-Any-Size-in-a-Easier-Way/ for steps on constructing a geneva gear as well as the Fusion 360 API manual and AI tools for the debugging process.

import adsk.core, adsk.fusion, traceback
import json
import os

def run(context):
    _handlers = []
    ui = None
    try:
       # Get the  application and user interface objects
       app = adsk.core.Application.get()
       ui = app.userInterface

       # Get the active produce and design
       product = app.activeProduct
       design = adsk.fusion.Design.cast(product)

       # Access the root component of the active design
       rootComp = design.rootComponent

       #Start up the GUI process
       cmdDef = ui.commandDefinitions.itemById('genevaGearCmd')
       if cmdDef:
            cmdDef.deleteMe()
        
       #Fresh cmdDef
       cmdDef = ui.commandDefinitions.addButtonDefinition(
          'genevaGearCmd',
          'Geneva Gear',
          'Create a Geneva Gear'
       )

       #Define function for making the geneva gears
       def GenevaCreator(drivenRadius, slotRadius, toothNumber, backlash, thickness, filletRadius):
         # Initiate timeline group
         timeline = design.timeline
         timelineStart = timeline.count
         
         
         # Math for the gears

         # Compute angle using taylor series
         pi = 3.1415926535897932
         angle = pi/toothNumber
         cos = 1-angle**2/2+angle**4/24-angle**6/720+angle**8/40320-angle**10/3628800
         sin = angle-angle**3/6+angle**5/120-angle**7/5040+angle**9/362880-angle**11/39916800
   
         # Calculation for 3rd point distance
         thirdDist = drivenRadius*cos + drivenRadius*sin**2/cos
   
         # Calculation for drive radius
         driveRadius = drivenRadius*sin/(1-sin**2)**(0.5)
   
         # Calculation for construction radius
         constructionRadius = thirdDist - driveRadius
   
         # Calculation for slot line length
         slotLineLength = drivenRadius - constructionRadius
   
         # Calculation for drive gear profile radius
         driveProfileRadius = thirdDist-drivenRadius*cos+slotRadius
   
         # Calculation for pin base tangent lines
         pinBaseRadius = 2*slotRadius
         const1 = thirdDist - constructionRadius
         const2 = (const1)/(driveRadius/(pinBaseRadius)-1)
   
         # Create the necessary components for the gears
         emptyOccurrence = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
         emptyOccurrence.isGrounded = True
         driveOccurrence = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
         drivenOccurrence = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
         driveComp = driveOccurrence.component
         drivenComp = drivenOccurrence.component
   
         # Create all of the reference points needed for the design
         startPoint = adsk.core.Point3D.create(0, 0, 0)
         diameterPoint = adsk.core.Point3D.create(drivenRadius*cos, drivenRadius*sin, 0)
         drivePoint = adsk.core.Point3D.create(thirdDist, 0, 0)
         constructionPoint = adsk.core.Point3D.create(constructionRadius*cos, constructionRadius*sin, 0)
         lowerSlotLineStart = adsk.core.Point3D.create(constructionRadius*cos + slotRadius*sin, constructionRadius*sin - slotRadius*cos, 0)
         lowerSlotLineEnd = adsk.core.Point3D.create(drivenRadius*cos + slotRadius*sin, drivenRadius*sin - slotRadius*cos, 0)
         upperSlotLineStart = adsk.core.Point3D.create(constructionRadius*cos - slotRadius*sin, constructionRadius*sin + slotRadius*cos, 0)
         upperSlotLineEnd = adsk.core.Point3D.create(drivenRadius*cos - slotRadius*sin, drivenRadius*sin + slotRadius*cos, 0)
         pinPoint = adsk.core.Point3D.create(constructionRadius, 0, 0)
         tangentLine1Start = adsk.core.Point3D.create(constructionRadius-backlash, pinBaseRadius+backlash, 0)
         tangentLine1End = adsk.core.Point3D.create(thirdDist+backlash, driveProfileRadius+backlash, 0)
         tangentLine2Start = adsk.core.Point3D.create(constructionRadius-backlash, -(pinBaseRadius+backlash), 0)
         tangentLine2End = adsk.core.Point3D.create(thirdDist+backlash, -(driveProfileRadius+backlash), 0)
         tangentLineIntersection = adsk.core.Point3D.create(constructionRadius-const2, 0, 0)
   

         # Geometry Creation Section
   
         # Create a sketch on the XY plane for the gears
         sketches = rootComp.sketches
         sketch1 = sketches.add(rootComp.xYConstructionPlane)
   
         # Get sketch lines to draw the sketch
         circles1 = sketch1.sketchCurves.sketchCircles
   
         # Create base circle
         drivenCircle = circles1.addByCenterRadius(startPoint,drivenRadius)
         
         # Extrude the driven circle
         drivenProfile = sketch1.profiles.item(0)
         extrudeDistance = adsk.core.ValueInput.createByReal(thickness)
         extrudes = rootComp.features.extrudeFeatures
         extrude = extrudes.addSimple(drivenProfile, extrudeDistance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
   
         # Create a sketch on the XY plane to cut the driven gears features
         sketch2 = sketches.add(rootComp.xYConstructionPlane)
   
         # New sketch elements
         lines = sketch2.sketchCurves.sketchLines
         circles = sketch2.sketchCurves.sketchCircles
   
         # Create First Slot
         slotCircle1 = circles.addByCenterRadius(constructionPoint, slotRadius)
         slotCircle2 = circles.addByCenterRadius(diameterPoint, slotRadius)
         slotLine1 = lines.addByTwoPoints(lowerSlotLineStart, lowerSlotLineEnd)
         slotLine2 = lines.addByTwoPoints(upperSlotLineStart, upperSlotLineEnd)
         
         # Create profile of the drive gear
         driveProfileCircle = circles.addByCenterRadius(drivePoint,driveProfileRadius) #circle without backlash
   
         # Create a cut to form the geneva gear
         allGenevaProfiles = adsk.core.ObjectCollection.create() #create a collection for the profile
         for profile in sketch2.profiles: #loop over the profiles
             allGenevaProfiles.add(profile)
         genevaExtrude = extrudes.addSimple(allGenevaProfiles, extrudeDistance, adsk.fusion.FeatureOperations.CutFeatureOperation)
         
         # Create circular pattern
         zAxis = rootComp.zConstructionAxis
         circularFeats = rootComp.features.circularPatternFeatures
         patternObjects = adsk.core.ObjectCollection.create()
         patternObjects.add(genevaExtrude)
         circularFeatInput = circularFeats.createInput(patternObjects, zAxis)
         circularFeatInput.quantity = adsk.core.ValueInput.createByReal(toothNumber)
         circularFeatInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')
         circularFeat = circularFeats.add(circularFeatInput)

         # Create fillets
         # Create a collection for the edges
         body0 = rootComp.bRepBodies.item(0)
         edges = body0.edges
         filletEdges = adsk.core.ObjectCollection.create()

         # Find the correct edges by sording by the eges alligned with the z axis
         for edge in edges:
            tolerance = 0.1
            edgeStartPoint = edge.startVertex.geometry
            edgeEndPoint = edge.endVertex.geometry
            if (abs(edgeStartPoint.x - edgeEndPoint.x) <=tolerance and abs(edgeStartPoint.y - edgeEndPoint.y) <= tolerance and (thickness-tolerance <= edgeEndPoint.z <= thickness+tolerance or thickness- tolerance <= edgeStartPoint.z <= thickness+tolerance)):
               filletEdges.add(edge)
         
         # Add the fillets
         fillet = rootComp.features.filletFeatures
         filletInput = fillet.createInput()
         filletInput.addConstantRadiusEdgeSet(filletEdges,adsk.core.ValueInput.createByReal(filletRadius), True)
         fillet.add(filletInput)

   
         # Create the base of the drive gear
         sketches = rootComp.sketches
         sketch3 = sketches.add(rootComp.xYConstructionPlane)
         constraints = sketch3.geometricConstraints
         circles3 = sketch3.sketchCurves.sketchCircles
         lines3 = sketch3.sketchCurves.sketchLines       
   
         #Add sketch geometry
         driveCircle = circles3.addByCenterRadius(drivePoint, driveProfileRadius)
         pinBaseCircle = circles3.addByCenterRadius(pinPoint, pinBaseRadius)
         tangentLine1 = lines3.addByTwoPoints(tangentLine1Start, tangentLine1End)
         tangentLine2 = lines3.addByTwoPoints(tangentLine2Start, tangentLine2End)
   
         # Add constraints to close profile
         driveCircle.isFixed = True
         pinBaseCircle.isFixed = True
         constraints.addTangent(pinBaseCircle,tangentLine1) 
         constraints.addTangent(driveCircle,tangentLine1)
         constraints.addTangent(pinBaseCircle,tangentLine2) 
         constraints.addTangent(driveCircle,tangentLine2)
         tangentLine1.extend(tangentLineIntersection)
         tangentLine2.extend(tangentLineIntersection)
   
         # Extrude the profiles
         negativeExtrudeDistance = adsk.core.ValueInput.createByReal(-thickness)
         driveBottomProfile = adsk.core.ObjectCollection.create() #create a collection for the profile
         for profile in sketch3.profiles: #loop over the profiles
             driveBottomProfile.add(profile)
         driveBaseExtrude = extrudes.addSimple(driveBottomProfile, negativeExtrudeDistance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
   
         # Create the top of the drive gear sketch
         sketch4 = sketches.add(rootComp.xYConstructionPlane)
         circles4 = sketch4.sketchCurves.sketchCircles
         driveBacklash = circles4.addByCenterRadius(drivePoint,driveProfileRadius-backlash)
         drivenBacklash = circles4.addByCenterRadius(startPoint,drivenRadius+backlash)
   
         # Extrude the desired profile
         driveTopProfile = sketch4.profiles.item(0)
         driveTopExtrude = extrudes.addSimple(driveTopProfile, extrudeDistance, adsk.fusion.FeatureOperations.JoinFeatureOperation)
   
         # Rotate the driven gear so the pin is alligned with the slot
         drivenGear = adsk.core.ObjectCollection.create()
         drivenGear.add(rootComp.bRepBodies.item(0))
         zAxis = adsk.core.Vector3D.create(0, 0, 1)
         transform = adsk.core.Matrix3D.create()
         transform.setToRotation(angle, zAxis, startPoint)
         moveFeats = rootComp.features.moveFeatures
         moveInput = moveFeats.createInput(drivenGear, transform)
         moveFeats.add(moveInput)    
   
         # Create pin sketch
         sketch5 = sketches.add(rootComp.xYConstructionPlane)
         circles5 = sketch5.sketchCurves.sketchCircles
         pinCircle = circles5.addByCenterRadius(pinPoint, slotRadius-backlash/2)
   
         # Extrude pin
         pinProfile = sketch5.profiles.item(0)
         pinExtrude = extrudes.addSimple(pinProfile, extrudeDistance, adsk.fusion.FeatureOperations.JoinFeatureOperation)
   
   
         # Motion Section
   
         # Add the bodies to components
         body1 = rootComp.bRepBodies.item(0)
         body2 = rootComp.bRepBodies.item(1)
         body1.moveToComponent(drivenOccurrence)
         body2.moveToComponent(driveOccurrence)
   
         # Create the points to define the joints, note they have to be contruction points, not Point3D
         constructionPoints = driveComp.constructionPoints
         pointInput = constructionPoints.createInput()
         pointInput.setByCenter(driveCircle)
         driveConstructionPoint = constructionPoints.add(pointInput)
         drivenConstructionPoint = drivenComp.originConstructionPoint
   
         # Define the geometry to describe the joints
         driveGeometry = adsk.fusion.JointGeometry.createByPoint(driveConstructionPoint)
         drivenGeometry = adsk.fusion.JointGeometry.createByPoint(drivenConstructionPoint)
   
         # Create the joints
         asBuiltJoints = rootComp.asBuiltJoints
         driveJointInput = asBuiltJoints.createInput(driveOccurrence, emptyOccurrence, driveGeometry)
         driveJointInput.setAsRevoluteJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
         driveJoint = asBuiltJoints.add(driveJointInput)
         drivenJointInput = asBuiltJoints.createInput(drivenOccurrence, emptyOccurrence, drivenGeometry)
         drivenJointInput.setAsRevoluteJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
         drivenJoint = asBuiltJoints.add(drivenJointInput)
   
         # Create contact set
         design.isContactAnalysisEnabled = True
         design.isContactSetAnalysis = True
         contacts = design.contactSets
         occurrencesAndBodies = []
         occurrencesAndBodies.append(rootComp.occurrences[0])
         occurrencesAndBodies.append(rootComp.occurrences[1])
         occurrencesAndBodies.append(rootComp.occurrences[2])
         contacts.add(occurrencesAndBodies)

         # Group elements
         timelineEnd = timeline.count - 1
         timelineGroup = timeline.timelineGroups.add(timelineStart,timelineEnd)
       

       #Start of code for GUI and JSON

       # Find where the JSON script is located
       script_dir = os.path.dirname(os.path.realpath(__file__))

       # Find the path to the JSON file
       jsonPath = os.path.join(script_dir, 'geneva_parameters.json')

       if os.path.exists(jsonPath) == False:
          ui.messageBox(f'JSON file not found!\n\nExpected location:\n{jsonPath}')
          return

       #open the JSON file
       try:
        with open(jsonPath,'r') as f:
           parameters = json.load(f)
        genevaParameters = parameters['geneva_mechanism']

       except (json.JSONDecodeError, KeyError):
          #Display error message if there is an issue
          ui.messageBox('Bad formatting, check the JSON guide format.')
          return

       # Get the values stored in the json file
       try:
        drivenRadius = genevaParameters['driven_radius']/10.0
        toothNumber = genevaParameters['number_of_slots']
        slotRadius = genevaParameters['slot_radius']/10.0
        backlash = genevaParameters['backlash']/10.0
        thickness = genevaParameters['thickness']/10.0
        filletRadius = genevaParameters['filletRadius']/10.0
        maxDivenRadius = genevaParameters['maxDivenRadius']/10.0
        minDrivenRadius = genevaParameters['minDrivenRadius']/10.0
        maxToothNumber = genevaParameters['maxToothNumber']
        minToothNumber = genevaParameters['minToothNumber']
        maxSlotRadius = genevaParameters['maxSlotRadius']/10.0
        minSlotRadius = genevaParameters['minSlotRadius']/10.0
        maxBacklash = genevaParameters['maxBacklash']/10.0
        minBacklash = genevaParameters['minBacklash']/10.0
        maxThickness = genevaParameters['maxThickness']/10.0
        minThickness = genevaParameters['minThickness']/10.0
        maxFilletRadius = genevaParameters['maxFilletRadius']/10.0
        minFilletRadius = genevaParameters['minFilletRadius']/10.0

        # Logic to determine if the values are outside of the prescribed range
        if drivenRadius > maxDivenRadius:
           ui.messageBox(f'Driven radius too large, must be under {maxFilletRadius} mm')
           return

        if toothNumber > maxToothNumber:
           ui.messageBox(f'Number of slots too large, must be under {maxToothNumber}')
           return      
          
        if slotRadius > maxSlotRadius:
           ui.messageBox(f'Slot radius too large, must be under {maxSlotRadius} mm')
           return
        
        if backlash > maxBacklash:
           ui.messageBox(f'Backlash too large, must be under {maxBacklash} mm')
           return

        if thickness > maxThickness:
           ui.messageBox(f'Thickness too large, must be under {maxThickness} mm')
           return
        
        if filletRadius > maxFilletRadius:
           ui.messageBox(f'Fillet radius too large, must be under {maxFilletRadius} mm')
           return
           

        if drivenRadius < minDrivenRadius:
           ui.messageBox(f'Driven radius too small, must be above {minDrivenRadius} mm')
           return

        if toothNumber < minToothNumber:
           ui.messageBox(f'Number of slots too small, must be above {minToothNumber}')
           return      
          
        if slotRadius < minSlotRadius:
           ui.messageBox(f'Slot radius too small, must be above {minSlotRadius} mm')
           return
        
        if backlash < minBacklash:
           ui.messageBox(f'Backlash too small, must be above 0.{minBacklash} mm')
           return

        if thickness < minThickness:
           ui.messageBox(f'Thickness too small, must be above {minThickness} mm')
           return
        
        if filletRadius < minFilletRadius:
           ui.messageBox(f'Fillet radius too small, must be above {minFilletRadius} mm')
           return


       except KeyError as e:
          #Display error message if there is an issue
          ui.messageBox(f'JSON Key deleted, check formatting for JSON file.\nMissing parameter:{e}')
          return
       
       # Code for the GUI

       # Shows a preview of what the gears will look like before hitting "OK"
       class MyPreviewHandler(adsk.core.CommandEventHandler):
          def __init__(self):
             super().__init__()

          def notify(self,args):
             try:
                # Get the values
                inputs = args.command.commandInputs
                drivenRadius = inputs.itemById('drivenRadius').valueOne
                toothNumber = inputs.itemById('toothNumber').value
                slotRadius = inputs.itemById('slotRadius').valueOne  
                backlash = inputs.itemById('backlash').valueOne  
                thickness = inputs.itemById('thickness').valueOne
                filletRadius = inputs.itemById('filletRadius').valueOne

                # Create the gear on change
                GenevaCreator(drivenRadius,slotRadius,toothNumber,backlash,thickness,filletRadius)

                # Make it so its not perminant
                args.isValudResult = True

             except:
                #Display error message if there is an issue
                args.isValidResult = False   

       # Creates the gears after hitting ok and stores the values in JSON file
       class MyExecuteHandler(adsk.core.CommandEventHandler):
          def __init__(self,jsonPath,parameters):
             super().__init__()

             self.jsonPath = jsonPath
             self.parameters = parameters
          
          def notify(self,args):
             try:
                cmd = args.command
                inputs = cmd.commandInputs

                #Get the values from the GUI
                drivenRadius = inputs.itemById('drivenRadius').valueOne
                toothNumber = inputs.itemById('toothNumber').value
                slotRadius = inputs.itemById('slotRadius').valueOne
                backlash = inputs.itemById('backlash').valueOne
                thickness = inputs.itemById('thickness').valueOne
                filletRadius = inputs.itemById('filletRadius').valueOne

                # Create the gears
                GenevaCreator(drivenRadius, slotRadius, toothNumber, backlash, thickness, filletRadius)

                # Write these values to the JSON file
                genevaParameters = self.parameters['geneva_mechanism']

                with open(jsonPath, 'w') as f:
                   genevaParameters['driven_radius'] = drivenRadius*10
                   genevaParameters['number_of_slots'] = toothNumber
                   genevaParameters['slot_radius'] = slotRadius*10
                   genevaParameters['backlash'] = backlash*10
                   genevaParameters['thickness'] = thickness*10
                   genevaParameters['filletRadius'] = filletRadius*10
                   json.dump(parameters, f)

             except:
                #Display error message if there is an issue
                ui.messageBox(traceback.format_exc())
                return
       
       # Creates the GUI, showing the different parameters and allowing the user to change them
       class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
          def __init__(self):
             super().__init__()
          def notify(self,args):
             try:
                cmd = args.command
                inputs = cmd.commandInputs

                # Add all of the input parameters
                inputs.addIntegerSpinnerCommandInput(
                   'toothNumber',
                   'Number of slots',
                   minToothNumber,
                   maxToothNumber,
                   1,
                   toothNumber
                )
                
                drivenRadiusSlider = inputs.addFloatSliderCommandInput(
                   'drivenRadius',
                   'Radius of the driven gear (mm)',
                   'mm',
                   minDrivenRadius,
                   maxDivenRadius,
                   False
                )
                
                slotRadiusSlider = inputs.addFloatSliderCommandInput(
                   'slotRadius',
                   'Radius of the slots (mm)',
                   'mm',
                   minSlotRadius,
                   maxSlotRadius,
                   False
                )
                
                backlashSlider = inputs.addFloatSliderCommandInput(
                   'backlash',
                   'Backlash (tolerance) of the gears (mm)',
                   'mm',
                   minBacklash,
                   maxBacklash,
                   False
                )
                
                thicknessSlider = inputs.addFloatSliderCommandInput(
                   'thickness',
                   'Thickness of the gears (mm)',
                   'mm',
                   minThickness,
                   maxThickness,
                   False
                )

                filletRadiusSlider = inputs.addFloatSliderCommandInput(
                   'filletRadius',
                   'Fillet radius of the edges (mm)',
                   'mm',
                   minFilletRadius,
                   maxFilletRadius,
                   False
                )
                
                # Read the values
                slotRadiusSlider.valueOne = slotRadius
                backlashSlider.valueOne = backlash
                thicknessSlider.valueOne = thickness
                drivenRadiusSlider.valueOne = drivenRadius
                filletRadiusSlider.valueOne = filletRadius

               # Add event detection
                onExecute = MyExecuteHandler(jsonPath, parameters)
                cmd.execute.add(onExecute)
                _handlers.append(onExecute)

               # Add change detection
                onPreview = MyPreviewHandler()
                cmd.executePreview.add(onPreview)
                _handlers.append(onPreview)


             except:
                #Display error message if there is an issue
                ui.messageBox(f'GUI Failed:\n{traceback.format_exc()}')
                return

       # Create the GUI
       onCreated = MyCommandCreatedHandler()
       cmdDef.commandCreated.add(onCreated)
       _handlers.append(onCreated)
       cmdDef.execute()
       adsk.autoTerminate(False)

    except Exception as e:
    #Display error message if there is an issue
       if ui:
        error_msg = 'Failed:\n{}\n\nType: {}'.format(traceback.format_exc(), type(e).__name__)
        ui.messageBox(error_msg, 'Error Details')