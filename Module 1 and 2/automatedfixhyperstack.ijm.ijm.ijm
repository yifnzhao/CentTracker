#@ File (label = "Original movies directory", style = "directory") input
#@ File (label = "Registered movies directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix



processFolder(input);
	
// find files with correct suffix
function processFolder(input) {
	list = getFileList(input);
	list = Array.sort(list);
	row=0;
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, output, list[i]);
			row++;	
	}
}


function processFile(input, output, file) {
		discardReg=substring(file, 0, 2);
	    if(discardReg!="r_"){
	    print("Processing: " + file);
	    open(input + File.separator + file);
		getVoxelSize(xy, Pxheight, z, unit);
		Stack.getDimensions(wi, he, ch, sl, fr);
		Interval=Stack.getFrameInterval();
		run("Close All");
		open(input+File.separator+"r_"+file);
		setVoxelSize(xy, Pxheight, z, unit);
		run("Stack to Hyperstack...", "order=xyczt(default) channels=ch slices=sl frames=fr display=Color");
		Stack.setFrameInterval(Interval);
		//run("Channels Tool...");
		if(ch>1){
		Stack.setDisplayMode("composite");
		}
		//run("Brightness/Contrast...");
		Stack.setPosition(1,25,1);
		run("Enhance Contrast", "saturated=0.35");
		Stack.setPosition(2,25,1);
		run("Enhance Contrast", "saturated=0.35");
		// crop the movie to crop out the borders resulting for registration
		setTool("rectangle");
		waitForUser("draw a rectangle around your ROI");
		run("Crop");
		run("Save");
		run("TrackMate");
		waitForUser("generate a .xml using Trackmate");
		run("Close All");
		run("Collect Garbage");
	    }
}