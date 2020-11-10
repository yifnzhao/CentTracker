
#@ File (label = "Input directory", style = "directory") input
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
			processFile(input, list[i]);
			row++;	
	}
}


function processFile(input, file) {

	    print("Processing: " + input + File.separator + file);
	    open(input + File.separator + file);	  
		ch = getNumber("Channels", 0);
		sl = getNumber("Slices", 0);
		fr = getNumber("frames", 0);
		run("Stack to Hyperstack...", "order=xyczt(default) channels=ch slices=sl frames=fr display=Color");
		//run("Channels Tool...");
		Stack.setDisplayMode("composite");
		//run("Brightness/Contrast...");
		Stack.setPosition(1,25,1);
		run("Enhance Contrast", "saturated=0.35");
		Stack.setPosition(2,25,1);
		run("Enhance Contrast", "saturated=0.35");
		// crop the movie to crop out the borders resulting for registration
		waitForUser("draw a rectangle around your ROI","Done");
		run("Crop");
		run("Save");
		run("TrackMate");
		waitForUser("generate .xml","Done");
		run("Close All");
		run("Collect Garbage");
}
