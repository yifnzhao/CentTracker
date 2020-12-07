#@ File (label = "Original movies directory", style = "directory") input
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

	    print("Processing: " + file);
	    open(input + File.separator + file);
	    csvdir= input + File.separator +"/roi/";
		File.makeDirectory(csvdir);
		Stack.getDimensions(wi, he, ch, sl, fr);
	    if (ch>1){
	    run("Split Channels");
	    }
	    waitForUser("click on centrosomes channel then click on OK");
		run("Z Project...", "projection=[Max Intensity] all");
		//run("Brightness/Contrast...");
		run("Enhance Contrast", "saturated=0.35");
	
		run("ROI Manager...");
		setTool("line");
		b=1;
		waitForUser("click when done tracking");		
		a=getBoolean("track an additional cell ?");
		roiManager("List");
		saveAs("Results", csvdir+File.separator+b+".csv");
		run("Close");
		roiManager("Delete");
		while(a==1){
			b=b+1;
			waitForUser("click when done tracking");	
			a=getBoolean("track an additional cell ?");
			roiManager("List");
			saveAs("Results", csvdir+File.separator+b+".csv");
			run("Close");
			roiManager("Delete");
			roiManager("Delete");
			}
		selectWindow("ROI Manager");
     		run("Close");
		run("Close All");
		run("Collect Garbage");
}
