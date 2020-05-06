from ij import IJ, ImagePlus, ImageStack, WindowManager
import fiji.plugin.trackmate.Settings as Settings
import fiji.plugin.trackmate.Model as Model
import fiji.plugin.trackmate.SelectionModel as SelectionModel
import fiji.plugin.trackmate.TrackMate as TrackMate
import fiji.plugin.trackmate.Logger as Logger
import fiji.plugin.trackmate.detection.DetectorKeys as DetectorKeys
import fiji.plugin.trackmate.detection.LogDetectorFactory as LogDetectorFactory
import fiji.plugin.trackmate.tracking.sparselap.SimpleSparseLAPTrackerFactory as SimpleSparseLAPTrackerFactory
import fiji.plugin.trackmate.tracking.LAPUtils as LAPUtils
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
import fiji.plugin.trackmate.features.FeatureAnalyzer as FeatureAnalyzer
import fiji.plugin.trackmate.features.spot.SpotContrastAndSNRAnalyzerFactory as SpotContrastAndSNRAnalyzerFactory
import fiji.plugin.trackmate.action.ExportStatsToIJAction as ExportStatsToIJAction
import fiji.plugin.trackmate.io.TmXmlReader as TmXmlReader
import fiji.plugin.trackmate.action.ExportTracksToXML as ExportTracksToXML
import fiji.plugin.trackmate.io.TmXmlWriter as TmXmlWriter
import fiji.plugin.trackmate.features.ModelFeatureUpdater as ModelFeatureUpdater
import fiji.plugin.trackmate.features.SpotFeatureCalculator as SpotFeatureCalculator
import fiji.plugin.trackmate.features.spot.SpotContrastAndSNRAnalyzer as SpotContrastAndSNRAnalyzer
import fiji.plugin.trackmate.features.spot.SpotIntensityAnalyzerFactory as SpotIntensityAnalyzerFactory
import fiji.plugin.trackmate.features.track.TrackSpeedStatisticsAnalyzer as TrackSpeedStatisticsAnalyzer
import fiji.plugin.trackmate.features.track.TrackDurationAnalyzer as TrackDurationAnalyzer
import fiji.plugin.trackmate.util.TMUtils as TMUtils
import sys
import java.io.File as File
import fiji.plugin.trackmate.io.TmXmlWriter as TmXmlWriter
from fiji.plugin.trackmate.providers import SpotAnalyzerProvider
from fiji.plugin.trackmate.providers import EdgeAnalyzerProvider
from fiji.plugin.trackmate.providers import TrackAnalyzerProvider

# Get currently selected image
#imp = WindowManager.getCurrentImage()
#imp = IJ.openImage('http://fiji.sc/samples/FakeTracks.tif')
path = "/Users/yifan/Dropbox/ZYF/dev/GitHub/automated-centrosome-pairing/data/2018-01-17_GSC_L4_L4440_RNAi/"
imp = IJ.openImage(path+'u_germline.tif')
#imp.show()
   
   
#----------------------------
# Instantiate model object
#----------------------------

model = Model()
   
# Send all messages to ImageJ log window.
model.setLogger(Logger.IJ_LOGGER)   

#------------------------
# Prepare settings object
#------------------------
      
settings = Settings()
settings.setFrom(imp)
      
# Configure detector - We use the Strings for the keys
settings.detectorFactory = LogDetectorFactory()
settings.detectorSettings = { 
    DetectorKeys.KEY_DO_SUBPIXEL_LOCALIZATION : True,
    DetectorKeys.KEY_RADIUS : 1.5,
    DetectorKeys.KEY_THRESHOLD : 5.,
    DetectorKeys.KEY_DO_MEDIAN_FILTERING : False,
}  
#       
## Configure tracker - We want to allow merges and fusions
settings.trackerFactory = SimpleSparseLAPTrackerFactory()
settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
settings.trackerSettings['LINKING_MAX_DISTANCE'] = 5.0
settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE']=5.0
settings.trackerSettings['MAX_FRAME_GAP']= 3
settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = True
settings.trackerSettings['ALLOW_TRACK_MERGING'] = True
   
# Add analyzers
# Compute edge properties, following https://github.com/fiji/TrackMate/issues/120
settings.clearSpotAnalyzerFactories()
spotAnalyzerProvider = SpotAnalyzerProvider()
spotAnalyzerKeys = spotAnalyzerProvider.getKeys()
for key in spotAnalyzerKeys:
    spotFeatureAnalyzer = spotAnalyzerProvider.getFactory(key)
    settings.addSpotAnalyzerFactory(spotFeatureAnalyzer)

settings.clearEdgeAnalyzers()
edgeAnalyzerProvider = EdgeAnalyzerProvider()
edgeAnalyzerKeys = edgeAnalyzerProvider.getKeys()
for key in edgeAnalyzerKeys:
    edgeAnalyzer = edgeAnalyzerProvider.getFactory(key)
    settings.addEdgeAnalyzer(edgeAnalyzer)

settings.clearTrackAnalyzers();
trackAnalyzerProvider = TrackAnalyzerProvider()
trackAnalyzerKeys = trackAnalyzerProvider.getKeys()
for key in trackAnalyzerKeys:
    trackAnalyzer = trackAnalyzerProvider.getFactory(key)
    settings.addTrackAnalyzer(trackAnalyzer) 
#settings.addTrackAnalyzer(TrackDurationAnalyzer())
#settings.addTrackAnalyzer(TrackSpeedStatisticsAnalyzer())
#settings.addSpotAnalyzerFactory(SpotIntensityAnalyzerFactory())
#settings.addSpotAnalyzerFactory(SpotContrastAndSNRAnalyzerFactory())

print(str(settings))

#-------------------
# Instantiate TrackMate
#-------------------
   
trackmate = TrackMate(model, settings)
      
#--------
# Process
#--------
   
ok = trackmate.checkInput()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))
   
ok = trackmate.process()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))
   
      
#----------------
# Display results
#----------------
model.getLogger().log('Found ' + str(model.getTrackModel().nTracks(True)) + ' tracks.')
selectionModel = SelectionModel(model)
displayer =  HyperStackDisplayer(model, selectionModel, imp)
displayer.render()
displayer.refresh()

outputFolder= "/Users/yifan/Dropbox/ZYF/dev/GitHub/automated-centrosome-pairing/data/"
outFile = File(outputFolder, "exportTracks.xml")
ExportTracksToXML.export(model, settings, outFile)

outFile = File(outputFolder, "exportModel.xml")
writer = TmXmlWriter(outFile)
writer.appendModel(model)
writer.appendSettings(settings)
writer.writeToFile()
print "All Done!"

# Echo results with the logger we set at start:
model.getLogger().log(str(model))


for id in model.getTrackModel().trackIDs(True):
  
    track = model.getTrackModel().trackSpots(id)
    for spot in track:
        sid = spot.ID()
        # Fetch spot features directly from spot. 
        x=spot.getFeature('POSITION_X')
        y=spot.getFeature('POSITION_Y')
        t=spot.getFeature('FRAME')
        q=spot.getFeature('QUALITY')
        snr=spot.getFeature('SNR') 
        mean=spot.getFeature('MEAN_INTENSITY')
        model.getLogger().log('\tspot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q) + ', snr='+str(snr) + ', mean = ' + str(mean))
