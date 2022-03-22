
// Set [Basic Paragraph] Paragraphy style to Underline = true
doc = app.activeDocument;
basicParaStyle = doc.paragraphStyles.item('[Basic Paragraph]');
basicParaStyle.underline = true;

// Set New chapter style to be visible
newChapStyle = doc.paragraphStyles.item('New Chapter Tag');
newChapStyle.pointSize = 18;
newChapStyle.horizontalScale = 100;
newChapStyle.fillColor = doc.swatches.item('Black');

// Set Tag Text to visible
var tagStyle = doc.characterStyles.item('Tag Text');
var sourceTagStyle = doc.characterStyles.item('Tag Text/Visible');
tagStyle.basedOn = sourceTagStyle;

// screen mode normal
doc.layoutWindows[0].screenMode = ScreenModeOptions.PREVIEW_OFF