#burned areas index values identification on MODIS imagery
#Description: applies 625 combintations of index value tresholds on MODIS imagery; confusion matrix produced after that with another script to get the best combination
#Works on Python 3 with numpy and osgeo libraries; images must be stored in separated subfolders per protected area, in one common folder
#Author: Martin Rapilly
#warning:PIL (pillow library) reads NaN as -32768

#imports libraries
import os, sys, math, time, datetime
    #limits multiprocessing to one core
os.environ['OPENBLAS_MAIN_FREE'] = '1'
from numpy import *
import numpy as np
from osgeo import gdal
from osgeo import gdal_array
from osgeo import osr
from itertools import islice
from multiprocessing import Pool, Process
import multiprocessing

#allows to see full array in print and log
np.set_printoptions(threshold=sys.maxsize)

#defines log path
log = open("F:/.../myprog.log", "a")
sys.stdout = log

#defines 5 tresholds for all four index used: dNBR, NBR and NDVI difference (ratio NDVIafter/NDVIbefore); for NBR and RdNBR, SWIR3 is used
listdNBRthreshold=[0.3105,0.388,0.2328,0.4657,0.1552]
listRdNBRthreshold=[0.2215,0.2768,0.166,0.3321,0.1107]
listNDVIdiffThreshold=[0.062725,0.0940875,0.1255,0.1558125, 0.188175]
listratioB5Threshold=[1.1754,1.4691,0.8815,1.763,0.5876]

#loops to iterate with each threshold (625 iterations in total)
for dNBRthreshold in listdNBRthreshold:
    for RdNBRthreshold in listRdNBRthreshold:
        for NDVIdiffThreshold in listNDVIdiffThreshold:
            for ratioB5Threshold in listratioB5Threshold:
   
                #keeps time variable for processing time measurement
                time1 = time.clock()

                #function that will be processed parallely by folder with multiprocessing
                def proc (path):
                    
                    #gets full name and creates a list of all files in the directory 
                    ListImages=[]
                    for file in os.listdir(path):
                        if file.endswith(".tif"):
                                ListImages.append(os.path.join(path, file))
                    #sort the list aphabetically (important step!) 
                    ListImages.sort()
                    
                    #creates empty numpy array the same size as the first image and with number of bands defined by user
                    firstImage=gdal.Open(ListImages[0])
                    band0 = firstImage.GetRasterBand(1)
                    arrayOfFirstImage = band0.ReadAsArray()
                    listEmpty=[]

                    #define number of bands here (range...) for storing results 
                    for x in range(120):
                        name="emptyArray_" + str(x)
                        #creates raster with same size as First image
                        name=np.full_like(arrayOfFirstImage, np.nan, dtype=np.double)
                        listEmpty.append(name)
                    #creates stack of all bands  
                    arrayStack=np.stack(listEmpty)
                    num_dim, num_rows,num_cols = arrayStack.shape
                    
                    #makes a list from the number of rows
                    listRows = list(range(num_rows))    

                    #makes a loop to get access to each pixel
                    for row in range(num_rows):
                        print("row number: ", row)
                        for col in range(num_cols):
                            #reset counter for band as script is working with a new pixel; cntrForBand is used to change arrayStack bands that will be written on (0,1,2 then 3,4,5 if first three have been used)
                            cntrForBand=0
                            print("col number: ", col)


                            #loops through all images in list ListImages to get image x
                            #uses ITER function to be able to jump 7 o 22 loops if a burned area has been detected
                            iterListImages = iter(ListImages)
                            for image in iterListImages:
                                indexImage1 = ListImages.index(image)
                                
                                #gets image full path
                                img1Path=os.path.abspath(image)
                 
                                #opens geotiff with gdal
                                img = gdal.Open(image)
                                
                                #gets bands 1 and 6 values for this date
                                band1Image1=img.GetRasterBand(1)
                                band6Image1=img.GetRasterBand(6)
                       
                                #converts gdal array (raster or band) into a numpy array:
                                band1Image1asArray = band1Image1.ReadAsArray()
                                band6Image1asArray = band6Image1.ReadAsArray()
                                
                                #if pixel has no value, doesn´t do anything and skips
                                #warning: -28772 can appear in band 6 sometimes instead of No Value
                                if math.isnan(band1Image1asArray[row][col])or band1Image1asArray[row][col]==-32768 or band1Image1asArray[row][col]==0.0 or band6Image1asArray[row][col]==-28672:
                                    print("row number: ", row)
                                    print("col number: ", col)
                                    print("img:",image )
                                    print("image 1 pixel with no data value; initiating with another image")

                                #if pixel has a value, proceeds
                                else:
                                    #Calculates NDVI value of pixel of interest
                                    band2Image1=img.GetRasterBand(2)
                                    band2Image1asArray = band2Image1.ReadAsArray()
                                    print ("band2Image1asArray[row][col],band1Image1asArray[row][col]: ", band2Image1asArray[row][col],band1Image1asArray[row][col])
                                    itemNDVIimage1=float((band2Image1asArray[row][col]-band1Image1asArray[row][col])/(band2Image1asArray[row][col]+band1Image1asArray[row][col]))
                                    print ("itemNDVIimage1: ",itemNDVIimage1)

                                    #Gets NBR value of pixel of interest
                                        #gets SWIR3 value from band 7
                                    band7Image1=img.GetRasterBand(7)
                                    band7Image1asArray = band7Image1.ReadAsArray()
                                    print ("band7Image1asArray[row][col],band2Image1asArray[row][col]: ", band7Image1asArray[row][col],band2Image1asArray[row][col])
                                        #calculates NBR
                                    itemImage1=float((band2Image1asArray[row][col]-band7Image1asArray[row][col])/(band2Image1asArray[row][col]+band7Image1asArray[row][col]))
                                    print ("itemNBRimage1: ",itemImage1)
                                        #cleans memory
                                    band1Image1=None
                                    band2Image1=None
                                    band6Image1=None
                                    band7Image1=None
                                    band1Image1asArray=None
                                    band2Image1asArray=None
                                    band6Image1asArray=None
                                    band7Image1asArray=None
                                    del band1Image1
                                    del band2Image1
                                    del band6Image1
                                    del band7Image1
                                    del band1Image1asArray
                                    del band2Image1asArray
                                    del band6Image1asArray
                                    del band7Image1asArray
                                    
                                    #resets switch to False ; switch is used to skip dates for imagery processing if a burned area has been identified
                                    switch1=False
                                   
                                    #list of numbers for image 2: from index of image x + 1 to index of image x + 8
                                    listImg2=[indexImage1+1,indexImage1+2,indexImage1+3,indexImage1+4,indexImage1+5,indexImage1+6,indexImage1+7,indexImage1+8]
                                    for indexImg2 in listImg2:
                        
                                        #if number of image 2 is above number of images in list, stops (all images have been processed)
                                        if indexImg2>=len(ListImages):
                                            print ("break")
                                            break
                                        
                                        #if not, proceeds
                                        else:
                                            
                                            #open next image in the list (next date)
                                            image2=gdal.Open(ListImages[indexImg2])
                                            print("image2 opened with GDAL")
                                            img2Path=os.path.abspath(ListImages[indexImg2])
                                            print ("path image 2: " + img2Path)
                                            
                                            #gets image 2 NDVI value for this pixel
                                            band1Image2 = image2.GetRasterBand(1)
                                            band6Image2 = image2.GetRasterBand(6)
                                            print("all bands saved to variable")
                                            band1Image2asArray = band1Image2.ReadAsArray()
                                            print ("b1 to numpy array: ok")
                                            band6Image2asArray = band6Image2.ReadAsArray()
                                            print ("b6 to numpy array: ok")
                                            
                                            #if image 2 has no value for NBR band, stop and continue with next image 2
                                            if math.isnan(band1Image2asArray[row][col])or band1Image2asArray[row][col]==-32768 or band1Image2asArray[row][col]==0.0 or band6Image2asArray[row][col]==-28672 or itemImage1==0:
                                                print ("image 2 pixel with no data value; initiating with another image")
                                            #else, proceeds
                                            else:
                                                #calculates NDVI for image second date
                                                band2Image2 = image2.GetRasterBand(2)
                                                band2Image2asArray = band2Image2.ReadAsArray()
                                                print ("band2Image2asArray[row][col],band2Image2asArray[row][col]: ", band2Image2asArray[row][col],band2Image2asArray[row][col])
                                                itemNDVIimage2=float((band2Image2asArray[row][col]-band1Image2asArray[row][col])/(band2Image2asArray[row][col]+band1Image2asArray[row][col]))
                                                print ("itemNDVIimage2: ",itemNDVIimage2)
                                                #calculates NBR for image second date
                                                band7Image2 = image2.GetRasterBand(7)
                                                band7Image2asArray = band7Image2.ReadAsArray() 
                                                itemImage2=float((band2Image2asArray[row][col]-band7Image2asArray[row][col])/(band2Image2asArray[row][col]+band7Image2asArray[row][col]))
                                                print ("itemNBRimage2: ",itemImage2)
                                                #cleans memory
                                                band1Image2=None
                                                band2Image2=None
                                                band6Image2=None
                                                band7Image2= None
                                                band1Image2asArray=None
                                                band2Image2asArray=None
                                                band6Image2asArray=None
                                                band7Image2asArray=None
                                                del band1Image2
                                                del band2Image2
                                                del band6Image2
                                                del band7Image2  
                                                del band1Image2asArray
                                                del band2Image2asArray
                                                del band6Image2asArray
                                                del band7Image2asArray
                                                
                                                #calculate dNBR, NBR, NDVI and Band 5 ratio difference between the two images
                                                print ("calcutating dNBR, RdNBR, NDVIdiff and ratioB5")
                                                dNBR=itemImage1-itemImage2
                                                RdNBR=dNBR/(math.sqrt(abs(itemImage1)))
                                                NDVIdiff=itemNDVIimage1-itemNDVIimage2
                                                band5Image1 = img.GetRasterBand(5)
                                                band5Image2 = image2.GetRasterBand(5)
                                                band5Image1asArray = band5Image1.ReadAsArray() 
                                                band5Image2asArray = band5Image2.ReadAsArray() 
                                                ratioB5=band5Image1asArray[row][col]/band5Image2asArray[row][col]

                                                #cleans memory
                                                del band5Image1
                                                del band5Image2
                                                del band5Image1asArray
                                                del band5Image2asArray
                                                print ("dNBR, RDNBR, NDVIdiff and ratioB5:",dNBR, RdNBR, NDVIdiff,ratioB5)

                                                #if dNBR equals exactly 0, it means that image 1 and image 2 were the same; stop and continue with next image
                                                if dNBR==0:
                                                    print("same image for image 1 and image2; initiating with another image for image 2")
                                                #if dNBR, NBR or NDVI difference values are under thresholds, stop and continue with next image
                                                elif dNBR<dNBRthreshold or RdNBR<RdNBRthreshold or NDVIdiff<NDVIdiffThreshold or ratioB5 <ratioB5Threshold:
                                                    print("dNBR or RdNBR or NDVIdiff under threshold; continue with next image for image 2")

                                                else:  
                                                    #open empty image and set new dNBR and RdNBR and date values in first, second and third band respectively. in ArrayStack, first number is number of band (first is zero) then row then column.
                                                    #if dNBR  or RdNBR values is above value already saved in the array or if current value is empty (nan), overwrite it; else, don't overwrite it
                                                    print ("current dNBR value for this cell in arrayStack: ",arrayStack[cntrForBand][row][col])
                                                    if (dNBR>arrayStack[cntrForBand][row][col] and RdNBR>arrayStack[cntrForBand+1][row][col] and NDVIdiff>arrayStack[cntrForBand+2][row][col] and ratioB5>arrayStack[cntrForBand+3][row][col]) or (math.isnan(arrayStack[cntrForBand][row][col])):
                                                        #keeps dNBR, RdNBR and date value in first, second and third of the three bands (hence cntrForBand for dNBR, cntrForBand+1 for RdNBR and cntrForBand+2 for Date)
                                                        arrayStack[cntrForBand][row][col]= dNBR
                                                        arrayStack[cntrForBand+1][row][col]= RdNBR
                                                        arrayStack[cntrForBand+2][row][col]= NDVIdiff
                                                        arrayStack[cntrForBand+3][row][col]= ratioB5
                                                        #keeps dates of first date and second date images
                                                        dateFin=int(img2Path[-15:-8])
                                                        dateIni=int(img1Path[-15:-8])
                                                        arrayStack[cntrForBand+4][row][col]= dateIni
                                                        arrayStack[cntrForBand+5][row][col]= dateFin
                                                        print ("arrayStack updated")
                                                        #turn switch on to skip 22 images (as forestry fire won't happen soon again)
                                                        switch1= True
                                                    else:                        
                                                        print ("dNBR value lower than value already in arrayStack; not changing value")
                                    #if one value of dNBR and RdNBR is above threshold during loops with image 1 and 2, then skip a year and continues with image 1 + 44
                                    #else, continue with image 1 + 7
                                    if switch1==True:
                                        next(islice(iterListImages, 44, 44), None)
                                        cntrForBand=cntrForBand+6
                              #         
                                    else:
                                        #optional: to simplify caculus (if no high dNBR and RdNBR values found, skips to image x+7)
                                        next(islice(iterListImages, 7, 7), None)
                    #closing script and saving output numpy array with indexes values and date whenever a burned area has been detected
                    print ("processing complete. Saving results to numpy array")
                    print (arrayStack)
                    time2 = time.clock()
                    np.save(path+"\\FinalOutput_"+str(dNBRthreshold)+"_"+str(RdNBRthreshold)+"_"+str(NDVIdiffThreshold)+"_"+str(ratioB5Threshold)+"_"+".csv", arrayStack)
                    print ("Process done in "+ str((time2-time1)/3600) + " hours")
                    print("file saved")
                              

                #multiprocessing parameters to define               
                if __name__ == '__main__':
                    #creates a list of all the subfolders (with rasters of one protected area per folder) in the folder which path must be defined here
                    listFolders= [ f.path for f in os.scandir("F:\\...\\INPUT_FOLDER") if f.is_dir() ]
                    print (listFolders, type(listFolders))
                    #get number of cores that are available for multiprocessing and set multiprocessing with this number of available cores
                    cpuCount = os.cpu_count() 
                    print ("number of core: ",cpuCount)
                    #initiates multiprocessing
                    for folder in listFolders:
                        p = multiprocessing.Process(target=proc, args=(folder,))
                        processes.append(p)
                        p.start()
                       
                                

