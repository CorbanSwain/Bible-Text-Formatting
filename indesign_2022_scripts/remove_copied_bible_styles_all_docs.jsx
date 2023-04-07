main();

function main() {
    var allDocs = app.documents.everyItem();
    
    allDocs.paragraphStyles.item("Normal_rtf_1").remove("Normal");
    
    var removeParaArr = ["heading 2",  "heading 1", "footnote text"];
    for (var i = 0; i < removeParaArr.length; ++i) {
        allDocs.paragraphStyles.item(removeParaArr[i]).remove();
    }
    
    var removeCharArr = ["footnote reference", "Verse"]
    for (var i = 0; i < removeCharArr.length; ++i) {
        allDocs.characterStyles.item(removeCharArr[i]).remove();
    }

 }