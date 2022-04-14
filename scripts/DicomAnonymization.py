# Copyright 2022
# All rights reserved
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import logging

scriptDirectory = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(scriptDirectory)
sys.path.append(parentDirectory)

from Common.Anonymizer import Anonymizer
from Common.Dcmtk import Dcmtk
from Common.AddDcmExt import addDCMextension

# Output files
logFileName = 'anonymizer.log'

# Boolean defines whether input dicom images will be uploaded
# DEMO ONLY
uploadInputFiles = False

# Boolean defines whether anonymized dicom images will be uploaded
uploadAnonymizedFiles = True

if __name__ == "__main__":

    ### Set directory paths for input, anonymization and downloaded DICOM files ###

    inputDicomFileDirectory = os.path.abspath(os.path.join(scriptDirectory, '..', 'ImageHeaders\InputFiles'))
    outputDicomFileDirectory = os.path.abspath(os.path.join(scriptDirectory, '..', 'ImageHeaders\AnonymizedFiles'))
    downloadedDicomFileDirectory = os.path.abspath(os.path.join(scriptDirectory, '..', 'ImageHeaders\DownloadedFiles'))
        
    ### Set directory path for dcmtk library ###
    dcmtkDirectory = os.path.abspath(os.path.join(scriptDirectory, '..', r'dcmtk-3.6.6-win64-dynamic\bin'))

    ### Anonymization of input files ###
    logging.basicConfig(filename=logFileName, level=logging.DEBUG)

    ### Upload files to Orthanc server ###
    connection = Dcmtk(scriptDirectory, dcmtkDirectory, "localhost", "4242")

    # Check connection with Orthanc Server is secure
    runStatus = connection.cEcho()
    logging.debug('cEcho run status ' + str(runStatus))
    if runStatus == 0:
        print('FATAL ERROR: Could not connect to Orthanc server')
    else:
        print("Orthanc Connection is successful")
        # Upload input DICOM files to Orthanc
        runStatus = connection.cStore(inputDicomFileDirectory, individualFile=False)
        if runStatus == 0:
            print('FATAL ERROR: Could not store input images in Orthanc server')
        else:
            print("Input images pushed to Orthanc server")

    ### DICOM Query/Retrieve ###
    patientID = 626457
    runStatus = connection.cGet(patientID, downloadedDicomFileDirectory)
    if runStatus == 0:
        print('FATAL ERROR: Could not download images from the Orthanc server')
    else:
        print("Input images downloaded from Orthanc server and saved in "+ downloadedDicomFileDirectory)
    
    # add dcm extension to all downloaded files
    addDCMextension(downloadedDicomFileDirectory)
    
    # change inputDicomFileDirectory to just downloaded files' directory 
    inputDicomFileDirectory = downloadedDicomFileDirectory
    
    anonymizer = Anonymizer()

    # iterate over files in inputDicomFileDirectory, anonymize those files, and save them in outputDicomFileDirectory
    for filename in os.listdir(inputDicomFileDirectory):

        # Get file paths to input and output locations
        inputDicomFilePath = os.path.join(inputDicomFileDirectory, filename)
        outputDicomFilePath = os.path.join(outputDicomFileDirectory, filename)

        # Read DICOM File (stored in anonymizer class as self.dataset)
        anonymizer.readDicomFile(inputDicomFilePath)

        # Remove private tags from DICOM file
        anonymizer.removePrivateTags()

        # Remove/modify tags based on DicomTags class
        anonymizer.anonymizeTags()

        # Save anonymized files to output location
        anonymizer.saveAnonymizedFile(outputDicomFilePath)

    print("All files in Input DICOM Directory have been anonymized")

    ### Push output files to Orthanc Server ###
    connection = Dcmtk(scriptDirectory, dcmtkDirectory, "localhost", "4242")

    # Check connection with Orthanc Server is secure
    runStatus = connection.cEcho()
    logging.debug('cEcho run status ' + str(runStatus))
    if runStatus == 0:
        print('FATAL ERROR: Could not connect to Orthanc server')
    else:
        print("Orthanc Connection is successful")
        # Upload input DICOM files to Orthanc as point of comparison if user desires it
        if uploadInputFiles:
            runStatus = connection.cStore(inputDicomFileDirectory, individualFile=False)
            if runStatus == 0:
                print('FATAL ERROR: Could not store input images in Orthanc server')
            else:
                print("Input images pushed to Orthanc server")

        if uploadAnonymizedFiles:
            # Upload output anonymized DICOM files to Orthanc
            runStatus = connection.cStore(outputDicomFileDirectory, individualFile=False)
            if runStatus == 0:
                print('FATAL ERROR: Could not store anonymized images in Orthanc server')
            else:
                print("Anonymized images pushed to Orthanc server")
