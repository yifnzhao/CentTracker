

#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix


processFolder(input);
saveAs("Results", output + "True" +".csv");	
	
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

	    print("Processing: " + input + File.separator + file);
	    open(input + File.separator + file);
	    run("Split Channels");
	    waitForUser("click on centrosomes channel then click on OK");
		run("Z Project...", "projection=[Max Intensity] all");
		//run("Brightness/Contrast...");
		run("Enhance Contrast", "saturated=0.35");
		run("ROI Manager...");
		//setTool("line");
		waitForUser("generate CSVs then click on OK");
		run("Close");
		run("Close");
		run("Close");
		run("Collect Garbage");
}
