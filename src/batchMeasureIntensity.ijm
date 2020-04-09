getPixelSize(punit, pixelw, pixelh) 			// gets the pixel dimensions
getVoxelSize(voxelw voxelh, depth, vunit);
open("/Users/yifan/Desktop/cpv2/0716/2018-07-16_GSC_L4_L4440_RNAi_T0_unlab.xml_spots_parsed.csv");
rowNumber = getValue("results.count");
coordsArray = newArray();
for (i = 0; i < rowNumber; i++){
	x = getResult("POSITION_X", i) ;
	x = x/pixelw;
	y = getResult("POSITION_Y", i) ;
	y = y/pixelh;
	z = getResult("POSITION_Z", i);
	z = z/depth + 1;
	frame = getResult("FRAME", i);
	frame = frame + 1; //tm xml count from 0
	id= getResult("ID", i);
	singleCoords = newArray(x, y, z, frame, id); 
	for (j = 0; j < 5; j++){
		coordsArray = Array.concat(coordsArray,singleCoords[j]);
	}
}
run("Set Measurements...", "center integrated decimal=10");
radius = 5;
for (i = 0; i < rowNumber; i++){
	x = coordsArray[5*i];
	y = coordsArray[5*i+1];
	z = coordsArray[5*i+2];
	frame = coordsArray[5*i+3];
//	id = coordsArray[5*i+4];
	setSlice(z);
	Stack.setFrame(frame);
	makeOval(x-radius, y-radius, radius*2, radius*2);
	run("Measure");
}
saveAs("Results", "/Users/yifan/Desktop/cpv2/0716/2018-07-16_GSC_L4_L4440_RNAi_T0_unlab_IntensityMeasurements.csv");