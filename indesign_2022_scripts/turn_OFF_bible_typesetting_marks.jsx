
var doc = app.activeDocument;

// Set [Basic Paragraph] Paragraphy style to Underline = false
var basicParaStyle = doc.paragraphStyles.item('[Basic Paragraph]');
basicParaStyle.underline = false

// Set New chapter style to be hidden
var newChapStyle = doc.paragraphStyles.item('New Chapter Tag');
newChapStyle.pointSize = 0.1;
newChapStyle.horizontalScale = 1;
newChapStyle.fillColor = doc.swatches.item('None');

// Set Tag Text to Hidden
var tagStyle = doc.characterStyles.item('Tag Text');
var sourceTagStyle = doc.characterStyles.item('Tag Text/Hidden');
tagStyle.basedOn = sourceTagStyle;

// Screen mode preview
doc.layoutWindows[0].screenMode = ScreenModeOptions.PREVIEW_TO_PAGE

