
#@ File (label = "cropped tiffs", style = "directory") input
#@ File (label = "Original movies directory", style = "directory") output
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
		print(i);
		if (i==0){
        			run("Clear Results");
        	       	
        	}
        	
        
	    open(input + File.separator + file);
		run("In [+]");
		run("In [+]");
		run("In [+]");
		run("In [+]");
		run("Grays");
		run("Enhance Contrast", "saturated=0.35");
		run("Enhance Contrast", "saturated=0.35");
		run("Enhance Contrast", "saturated=0.35");
		doCommand("Start Animation [\\]");
		answer=getBoolean("Is it a true pair");
		close();
		requires("1.47o");
		requires("1.52v");
		a=indexOf(File.getNameWithoutExtension(file), "Cell_");
		setResult("Cell",row, substring(File.getNameWithoutExtension(file), a+5));
		setResult("True_pairs",row, answer);
		updateResults();
		saveAs("Results", output+File.separator+substring(File.getNameWithoutExtension(file), 2,a-1)+ File.separator+"True" +".csv");	
		
}
