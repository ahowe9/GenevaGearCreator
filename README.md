# Geneva Gear Customizer
**Author:** Aaron Howe  
**Date:** 2/23/2026  

## About
This Fusion 360 add-in utilizes the Fusion 360 API to create parameterized Geneva gears.

## Screenshot
![Geneva Gear GUI](/pictures/GenevaGearCreator.png)
## Features
- Creates a pair of Geneva gears based on six parameters:
    - Driven gear radius
    - Slot radius
    - Number of slots
    - Backlash
    - Thickness
    - Edge fillet radius 
- Interactive Geneva gear creation through a GUI
- Saves the most recent parameters

## Installation
1) Download the folder in this repository
2) In Fusion 360, navigate to the Utilities tab and select "Scripts and Add-Ins."
3) Select the + sign on the top and select "script or add-in from device."
4) Select this folder.

## How to use
1) Go to Fusion 360 and create a new design **NOTE: You must be in an assembly or hybrid workspace for the components to be created**
2) Go to utilities, then scripts and add-ins, and select Create_Geneva_Gear
3) Adjust the parameters using the sliders or the text boxes
4) Click "OK" to generate the gears
5) Previous parameters saved for future use in JSON (you can change the minimum and maximum values of the parameters if needed in the JSON file).
1) Download the folder in this repository
2) In Fusion 360, navigate to the Utilities tab and select "Scripts and Add-Ins."
3) Select the + sign on the top and select "script or add-in from device."
4) Select this folder.

## How to use
1) Go to Fusion 360 and create a new design **NOTE: You must be in an assembly or hybrid workspace for the components to be created**
2) Go to utilities, then scripts and add-ins, and select Create_Geneva_Gear
3) Adjust the parameters using the sliders or the text boxes
4) Click "OK" to generate the gears
5) Previous parameters saved for future use in JSON (you can change the minimum and maximum values of the parameters if needed in the JSON file).

## JSON Configuration
Parameters are stored in `geneva_parameters.json`. All values are in millimeters; adjust your parameters accordingly.

## Acknowledgements
I used this page https://www.instructables.com/Make-Geneva-Wheels-of-Any-Size-in-a-Easier-Way/ for steps on constructing a Geneva gear. Professor Jorge Correa Panesso helped with the GUI and JSON ideas. I also used the Fusion 360 API manual and AI tools for debugging.


